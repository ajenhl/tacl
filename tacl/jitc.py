import csv
import io
import json
import logging
import math
import os
import shutil

from jinja2 import Environment, PackageLoader
import pandas as pd
from pkg_resources import resource_filename, resource_listdir

from . import constants
from .results import Results
from .statistics_report import StatisticsReport


class JITCProcessor:

    """Generate statistics to list works from one corpus (referred to
    below as "Maybe" and defined in a catalogue file) in order of
    similarity to each work in that corpus. Takes into account a
    second corpus of works (referred to below as "No" and defined in a
    catalogue file) that are similar to those in the first, but not in
    the way(s) that are the subject of the investigation.

    Given the two corpora, Maybe and No, the script performs the
    following actions:

    1. For each work Y in Maybe:
      1. Run an intersection between Y and No.
      2. For each work M in Maybe (excluding Y):
        1. Run an intersect between Y and M.
        2. Drop Y results.
        3. Run a supplied diff between results from [1.2.2] and
           results from [1.1].
        4. Get number of tokens in M.
      3. Rank and list works in Maybe in descending order of the
         ratio, from [1.2.3], of matching tokens (n-gram size x count)
         to total tokens [1.2.4].
    2. Concatenate all results from [1.2.3] files.

    Note that in the above, when a work is treated as Y, its different
    witnesses are not treated separately. The statistics derived from
    queries including it are those that treat all of its witnesses
    together; eg, if two n-grams in a witness of M are found only in
    two different witnesses of Y, they will both be counted as shared.

    """

    def __init__(self, store, corpus, catalogue, maybe_label, tokenizer,
                 output_dir):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._maybe_label = maybe_label
        self._maybe_works = [work for work, label in catalogue.items()
                             if label == maybe_label]
        self._no_works = [work for work, label in catalogue.items()
                          if label != maybe_label]
        self._no_label = catalogue[self._no_works[0]]
        self._output_dir = output_dir
        self._output_data_dir = os.path.join(self._output_dir, 'data')
        self._store = store
        self._tokenizer = tokenizer
        self._stats = {}
        self._ym_intersects_dir = os.path.join(self._output_data_dir,
                                               'ym_intersects')

    def _copy_static_assets(self, output_dir):
        for asset in resource_listdir(__name__, 'assets/jitc'):
            filename = resource_filename(__name__, 'assets/jitc/{}'.format(
                asset))
            shutil.copy2(filename, output_dir)

    def _create_breakdown_chart(self, data, work, output_dir):
        # Create a stacked bar chart that shows the percentage of the
        # content consisting of shared tokens that aren't in the no
        # corpus, shared tokens that are also in the no corpus, and
        # unshared tokens.
        chart_data = data.loc[work].sort_values(by='shared', ascending=False)[
            ['shared', 'unique', 'common']]
        csv_path = os.path.join(output_dir, 'breakdown_{}.csv'.format(
            work))
        chart_data.to_csv(csv_path)

    def _create_chord_chart(self, data, output_dir):
        matrix = []
        chord_data = data.unstack('main_work')['shared']
        for index, row_data in chord_data.fillna(value=0).iterrows():
            matrix.append([value / 100 for value in row_data])
        colours = generate_colours(len(self._maybe_works))
        colour_works = [{'work': work, 'colour': colour} for work, colour
                        in zip(chord_data, colours)]
        json_data = json.dumps({'works': colour_works, 'matrix': matrix})
        with open(os.path.join(output_dir, 'chord_data.js'), 'w') as fh:
            fh.write('var chordData = {}'.format(json_data))

    def _create_matrix_chart(self, data, output_dir):
        nodes = [{'work': work, 'group': 1} for work in self._maybe_works]
        weights = data.stack().unstack('related_work').max()
        seen = []
        links = []
        for (source, target), weight in weights.iteritems():
            if target not in seen and target != source:
                seen.append(source)
                links.append({'source': self._maybe_works.index(source),
                              'target': self._maybe_works.index(target),
                              'value': weight})
        json_data = json.dumps({'nodes': nodes, 'links': links})
        with open(os.path.join(output_dir, 'matrix_data.js'), 'w') as fh:
            fh.write('var matrixData = {}'.format(json_data))

    def _create_related_chart(self, data, work, output_dir):
        # Create a chart that has two bars per work on x-axis: one for
        # the percentage of that work that overlaps with the base
        # work, and one for the percentage of the base work that
        # overlaps with that work. A tooltip showing the values per
        # witness would be good.
        chart_data = data[work].dropna().sort_values(by='shared_related_work',
                                                     ascending=False)
        csv_path = os.path.join(output_dir, 'related_{}.csv'.format(work))
        chart_data.to_csv(csv_path)

    def _drop_no_label_results(self, results, fh):
        """Writes `results` to `fh` minus those results associated with the
        'no' label.

        :param results: results to be manipulated
        :type results: file-like object
        :param fh: output destination
        :type fh: file-like object

        """
        results.seek(0)
        results = Results(results, self._tokenizer)
        results.remove_label(self._no_label)
        results.csv(fh)

    def _generate_statistics(self, out_path, results_path):
        """Write a statistics report for `results_path` to `out_path`."""
        if not os.path.exists(out_path):
            report = StatisticsReport(self._corpus, self._tokenizer,
                                      results_path)
            report.generate_statistics()
            with open(out_path, mode='w', encoding='utf-8', newline='') as fh:
                report.csv(fh)

    def _get_reversed_data(self, data):
        reverse_data = data.unstack('main_work')['shared']
        tuples = list(zip(['shared_related_work'] * len(reverse_data.columns),
                          reverse_data.columns))
        reverse_data.columns = pd.MultiIndex.from_tuples(
            tuples, names=['work', 'main_work'])
        for work in reverse_data['shared_related_work'].columns:
            reverse_data['shared_base_work', work] = reverse_data[
                'shared_related_work'].loc[work].tolist()
        return reverse_data.swaplevel('work', 'main_work', axis=1)

    def _process_maybe_work(self, yes_work, maybe_work, work_dir,
                            yn_results_path):
        if maybe_work == yes_work:
            return
        self._logger.info(
            'Processing "maybe" work {} against "yes" work {}.'.format(
                maybe_work, yes_work))
        for siglum in self._corpus.get_sigla(maybe_work):
            witness = (maybe_work, siglum)
            self._stats[yes_work]['common'][witness] = 0
            self._stats[yes_work]['shared'][witness] = 0
            self._stats[yes_work]['unique'][witness] = 100
        works = [yes_work, maybe_work]
        works.sort()
        ym_results_path = os.path.join(
            self._ym_intersects_dir, '{}_intersect_{}.csv'.format(*works))
        catalogue = {yes_work: self._no_label,
                     maybe_work: self._maybe_label}
        self._run_query(ym_results_path, self._store.intersection, [catalogue],
                        False)
        intersect_stats_path = os.path.join(
            work_dir, 'stats_intersect_{}.csv'.format(maybe_work))
        self._generate_statistics(intersect_stats_path, ym_results_path)
        with open(intersect_stats_path, encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row[constants.WORK_FIELDNAME] == maybe_work:
                    witness = (maybe_work, row[constants.SIGLUM_FIELDNAME])
                    ratio = float(row[constants.PERCENTAGE_FIELDNAME])
                    self._stats[yes_work]['common'][witness] = ratio
                    self._stats[yes_work]['unique'][witness] -= ratio
        distinct_results_path = os.path.join(
            work_dir, 'distinct_{}.csv'.format(maybe_work))
        results = [yn_results_path, ym_results_path]
        labels = [self._no_label, self._maybe_label]
        self._run_query(distinct_results_path, self._store.diff_supplied,
                        [results, labels])
        diff_stats_path = os.path.join(work_dir,
                                       'stats_diff_{}.csv'.format(maybe_work))
        self._generate_statistics(diff_stats_path, distinct_results_path)
        with open(diff_stats_path, encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row[constants.WORK_FIELDNAME] == maybe_work:
                    witness = (maybe_work, row[constants.SIGLUM_FIELDNAME])
                    ratio = float(row[constants.PERCENTAGE_FIELDNAME])
                    self._stats[yes_work]['shared'][witness] = ratio
                    self._stats[yes_work]['common'][witness] -= ratio

    def _process_yes_work(self, yes_work, no_catalogue, output_dir):
        self._logger.info('Processing "maybe" work {} as "yes".'.format(
            yes_work))
        self._stats[yes_work] = {'common': {}, 'shared': {}, 'unique': {}}
        yes_work_dir = os.path.join(output_dir, yes_work)
        os.makedirs(yes_work_dir, exist_ok=True)
        results_path = os.path.join(yes_work_dir, 'intersect_with_no.csv')
        self._run_query(results_path, self._store.intersection, [no_catalogue])
        for maybe_work in self._maybe_works:
            self._process_maybe_work(yes_work, maybe_work, yes_work_dir,
                                     results_path)

    def process(self):
        no_catalogue = {work: self._no_label for work in self._no_works}
        data = {}
        os.makedirs(self._ym_intersects_dir, exist_ok=True)
        for yes_work in self._maybe_works:
            no_catalogue[yes_work] = self._maybe_label
            self._process_yes_work(yes_work, no_catalogue,
                                   self._output_data_dir)
            no_catalogue.pop(yes_work)
            for scope in ('shared', 'common', 'unique'):
                work_data = self._stats[yes_work][scope]
                # QAZ: Check that keys() and values() will always
                # return items in the same order when called
                # consecutively like this.
                index = pd.MultiIndex.from_tuples(
                    list(work_data.keys()), names=['related_work', 'siglum'])
                data[(yes_work, scope)] = pd.Series(list(work_data.values()),
                                                    index=index)
        full_data = pd.DataFrame(data)
        full_data.columns.names = ['main_work', 'scope']
        full_data = full_data.stack('main_work').swaplevel(
            'main_work', 'siglum').swaplevel('related_work', 'main_work')
        grouped = full_data.groupby(level=['main_work', 'related_work'],
                                    axis=0, group_keys=False)
        max_data = grouped.apply(lambda x: x.loc[x['shared'].idxmax()])
        reverse_data = self._get_reversed_data(max_data)
        report_data_dir = os.path.join(self._output_dir, 'report_data')
        os.makedirs(report_data_dir, exist_ok=True)
        report_assets_dir = os.path.join(self._output_dir, 'report_assets')
        os.makedirs(report_assets_dir, exist_ok=True)
        # Matrix chart.
        self._create_matrix_chart(reverse_data, report_data_dir)
        # Chord chart.
        self._create_chord_chart(max_data, report_data_dir)
        tables = []
        works = [(index, work) for index, work in enumerate(self._maybe_works)]
        export_data = full_data.unstack('main_work').swaplevel(
            'main_work', 'scope', axis=1)
        export_data.index.names = ['related work', 'siglum']
        for index, work in enumerate(self._maybe_works):
            self._create_breakdown_chart(max_data, work, report_data_dir)
            self._create_related_chart(reverse_data, work, report_data_dir)
            tables.append(export_data[work].dropna().to_html())
        loader = PackageLoader('tacl', 'assets/templates')
        env = Environment(loader=loader)
        template = env.get_template('jitc.html')
        report = template.render(
            {'works': works, 'sep': os.sep, 'tables': tables,
             'other_works': self._no_works})
        with open(os.path.join(self._output_dir, 'report.html'), 'w') as fh:
            fh.write(report)
        self._copy_static_assets(report_assets_dir)

    def _run_query(self, path, query, query_args, drop_no=True):
        if os.path.exists(path):
            return
        output_results = io.StringIO(newline='')
        query(*query_args, output_fh=output_results)
        with open(path, mode='w', encoding='utf-8', newline='') as fh:
            if drop_no:
                self._drop_no_label_results(output_results, fh)
            else:
                fh.write(output_results.getvalue())


def rgb_colour(h, f):
    """Convert a colour specified by h-value and f-value to an RGB string."""
    v = 1
    p = 0
    if h == 0:
        colour = v, f, p
    elif h == 1:
        colour = 1 - f, v, p
    elif h == 2:
        colour = p, v, f
    elif h == 3:
        colour = p, 1 - f, v
    elif h == 4:
        colour = f, p, v
    elif h == 5:
        colour = v, p, 1 - f
    return 'rgb({}, {}, {})'.format(*[round(value * 255) for value in colour])


def generate_colours(n):
    """Return a list of distinct colours, each of which is represented as
    an RGB string suitable for use in CSS."""
    hues = [360 / n * i for i in range(n)]
    hs = (math.floor(hue / 60) % 6 for hue in hues)
    fs = (hue / 60 - math.floor(hue / 60) for hue in hues)
    return [rgb_colour(h, f) for h, f in zip(hs, fs)]
