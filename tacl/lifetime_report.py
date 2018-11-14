import os
import os.path

from . import constants
from .report import Report


class LifetimeReport (Report):

    """Class for creating a lifetime report from a catalogue and a set of
    results, consisting of:

    * an HTML table showing the disposition of each n-gram across the
      ordered corpora (with texts and count ranges);

    * an HTML table showing, for each corpus, the n-grams that first
      occurred, only occurred, and last occurred in that corpus; and

    * results files for each category (first occurred in, only
      occurred in , last occurred in) for each corpus.

    This report may be generated from any results file, but is most
    usefully applied to the output of the lifetime script (in the
    tacl-extra package).

    """

    _report_name = 'lifetime'

    def generate(self, output_dir, catalogue, results, label):
        """Generates the report, writing it to `output_dir`."""
        data = results.get_raw_data()
        labels = catalogue.ordered_labels
        ngrams = self._generate_results(output_dir, labels, data)
        ngram_table = self._generate_ngram_table(output_dir, labels, data)
        corpus_table = self._generate_corpus_table(labels, ngrams)
        context = {'corpus_table': corpus_table, 'focus_label': label,
                   'labels': labels, 'ngram_table': ngram_table, 'sep': os.sep}
        report_name = 'lifetime-{}.html'.format(label)
        self._write(context, output_dir, report_name)

    def _generate_corpus_table(self, labels, ngrams):
        """Returns an HTML table containing data on each corpus' n-grams."""
        html = []
        for label in labels:
            html.append(self._render_corpus_row(label, ngrams))
        return '\n'.join(html)

    def _generate_ngram_table(self, output_dir, labels, results):
        """Returns an HTML table containing data on each n-gram in
        `results`."""
        html = []
        grouped = results.groupby(constants.NGRAM_FIELDNAME)
        row_template = self._generate_ngram_row_template(labels)
        for name, group in grouped:
            html.append(self._render_ngram_row(name, group, row_template,
                                               labels))
        return '\n'.join(html)

    def _generate_ngram_row_template(self, labels):
        """Returns the HTML template for a row in the n-gram table."""
        cells = ['<td>{ngram}</td>']
        for label in labels:
            cells.append('<td>{{{}}}</td>'.format(label))
        return '\n'.join(cells)

    def _generate_results(self, output_dir, labels, results):
        """Creates multiple results files in `output_dir` based on `results`.

        For each label in `labels`, create three results file,
        containing those n-grams with that label that first occurred,
        only occurred, and last occurred in that label.

        """
        ngrams = {}
        for idx, label in enumerate(labels):
            now_results = results[results[constants.LABEL_FIELDNAME] == label]
            earlier_labels = labels[:idx]
            earlier_ngrams = results[results[constants.LABEL_FIELDNAME].isin(
                earlier_labels)][constants.NGRAM_FIELDNAME].values
            later_labels = labels[idx + 1:]
            later_ngrams = results[results[constants.LABEL_FIELDNAME].isin(
                later_labels)][constants.NGRAM_FIELDNAME].values
            first_ngrams = []
            only_ngrams = []
            last_ngrams = []
            for ngram in now_results[constants.NGRAM_FIELDNAME].unique():
                if ngram in earlier_ngrams:
                    if ngram not in later_ngrams:
                        last_ngrams.append(ngram)
                elif ngram in later_ngrams:
                    first_ngrams.append(ngram)
                else:
                    only_ngrams.append(ngram)
            self._save_results(output_dir, label, now_results, first_ngrams,
                               'first')
            self._save_results(output_dir, label, now_results, only_ngrams,
                               'only')
            self._save_results(output_dir, label, now_results, last_ngrams,
                               'last')
            ngrams[label] = {'first': first_ngrams, 'last': last_ngrams,
                             'only': only_ngrams}
        return ngrams

    def _render_corpus_row(self, label, ngrams):
        """Returns the HTML for a corpus row."""
        row = ('<tr>\n<td>{label}</td>\n<td>{first}</td>\n<td>{only}</td>\n'
               '<td>{last}</td>\n</tr>')
        cell_data = {'label': label}
        for period in ('first', 'only', 'last'):
            cell_data[period] = ', '.join(ngrams[label][period])
        return row.format(**cell_data)

    def _render_ngram_row(self, ngram, ngram_group, row_template, labels):
        """Returns the HTML for an n-gram row."""
        cell_data = {'ngram': ngram}
        label_data = {}
        for label in labels:
            label_data[label] = []
        work_grouped = ngram_group.groupby(constants.WORK_FIELDNAME)
        for work, group in work_grouped:
            min_count = group[constants.COUNT_FIELDNAME].min()
            max_count = group[constants.COUNT_FIELDNAME].max()
            if min_count == max_count:
                count = min_count
            else:
                count = '{}\N{EN DASH}{}'.format(min_count, max_count)
            label_data[group[constants.LABEL_FIELDNAME].iloc[0]].append(
                '{} ({})'.format(work, count))
        for label, data in label_data.items():
            label_data[label] = '; '.join(data)
        cell_data.update(label_data)
        html = row_template.format(**cell_data)
        return '<tr>\n{}\n</tr>'.format(html)

    def _save_results(self, output_dir, label, results, ngrams, type_label):
        """Saves `results` filtered by `label` and `ngram` to `output_dir`.

        :param output_dir: directory to save results to
        :type output_dir: `str`
        :param label: catalogue label of results, used in saved filename
        :type label: `str`
        :param results: results to filter and save
        :type results: `pandas.DataFrame`
        :param ngrams: n-grams to save from results
        :type ngrams: `list` of `str`
        :param type_label: name of type of results, used in saved filename
        :type type_label: `str`

        """
        path = os.path.join(output_dir, '{}-{}.csv'.format(label, type_label))
        results[results[constants.NGRAM_FIELDNAME].isin(
            ngrams)].to_csv(path, encoding='utf-8', float_format='%d',
                            index=False)
