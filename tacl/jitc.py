import csv
import io
import json
import logging
import os

import pandas as pd

from . import constants
from .colour import generate_colours
from .report import Report
from .results import Results
from .statistics_report import StatisticsReport


# Data headers.
BASE_WORK = 'base_work'
COMMON = 'common'  # Text in common among yes, maybe and no.
RELATED_WORK = 'related_work'
SCOPE = 'scope'
SHARED = 'shared'  # Text shared between yes and maybe.
SHARED_BASE_WORK = 'shared_base_work'
SHARED_RELATED_WORK = 'shared_related_work'
SIGLUM = 'siglum'
UNIQUE = 'unique'  # Text unique to yes.
WORK = 'work'


class JitCReport(Report):

    """Generate statistics to list works from one corpus (referred to
    below as "Maybe" and defined in a catalogue file) in order of
    similarity to each work in that corpus. Takes into account a
    second corpus of works (referred to below as "No" and defined in
    the same catalogue file) that are similar to those in the first,
    but not in the way(s) that are the subject of the investigation.

    Given the two corpora, Maybe and No, the script performs the
    following actions:

    1. For each work Y in Maybe:

      1. Run an intersection between Y and No.
      2. For each work M in Maybe (excluding Y):

        1. Run an intersect between Y and M.
        2. Run a supplied diff between results from [1.2.1] and
           results from [1.1].
        3. Get number of tokens in M.

      3. Rank and list works in Maybe in descending order of the
         ratio, from [1.2.2], of matching tokens (n-gram size x count)
         to total tokens [1.2.3].

    2. Concatenate all results from [1.2.2] and present them in an
       HTML report.

    Note that in the above, when a work is treated as Y, its witnesses
    are not treated separately. The statistics derived from queries
    including it are those that treat all of its witnesses together;
    eg, if two n-grams in a witness of M are found only in two
    different witnesses of Y, they will both be counted as shared.

    """

    _report_name = 'jitc'

    def __init__(self, store, corpus, tokenizer):
        self._logger = logging.getLogger(__name__)
        self._corpus = corpus
        self._tokenizer = tokenizer
        self._store = store

    def _create_breakdown_chart(self, data, work, output_dir):
        """Generates and writes to a file in `output_dir` the data used to
        display a stacked bar chart.

        The generated data gives the percentages of the text of the
        work (across all witnesses) that are in common with all other
        works, shared with each "maybe" work, and unique.

        :param data: data to derive the chart data from
        :type data: `pandas.DataFrame`
        :param work: work to show related work data for
        :type work: `str`
        :param output_dir: directory to output data file to
        :type output_dir: `str`

        """
        chart_data = data.loc[work].sort_values(by=SHARED, ascending=False)[
            [SHARED, UNIQUE, COMMON]]
        csv_path = os.path.join(output_dir, 'breakdown_{}.csv'.format(
            work))
        chart_data.to_csv(csv_path)

    def _create_chord_chart(self, data, works, output_dir):
        """Generates and writes to a file in `output_dir` the data used to
        display a chord chart.

        :param data: data to derive the chord data from
        :type data: `pandas.DataFrame`
        :param works: works to display
        :type works: `list`
        :param output_dir: directory to output data file to
        :type output_dir: `str`

        """
        matrix = []
        chord_data = data.unstack(BASE_WORK)[SHARED]
        for index, row_data in chord_data.fillna(value=0).iterrows():
            matrix.append([value / 100 for value in row_data])
        colours = generate_colours(len(works))
        colour_works = [{'work': work, 'colour': colour} for work, colour
                        in zip(chord_data, colours)]
        json_data = json.dumps({'works': colour_works, 'matrix': matrix})
        with open(os.path.join(output_dir, 'chord_data.js'), 'w') as fh:
            fh.write('var chordData = {}'.format(json_data))

    def _create_matrix_chart(self, data, works, output_dir):
        """Generates and writes to a file in `output_dir` the data used to
        display a matrix chart.

        :param data: data to derive the matrix data from
        :type data: `pandas.DataFrame`
        :param works: works to display
        :type works: `list`
        :param output_dir: directory to output data file to
        :type output_dir: `str`

        """
        nodes = [{'work': work, 'group': 1} for work in works]
        weights = data.stack().unstack(RELATED_WORK).max()
        seen = []
        links = []
        for (source, target), weight in weights.iteritems():
            if target not in seen and target != source:
                seen.append(source)
                links.append({'source': works.index(source),
                              'target': works.index(target),
                              'value': weight})
        json_data = json.dumps({'nodes': nodes, 'links': links})
        with open(os.path.join(output_dir, 'matrix_data.js'), 'w') as fh:
            fh.write('var matrixData = {}'.format(json_data))

    def _create_related_chart(self, data, work, output_dir):
        """Generates and writes to a file in `output_dir` the data used to
        display a grouped bar chart.

        This data gives, for each "maybe" work, the percentage of it
        that is shared with `work`, and the percentage of `work` that
        is shared with the "maybe" work.

        :param data: data to derive the chart data from
        :type data: `pandas.DataFrame`
        :param works: work to show related data for
        :type works: `str`
        :param output_dir: directory to output data file to
        :type output_dir: `str`

        """
        chart_data = data[work].dropna().sort_values(by=SHARED_RELATED_WORK,
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

    def generate(self, output_dir, catalogue, maybe_label):
        maybe_works = [work for work, label in catalogue.items()
                       if label == maybe_label]
        maybe_works.sort()
        no_works = [work for work, label in catalogue.items()
                    if label != maybe_label]
        no_works.sort()
        self._maybe_label = maybe_label
        self._no_label = catalogue[no_works[0]]
        data = self._process_works(maybe_works, no_works, output_dir)
        grouped = data.groupby(level=[BASE_WORK, RELATED_WORK],
                               axis=0, group_keys=False)
        max_data = grouped.apply(lambda x: x.loc[x[SHARED].idxmax()])
        reverse_data = self._get_reversed_data(max_data)
        report_data_dir = os.path.join(output_dir, 'report_data')
        os.makedirs(report_data_dir, exist_ok=True)
        report_assets_dir = os.path.join(output_dir, 'report_assets')
        os.makedirs(report_assets_dir, exist_ok=True)
        # Matrix chart.
        self._create_matrix_chart(reverse_data, maybe_works, report_data_dir)
        # Chord chart.
        self._create_chord_chart(max_data, maybe_works, report_data_dir)
        tables = []
        works = [(i, work) for i, work in enumerate(maybe_works)]
        export_data = data.unstack(BASE_WORK).swaplevel(
            BASE_WORK, SCOPE, axis=1)
        export_data.index.names = [RELATED_WORK, SIGLUM]
        for index, work in enumerate(maybe_works):
            self._create_breakdown_chart(max_data, work, report_data_dir)
            self._create_related_chart(reverse_data, work, report_data_dir)
            tables.append(export_data[work].dropna().to_html())
        context = {'other_works': no_works, 'sep': os.sep,
                   'tables': tables, 'works': works}
        self._write(context, output_dir, 'report.html', report_assets_dir)

    def _generate_statistics(self, out_path, results_path):
        """Writes a statistics report for the results at `results_path` to
        `out_path`.

        Reuses an existing statistics report if one exists at
        `out_path`.

        :param out_path: path to output statistics report to
        :type out_path: `str`
        :param results_path: path of results to generate statistics for
        :type results_path: `str`

        """
        if not os.path.exists(out_path):
            report = StatisticsReport(self._corpus, self._tokenizer,
                                      results_path)
            report.generate_statistics()
            with open(out_path, mode='w', encoding='utf-8', newline='') as fh:
                report.csv(fh)

    def _get_reversed_data(self, data):
        reverse_data = data.unstack(BASE_WORK)[SHARED]
        tuples = list(zip([SHARED_RELATED_WORK] * len(reverse_data.columns),
                          reverse_data.columns))
        reverse_data.columns = pd.MultiIndex.from_tuples(
            tuples, names=[WORK, BASE_WORK])
        for work in reverse_data[SHARED_RELATED_WORK].columns:
            reverse_data[SHARED_BASE_WORK, work] = reverse_data[
                SHARED_RELATED_WORK].loc[work].tolist()
        return reverse_data.swaplevel(WORK, BASE_WORK, axis=1)

    def _process_diff(self, yes_work, maybe_work, work_dir, ym_results_path,
                      yn_results_path, stats):
        """Returns statistics on the difference between the intersection of
        `yes_work` and `maybe_work` and the intersection of `yes_work`
        and "no" works.

        :param yes_work: name of work for which stats are collected
        :type yes_work: `str`
        :param maybe_work: name of work being compared with `yes_work`
        :type maybe_work: `str`
        :param work_dir: directory where generated files are saved
        :type work_dir: `str`
        :param ym_results_path: path to results intersecting
                                `yes_work` with `maybe_work`
        :type yn_results_path: `str`
        :param yn_results_path: path to results intersecting
                                `yes_work` with "no" works
        :type yn_results_path: `str`
        :param stats: data structure to hold the statistical data
        :type stats: `dict`
        :rtype: `dict`

        """
        distinct_results_path = os.path.join(
            work_dir, 'distinct_{}.csv'.format(maybe_work))
        results = [yn_results_path, ym_results_path]
        labels = [self._no_label, self._maybe_label]
        self._run_query(distinct_results_path, self._store.diff_supplied,
                        [results, labels, self._tokenizer])
        return self._update_stats('diff', work_dir, distinct_results_path,
                                  yes_work, maybe_work, stats, SHARED, COMMON)

    def _process_intersection(self, yes_work, maybe_work, work_dir,
                              ym_results_path, stats):
        """Returns statistics on the intersection between `yes_work` and
        `maybe_work`.

        :param yes_work: name of work for which stats are collected
        :type yes_work: `str`
        :param maybe_work: name of work being compared with `yes_work`
        :type maybe_work: `str`
        :param work_dir: directory where generated files are saved
        :type work_dir: `str`
        :param ym_results_path: path to results intersecting
                                `yes_work` with `maybe_work`
        :type ym_results_path: `str`
        :param stats: data structure to hold the statistical data
        :type stats: `dict`
        :rtype: `dict`

        """
        catalogue = {yes_work: self._no_label, maybe_work: self._maybe_label}
        self._run_query(ym_results_path, self._store.intersection, [catalogue],
                        False)
        # Though this is the intersection only between "yes" and
        # "maybe", the percentage of overlap is added to the "common"
        # stat rather than "shared". Then, in _process_diff, the
        # percentage of difference between "yes" and "no" can be
        # removed from "common" and added to "shared".
        return self._update_stats('intersect', work_dir, ym_results_path,
                                  yes_work, maybe_work, stats, COMMON, UNIQUE)

    def _process_maybe_work(self, yes_work, maybe_work, work_dir,
                            yn_results_path, stats):
        """Returns statistics of how `yes_work` compares with `maybe_work`.

        :param yes_work: name of work for which stats are collected
        :type yes_work: `str`
        :param maybe_work: name of work being compared with `yes_work`
        :type maybe_work: `str`
        :param work_dir: directory where generated files are saved
        :type work_dir: `str`
        :param yn_results_path: path to results intersecting
                                `yes_work` with "no" works
        :type yn_results_path: `str`
        :param stats: data structure to hold statistical data of the
                      comparison
        :type stats: `dict`
        :rtype: `dict`

        """
        if maybe_work == yes_work:
            return stats
        self._logger.info(
            'Processing "maybe" work {} against "yes" work {}.'.format(
                maybe_work, yes_work))
        # Set base values for each statistic of interest, for each
        # witness.
        for siglum in self._corpus.get_sigla(maybe_work):
            witness = (maybe_work, siglum)
            stats[COMMON][witness] = 0
            stats[SHARED][witness] = 0
            stats[UNIQUE][witness] = 100
        works = [yes_work, maybe_work]
        # Sort the works to have a single filename for the
        # intersection each pair of works, whether they are yes or
        # maybe. This saves repeating the intersection with the roles
        # switched, since _run_query will use a found file rather than
        # rerun the query.
        works.sort()
        ym_results_path = os.path.join(
            self._ym_intersects_dir, '{}_intersect_{}.csv'.format(*works))
        stats = self._process_intersection(yes_work, maybe_work, work_dir,
                                           ym_results_path, stats)
        stats = self._process_diff(yes_work, maybe_work, work_dir,
                                   ym_results_path, yn_results_path, stats)
        return stats

    def _process_works(self, maybe_works, no_works, output_dir):
        """Collect and return the data of how each work in `maybe_works`
        relates to each other work.

        :param maybe_works:
        :type maybe_works: `list` of `str`
        :param no_works:
        :type no_works: `list` of `str`
        :param output_dir: base output directory
        :type output_dir: `str`
        :rtype: `pandas.DataFrame`

        """
        output_data_dir = os.path.join(output_dir, 'data')
        no_catalogue = {work: self._no_label for work in no_works}
        self._ym_intersects_dir = os.path.join(output_data_dir,
                                               'ym_intersects')
        data = {}
        os.makedirs(self._ym_intersects_dir, exist_ok=True)
        for yes_work in maybe_works:
            no_catalogue[yes_work] = self._maybe_label
            stats = self._process_yes_work(yes_work, no_catalogue,
                                           maybe_works, output_data_dir)
            no_catalogue.pop(yes_work)
            for scope in (SHARED, COMMON, UNIQUE):
                work_data = stats[scope]
                index = pd.MultiIndex.from_tuples(
                    list(work_data.keys()), names=[RELATED_WORK, SIGLUM])
                data[(yes_work, scope)] = pd.Series(list(work_data.values()),
                                                    index=index)
        df = pd.DataFrame(data)
        df.columns.names = [BASE_WORK, SCOPE]
        df = df.stack(BASE_WORK).swaplevel(
            BASE_WORK, SIGLUM).swaplevel(RELATED_WORK, BASE_WORK)
        return df

    def _process_yes_work(self, yes_work, no_catalogue, maybe_works,
                          output_dir):
        """Returns statistics of how `yes_work` compares with the other works
        in `no_catalogue` and the "maybe" works.

        :param yes_work: name of work being processed
        :type yes_work: `str`
        :param no_catalogue: catalogue of containing `yes_work` and the "no"
                             works
        :type no_catalogue: `Catalogue`
        :param maybe_works: names of "maybe" works
        :type maybe_works: `list` of `str`
        :param output_dir: directory where generated files are saved
        :type output_dir: `str`
        :rtype: `dict`

        """
        self._logger.info('Processing "maybe" work {} as "yes".'.format(
            yes_work))
        stats = {COMMON: {}, SHARED: {}, UNIQUE: {}}
        yes_work_dir = os.path.join(output_dir, yes_work)
        os.makedirs(yes_work_dir, exist_ok=True)
        results_path = os.path.join(yes_work_dir, 'intersect_with_no.csv')
        self._run_query(results_path, self._store.intersection, [no_catalogue])
        for maybe_work in maybe_works:
            stats = self._process_maybe_work(
                yes_work, maybe_work, yes_work_dir, results_path, stats)
        return stats

    def _run_query(self, path, query, query_args, drop_no=True):
        """Runs `query` and outputs results to a file at `path`.

        If `path` exists, the query is not run.

        :param path: path to output results to
        :type path: `str`
        :param query: query to run
        :type query: `method`
        :param query_args: arguments to supply to the query
        :type query_args: `list`
        :param drop_no: whether to drop results from the No corpus
        :type drop_no: `bool`

        """
        if os.path.exists(path):
            return
        output_results = io.StringIO(newline='')
        query(*query_args, output_fh=output_results)
        with open(path, mode='w', encoding='utf-8', newline='') as fh:
            if drop_no:
                self._drop_no_label_results(output_results, fh)
            else:
                fh.write(output_results.getvalue())

    def _update_stats(self, stats_type, work_dir, results_path, yes_work,
                      maybe_work, stats, add_type, minus_type):
        stats_path = os.path.join(work_dir, 'stats_{}_{}.csv'.format(
            stats_type, maybe_work))
        self._generate_statistics(stats_path, results_path)
        with open(stats_path, encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row[constants.WORK_FIELDNAME] == maybe_work:
                    witness = (maybe_work, row[constants.SIGLUM_FIELDNAME])
                    ratio = float(row[constants.PERCENTAGE_FIELDNAME])
                    stats[add_type][witness] += ratio
                    stats[minus_type][witness] -= ratio
        return stats
