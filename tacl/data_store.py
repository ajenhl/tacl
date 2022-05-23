"""Module containing the DataStore class."""

import csv
import logging
import os.path
import sqlite3
import sys
import tempfile

import pandas as pd

from . import constants
from .exceptions import (MalformedDataStoreError, MalformedQueryError,
                         MalformedResultsError)
from .text import WitnessText


class DataStore:

    """Class representing the data store for text data.

    It provides an interface to the underlying database, with methods
    to add and query data.

    """

    def __init__(self, db_name, use_memory=True, ram=0, must_exist=True):
        self._logger = logging.getLogger(__name__)
        if db_name == ':memory:':
            self._db_name = db_name
        else:
            self._db_name = os.path.abspath(db_name)
            if must_exist and not os.path.exists(self._db_name):
                raise MalformedDataStoreError(
                    constants.MISSING_DATA_STORE_ERROR.format(self._db_name))
        self._conn = sqlite3.connect(self._db_name)
        self._conn.row_factory = sqlite3.Row
        if use_memory:
            self._conn.execute(constants.PRAGMA_TEMP_STORE_SQL)
        if ram:
            cache_size = ram * -1000000
            self._conn.execute(constants.PRAGMA_CACHE_SIZE_SQL.format(
                cache_size))
        self._conn.execute(constants.PRAGMA_COUNT_CHANGES_SQL)
        self._conn.execute(constants.PRAGMA_FOREIGN_KEYS_SQL)
        self._conn.execute(constants.PRAGMA_LOCKING_MODE_SQL)
        self._conn.execute(constants.PRAGMA_SYNCHRONOUS_SQL)

    def _add_indices(self):
        """Adds the database indices relating to n-grams."""
        self._logger.info('Adding database indices')
        self._conn.execute(constants.CREATE_INDEX_TEXTNGRAM_SQL)
        self._logger.info('Indices added')

    def add_ngrams(self, corpus, minimum, maximum, catalogue=None,
                   text_class=WitnessText):
        """Adds n-gram data from `corpus` to the data store.

        :param corpus: corpus of works
        :type corpus: `Corpus`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :param catalogue: optional catalogue to limit corpus to
        :type catalogue: `Catalogue`
        :param text_class: class to use to represent each witness
        :type text_class: subclass of `Text`

        """
        if not isinstance(minimum, int) or not isinstance(maximum, int):
            raise MalformedQueryError(
                constants.NGRAM_SIZE_MUST_BE_INTEGER_ERROR)
        if minimum < 1:
            raise MalformedQueryError(constants.NGRAM_SIZE_TOO_SMALL_ERROR)
        if minimum > maximum:
            raise MalformedQueryError(
                constants.NGRAM_MINIMUM_SIZE_GREATER_THAN_MAXIMUM_ERROR)
        self._initialise_database()
        if catalogue:
            for work in catalogue:
                db_witnesses = self._get_text_ids(work)
                has_witnesses = False
                for witness in corpus.get_witnesses(
                        work, text_class=text_class):
                    has_witnesses = True
                    text_id = self._add_text_ngrams(witness, minimum, maximum)
                    db_witnesses.pop(text_id, None)
                if not has_witnesses:
                    raise FileNotFoundError(
                        constants.CATALOGUE_WORK_NOT_IN_CORPUS_ERROR.format(
                            work))
                for text_id, names in db_witnesses:
                    self._delete_text(text_id, *names)
        else:
            db_witnesses = self._get_text_ids()
            for witness in corpus.get_witnesses(text_class=text_class):
                text_id = self._add_text_ngrams(witness, minimum, maximum)
                db_witnesses.pop(text_id, None)
            for text_id, names in db_witnesses.items():
                self._delete_text(text_id, *names)
        self._add_indices()
        self._analyse()

    def _add_temporary_ngrams(self, ngrams):
        """Adds `ngrams` to a temporary table."""
        # Remove duplicate n-grams, empty n-grams, and non-string n-grams.
        ngrams = [ngram for ngram in ngrams if ngram and isinstance(
            ngram, str)]
        # Deduplicate while preserving order (useful for testing).
        seen = {}
        ngrams = [seen.setdefault(x, x) for x in ngrams if x not in seen]
        self._conn.execute(constants.DROP_TEMPORARY_NGRAMS_TABLE_SQL)
        self._conn.execute(constants.CREATE_TEMPORARY_NGRAMS_TABLE_SQL)
        self._conn.executemany(constants.INSERT_TEMPORARY_NGRAM_SQL,
                               [(ngram,) for ngram in ngrams])

    def _add_temporary_results_sets(self, results_filenames, labels):
        if len(labels) < 2:
            raise MalformedQueryError(
                constants.INSUFFICIENT_LABELS_QUERY_ERROR)
        if len(results_filenames) != len(labels):
            raise MalformedQueryError(
                constants.SUPPLIED_ARGS_LENGTH_MISMATCH_ERROR)
        self._create_temporary_results_table()
        for results_filename, label in zip(results_filenames, labels):
            with open(results_filename, encoding='utf-8', newline='') as fh:
                self._add_temporary_results(fh, label)
        self._add_temporary_results_index()
        self._analyse('temp.InputResults')

    def _add_temporary_results(self, results, label):
        """Adds `results` to a temporary table with `label`.

        :param results: results file
        :type results: `File`
        :param label: label to be associated with results
        :type label: `str`

        """
        NGRAM, SIZE, NAME, SIGLUM, COUNT, LABEL = constants.QUERY_FIELDNAMES
        reader = csv.DictReader(results)
        try:
            data = [(row[NGRAM], row[SIZE], row[NAME], row[SIGLUM], row[COUNT],
                     label) for row in reader]
        except KeyError:
            missing_cols = [col for col in constants.QUERY_FIELDNAMES if col
                            not in reader.fieldnames]
            raise MalformedResultsError(
                constants.MISSING_REQUIRED_COLUMNS_ERROR.format(
                    ', '.join(missing_cols)))
        self._conn.executemany(constants.INSERT_TEMPORARY_RESULTS_SQL, data)

    def _add_temporary_results_index(self):
        self._logger.info('Adding index to temporary results table')
        self._conn.execute(constants.CREATE_INDEX_INPUT_RESULTS_SQL)
        self._logger.info('Index added')

    def _add_text_ngrams(self, witness, minimum, maximum):
        """Adds n-gram data from `witness` to the data store.

        :param witness: witness to get n-grams from
        :type witness: `WitnessText`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`
        :rtype: `int`

        """
        text_id = self._get_text_id(witness)
        self._logger.info('Adding n-grams ({} <= n <= {}) for {}'.format(
            minimum, maximum, witness.get_filename()))
        skip_sizes = []
        for size in range(minimum, maximum + 1):
            if self._has_ngrams(text_id, size):
                self._logger.info(
                    '{}-grams are already in the database'.format(size))
                skip_sizes.append(size)
        for size, ngrams in witness.get_ngrams(minimum, maximum, skip_sizes):
            self._add_text_size_ngrams(text_id, size, ngrams)
        return text_id

    def _add_text_record(self, witness):
        """Adds a Text record for `witness`.

        :param witness: witness to add a record for
        :type text: `WitnessText`

        """
        filename = witness.get_filename()
        self._logger.info('Adding record for text {}'.format(filename))
        checksum = witness.get_checksum()
        token_count = len(witness.get_tokens())
        with self._conn:
            cursor = self._conn.execute(
                constants.INSERT_TEXT_SQL,
                [witness.work, witness.siglum, checksum, token_count, ''])
        return cursor.lastrowid

    def _add_text_size_ngrams(self, text_id, size, ngrams):
        """Adds `ngrams`, that are of size `size`, to the data store.

        The added `ngrams` are associated with `text_id`.

        :param text_id: database ID of text associated with `ngrams`
        :type text_id: `int`
        :param size: size of n-grams
        :type size: `int`
        :param ngrams: n-grams to be added
        :type ngrams: `collections.Counter`

        """
        unique_ngrams = len(ngrams)
        self._logger.info('Adding {} unique {}-grams'.format(
            unique_ngrams, size))
        parameters = [[text_id, ngram, size, count]
                      for ngram, count in ngrams.items()]
        with self._conn:
            self._conn.execute(constants.INSERT_TEXT_HAS_NGRAM_SQL,
                               [text_id, size, unique_ngrams])
            self._conn.executemany(constants.INSERT_NGRAM_SQL, parameters)

    def _analyse(self, table=''):
        """Analyses the database, or `table` if it is supplied.

        :param table: optional name of table to analyse
        :type table: `str`

        """
        self._logger.info('Starting analysis of database')
        self._conn.execute(constants.ANALYSE_SQL.format(table))
        self._logger.info('Analysis of database complete')

    @staticmethod
    def _check_diff_result(row, matches, tokenize, join):
        """Returns `row`, possibly with its count changed to 0, depending on
        the status of the n-grams that compose it.

        The n-gram represented in `row` can be decomposed into two
        (n-1)-grams. If neither sub-n-gram is present in `matches`, do
        not change the count since this is a new difference.

        If both sub-n-grams are present with a positive count, do not
        change the count as it is composed entirely of sub-ngrams and
        therefore not filler.

        Otherwise, change the count to 0 as the n-gram is filler.

        :param row: result row of the n-gram to check
        :type row: pandas.Series
        :param matches: (n-1)-grams and their associated counts to check
                        against
        :type matches: `dict`
        :param tokenize: function to tokenize a string
        :type tokenize: `function`
        :param join: function to join tokens into a string
        :type join: `function`
        :rtype: pandas.Series

        """
        ngram_tokens = tokenize(row[constants.NGRAM_FIELDNAME])
        sub_ngram1 = join(ngram_tokens[:-1])
        sub_ngram2 = join(ngram_tokens[1:])
        count = constants.COUNT_FIELDNAME
        discard = False
        # For performance reasons, avoid searching through matches
        # unless necessary.
        status1 = matches.get(sub_ngram1)
        if status1 == 0:
            discard = True
        else:
            status2 = matches.get(sub_ngram2)
            if status2 == 0:
                discard = True
            elif (status1 is None) ^ (status2 is None):
                discard = True
        if discard:
            row[count] = 0
        return row

    def counts(self, catalogue, output_fh):
        """Returns `output_fh` populated with CSV results giving
        n-gram counts of the witnesses of the works in `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = list(self._set_labels(catalogue))
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_COUNTS_SQL.format(label_placeholders)
        self._logger.info('Running counts query')
        self._logger.debug('Query: {}\nLabels: {}'.format(query, labels))
        cursor = self._conn.execute(query, labels)
        return self._csv(cursor, constants.COUNTS_FIELDNAMES, output_fh)

    def _create_temporary_results_table(self):
        self._conn.execute(constants.DROP_TEMPORARY_RESULTS_TABLE_SQL)
        self._conn.execute(constants.CREATE_TEMPORARY_RESULTS_TABLE_SQL)

    def _csv(self, cursor, fieldnames, output_fh):
        """Writes the rows of `cursor` in CSV format to `output_fh`
        and returns it.

        :param cursor: database cursor containing data to be output
        :type cursor: `sqlite3.Cursor`
        :param fieldnames: row headings
        :type fieldnames: `list`
        :param output_fh: file to write data to
        :type output_fh: file object
        :rtype: file object

        """
        self._logger.info('Finished query; outputting results in CSV format')
        # Specify a lineterminator to avoid an extra \r being added on
        # Windows; see
        # https://stackoverflow.com/questions/3191528/csv-in-python-adding-extra-carriage-return
        if sys.platform in ('win32', 'cygwin') and output_fh is sys.stdout:
            writer = csv.writer(output_fh, lineterminator='\n')
        else:
            writer = csv.writer(output_fh)
        writer.writerow(fieldnames)
        for row in cursor:
            writer.writerow(row)
        self._logger.info('Finished outputting results')
        return output_fh

    def _csv_temp(self, cursor, fieldnames):
        """Writes the rows of `cursor` in CSV format to a temporary file and
        returns the path to that file.

        :param cursor: database cursor containing data to be output
        :type cursor: `sqlite3.Cursor`
        :param fieldnames: row headings
        :type fieldnames: `list`
        :rtype: `str`

        """
        temp_fd, temp_path = tempfile.mkstemp(text=True)
        with open(temp_fd, 'w', encoding='utf-8', newline='') as results_fh:
            self._csv(cursor, fieldnames, results_fh)
        return temp_path

    def _delete_text(self, text_id, work, siglum):
        """Deletes the text identified by `text_id` from the database.

        :param text_id: database ID of text
        :type text_id: `int`
        :param work: name of text's work
        :type work: `str`
        :param siglum: text's siglum
        :type siglum: `str`

        """
        self._logger.info('Deleting text {} {} from database'.format(
            work, siglum))
        with self._conn:
            self._conn.execute(constants.DELETE_TEXT_SQL, [text_id])

    def _delete_text_ngrams(self, text_id):
        """Deletes all n-grams associated with `text_id` from the data
        store.

        :param text_id: database ID of text
        :type text_id: `int`

        """
        with self._conn:
            self._conn.execute(constants.DELETE_TEXT_NGRAMS_SQL, [text_id])
            self._conn.execute(constants.DELETE_TEXT_HAS_NGRAMS_SQL, [text_id])

    def _diff(self, cursor, tokenizer, output_fh):
        """Returns output_fh with diff results that have been reduced.

        Uses a temporary file to store the results from `cursor`
        before being reduced, in order to not have the results stored
        in memory twice.

        :param cursor: database cursor containing raw diff data
        :type cursor: `sqlite3.Cursor`
        :param tokenizer: tokenizer for the n-grams
        :type tokenizer: `Tokenizer`
        :type output_fh: file-like object
        :rtype: file-like object

        """
        temp_path = self._csv_temp(cursor, constants.QUERY_FIELDNAMES)
        output_fh = self._reduce_diff_results(temp_path, tokenizer, output_fh)
        try:
            os.remove(temp_path)
        except OSError as e:
            self._logger.error('Failed to remove temporary file containing '
                               'unreduced results: {}'.format(e))
        return output_fh

    def diff(self, catalogue, tokenizer, output_fh):
        """Returns `output_fh` populated with CSV results giving the n-grams
        that are unique to the witnesses of each labelled set of works
        in `catalogue`.

        Note that this is not the same as the symmetric difference of
        these sets, except in the case where there are only two
        labels.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param tokenizer: tokenizer for the n-grams
        :type tokenizer: `Tokenizer`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = self._sort_labels(self._set_labels(catalogue))
        if len(labels) < 2:
            raise MalformedQueryError(
                constants.INSUFFICIENT_LABELS_QUERY_ERROR)
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_DIFF_SQL.format(label_placeholders,
                                                 label_placeholders)
        parameters = labels + labels
        self._logger.info('Running diff query')
        self._logger.debug('Query: {}\nLabels: {}'.format(query, labels))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._diff(cursor, tokenizer, output_fh)

    def diff_asymmetric(self, catalogue, prime_label, tokenizer, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        difference in n-grams between the witnesses of labelled sets
        of works in `catalogue`, limited to those works labelled with
        `prime_label`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param prime_label: label to limit results to
        :type prime_label: `str`
        :param tokenizer: tokenizer for the n-grams
        :type tokenizer: `Tokenizer`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = list(self._set_labels(catalogue))
        if len(labels) < 2:
            raise MalformedQueryError(
                constants.INSUFFICIENT_LABELS_QUERY_ERROR)
        try:
            labels.remove(prime_label)
        except ValueError:
            raise MalformedQueryError(
                constants.LABEL_NOT_IN_CATALOGUE_ERROR.format(prime_label))
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_DIFF_ASYMMETRIC_SQL.format(label_placeholders)
        parameters = [prime_label, prime_label] + labels
        self._logger.info('Running asymmetric diff query')
        self._logger.debug('Query: {}\nLabels: {}\nPrime label: {}'.format(
            query, labels, prime_label))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._diff(cursor, tokenizer, output_fh)

    def diff_supplied(self, results_filenames, labels, tokenizer, output_fh):
        """Returns `output_fh` populated with CSV results giving the n-grams
        that are unique to the witnesses in each set of works in
        `results_sets`, using the labels in `labels`.

        Note that this is not the same as the symmetric difference of
        these sets, except in the case where there are only two
        labels.

        :param results_filenames: list of results filenames to be diffed
        :type results_filenames: `list` of `str`
        :param labels: labels to be applied to the results_sets
        :type labels: `list`
        :param tokenizer: tokenizer for the n-grams
        :type tokenizer: `Tokenizer`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        self._add_temporary_results_sets(results_filenames, labels)
        query = constants.SELECT_DIFF_SUPPLIED_SQL
        self._logger.info('Running supplied diff query')
        self._logger.debug('Query: {}'.format(query))
        self._log_query_plan(query, [])
        cursor = self._conn.execute(query)
        return self._diff(cursor, tokenizer, output_fh)

    def _drop_indices(self):
        """Drops the database indices relating to n-grams."""
        self._logger.info('Dropping database indices')
        self._conn.execute(constants.DROP_TEXTNGRAM_INDEX_SQL)
        self._logger.info('Finished dropping database indices')

    def _get_checksum(self, text_id):
        """Returns the checksum for the text with `text_id`."""

    @staticmethod
    def _get_intersection_subquery(labels):
        # Create nested subselects.
        subquery = constants.SELECT_INTERSECT_SUB_SQL
        # The subqueries are nested in reverse order of 'size', so
        # that the inmost select is operating on the smallest corpus,
        # thereby minimising the result sets of outer queries the most.
        for label in labels[1:]:
            subquery = constants.SELECT_INTERSECT_SUB_SQL + \
                       constants.SELECT_INTERSECT_SUB_EXTRA_SQL.format(
                           subquery)
        return subquery

    @staticmethod
    def _get_placeholders(items):
        """Returns a string of placeholders, one for each item in
        `items`.

        :param items: items to create placeholders for
        :type items: `list`
        :rtype: `str`

        """
        return ('?,' * len(items)).strip(',')

    def _get_text_id(self, witness):
        """Returns the database ID of the Text record for `witness`.

        This may require creating such a record.

        If `text`\'s checksum does not match an existing record's
        checksum, the record's checksum is updated and all associated
        TextNGram and TextHasNGram records are deleted.

        :param witness: witness to add a record for
        :type witness: `WitnessText`
        :rtype: `int`

        """
        text_record = self._conn.execute(
            constants.SELECT_TEXT_SQL,
            [witness.work, witness.siglum]).fetchone()
        if text_record is None:
            text_id = self._add_text_record(witness)
        else:
            text_id = text_record['id']
            if text_record['checksum'] != witness.get_checksum():
                filename = witness.get_filename()
                self._logger.info('Text {} has changed since it was added to '
                                  'the database'.format(filename))
                self._update_text_record(witness, text_id)
                self._logger.info('Deleting potentially out-of-date n-grams')
                self._delete_text_ngrams(text_id)
        return text_id

    def _get_text_ids(self, work=None):
        """Returns a dictionary of IDs of texts in the database, with work and
        siglum as values for each.

        If `work` is supplied, returns IDs of texts that are
        associated with the specified work.

        :param work: optional name of work to limit texts to
        :type work: `str`
        :rtype: `dict`

        """
        if work is None:
            query = constants.SELECT_TEXTS_SQL
            rows = self._conn.execute(query).fetchall()
        else:
            query = constants.SELECT_WORK_TEXTS_SQL
            rows = self._conn.execute(query, [work]).fetchall()
        return {row['id']: [row['work'], row['siglum']] for row in rows}

    def _has_ngrams(self, text_id, size):

        """Returns True if a text has existing records for n-grams of
        size `size`.

        :param text_id: database ID of text to check
        :type text_id: `int`
        :param size: size of n-grams
        :type size: `int`
        :rtype: `bool`

        """
        if self._conn.execute(constants.SELECT_HAS_NGRAMS_SQL,
                              [text_id, size]).fetchone() is None:
            return False
        return True

    def _initialise_database(self):
        """Creates the database schema.

        This will not create tables or indices that already exist and
        is safe to be called on an existing database.

        """
        self._logger.info('Creating database schema, if necessary')
        self._conn.execute(constants.CREATE_TABLE_TEXT_SQL)
        self._conn.execute(constants.CREATE_TABLE_TEXTNGRAM_SQL)
        self._conn.execute(constants.CREATE_TABLE_TEXTHASNGRAM_SQL)
        self._conn.execute(constants.CREATE_INDEX_TEXTHASNGRAM_SQL)
        self._conn.execute(constants.CREATE_INDEX_TEXT_SQL)

    def intersection(self, catalogue, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        intersection in n-grams of the witnesses of labelled sets of
        works in `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = self._sort_labels(self._set_labels(catalogue))
        if len(labels) < 2:
            raise MalformedQueryError(
                constants.INSUFFICIENT_LABELS_QUERY_ERROR)
        label_placeholders = self._get_placeholders(labels)
        subquery = self._get_intersection_subquery(labels)
        query = constants.SELECT_INTERSECT_SQL.format(label_placeholders,
                                                      subquery)
        parameters = labels + labels
        self._logger.info('Running intersection query')
        self._logger.debug('Query: {}\nLabels: {}'.format(query, labels))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def intersection_supplied(self, results_filenames, labels, output_fh):
        """Returns `output_fh` populated with CSV results giving the n-grams
        that are common to witnesses in every set of works in
        `results_sets`, using the labels in `labels`.

        :param results_filenames: list of results to be diffed
        :type results_filenames: `list` of `str`
        :param labels: labels to be applied to the results_sets
        :type labels: `list`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        self._add_temporary_results_sets(results_filenames, labels)
        query = constants.SELECT_INTERSECT_SUPPLIED_SQL
        parameters = [len(labels)]
        self._logger.info('Running supplied intersect query')
        self._logger.debug('Query: {}\nNumber of labels: {}'.format(
            query, parameters[0]))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def _log_query_plan(self, query, parameters):
        cursor = self._conn.execute('EXPLAIN QUERY PLAN ' + query, parameters)
        query_plan = 'Query plan:\n'
        for row in cursor.fetchall():
            query_plan += '|'.join([str(value) for value in row]) + '\n'
        self._logger.debug(query_plan)

    def query(self, query, parameters, output_fh):
        """Run `query` with `parameters`, outputting results to `output_fh`."""
        self._logger.info('Running supplied query')
        self._logger.debug('Query: {}\nParameters: {}'.format(
            query, parameters))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        headers = [column[0] for column in cursor.description]
        return self._csv(cursor, headers, output_fh)

    def _reduce_diff_results(self, matches_path, tokenizer, output_fh):
        """Returns `output_fh` populated with a reduced set of data from
        `matches_fh`.

        Diff results typically contain a lot of filler results that
        serve only to hide real differences. If one text has a single
        extra token than another, the diff between them will have
        results for every n-gram containing that extra token, which is
        not helpful. This method removes these filler results by
        'reducing down' the results.

        :param matches_path: filepath or buffer of CSV results to be reduced
        :type matches_path: `str` or file-like object
        :param tokenizer: tokenizer for the n-grams
        :type tokenizer: `Tokenizer`
        :param output_fh: object to write results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        self._logger.info('Removing filler results')
        # For performance, perform the attribute accesses once.
        tokenize = tokenizer.tokenize
        join = tokenizer.joiner.join
        results = []
        previous_witness = (None, None)
        previous_data = {}
        # Calculate the index of ngram and count columns in a Pandas
        # named tuple row, as used below. The +1 is due to the tuple
        # having the row index as the first element.
        ngram_index = constants.QUERY_FIELDNAMES.index(
            constants.NGRAM_FIELDNAME) + 1
        count_index = constants.QUERY_FIELDNAMES.index(
            constants.COUNT_FIELDNAME) + 1
        # Operate over individual witnesses and sizes, so that there
        # is no possible results pollution between them.
        grouped = pd.read_csv(matches_path, encoding='utf-8',
                              na_filter=False).groupby(
            [constants.WORK_FIELDNAME, constants.SIGLUM_FIELDNAME,
             constants.SIZE_FIELDNAME])
        for (work, siglum, size), group in grouped:
            if (work, siglum) != previous_witness:
                previous_matches = group
                previous_witness = (work, siglum)
            else:
                self._logger.debug(
                    'Reducing down {} {}-grams for {} {}'.format(
                        len(group.index), size, work, siglum))
                if previous_matches.empty:
                    reduced_count = 0
                else:
                    previous_matches = group.apply(
                        self._check_diff_result, axis=1,
                        args=(previous_data, tokenize, join))
                    reduced_count = len(previous_matches[previous_matches[
                                        constants.COUNT_FIELDNAME] != 0].index)
                self._logger.debug('Reduced down to {} grams'.format(
                    reduced_count))
            # Put the previous matches into a form that is more
            # performant for the lookups made in _check_diff_result.
            previous_data = {}
            for row in previous_matches.itertuples():
                previous_data[row[ngram_index]] = row[count_index]
            if not previous_matches.empty:
                results.append(previous_matches[previous_matches[
                    constants.COUNT_FIELDNAME] != 0])
        reduced_results = pd.concat(results, ignore_index=True).reindex(
            columns=constants.QUERY_FIELDNAMES)
        reduced_results.to_csv(output_fh, encoding='utf-8', float_format='%d',
                               index=False)
        return output_fh

    def search(self, catalogue, ngrams, output_fh):
        """Returns `output_fh` populated with CSV results for each n-gram in
        `ngrams` that occurs within labelled witnesses in `catalogue`.

        If `ngrams` is empty, include all n-grams.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param ngrams: n-grams to search for
        :type ngrams: `list` of `str`
        :param output_fh: object to write results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = list(self._set_labels(catalogue))
        label_placeholders = self._get_placeholders(labels)
        if ngrams:
            self._add_temporary_ngrams(ngrams)
            query = constants.SELECT_SEARCH_SQL.format(label_placeholders)
        else:
            query = constants.SELECT_SEARCH_ALL_SQL.format(label_placeholders)
        self._logger.info('Running search query')
        self._logger.debug('Query: {}\nN-grams: {}'.format(
            query, ', '.join(ngrams)))
        self._log_query_plan(query, labels)
        cursor = self._conn.execute(query, labels)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def _set_labels(self, catalogue):
        """Returns a dictionary of the unique labels in `catalogue` and the
        count of all tokens associated with each, and sets the record
        of each Text to its corresponding label.

        Texts that do not have a label specified are set to the empty
        string.

        Token counts are included in the results to allow for
        semi-accurate sorting based on corpora size.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :rtype: `dict`

        """
        with self._conn:
            self._conn.execute(constants.UPDATE_LABELS_SQL, [''])
            labels = {}
            for work, label in catalogue.items():
                self._conn.execute(constants.UPDATE_LABEL_SQL, [label, work])
                cursor = self._conn.execute(
                    constants.SELECT_TEXT_TOKEN_COUNT_SQL, [work])
                token_count = cursor.fetchone()['token_count']
                labels[label] = labels.get(label, 0) + token_count
        return labels

    @staticmethod
    def _sort_labels(label_data):
        """Returns the labels in `label_data` sorted in descending order
        according to the 'size' (total token count) of their referent
        corpora.

        :param label_data: labels (with their token counts) to sort
        :type: `dict`
        :rtype: `list`

        """
        labels = list(label_data)
        labels.sort(key=label_data.get, reverse=True)
        return labels

    def _update_text_record(self, witness, text_id):
        """Updates the record with `text_id` with `witness`\'s checksum and
        token count.

        :param withness: witness to update from
        :type witness: `WitnessText`
        :param text_id: database ID of Text record
        :type text_id: `int`

        """
        checksum = witness.get_checksum()
        token_count = len(witness.get_tokens())
        with self._conn:
            self._conn.execute(constants.UPDATE_TEXT_SQL,
                               [checksum, token_count, text_id])

    def validate(self, corpus, catalogue):
        """Returns True if all of the files labelled in `catalogue`
        are up-to-date in the database.

        :param corpus: corpus of works
        :type corpus: `Corpus`
        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :rtype: `bool`

        """
        is_valid = True
        for name in catalogue:
            count = 0
            # It is unfortunate that this creates WitnessText objects
            # for each work, since that involves reading the file.
            for witness in corpus.get_witnesses(name):
                count += 1
                filename = witness.get_filename()
                row = self._conn.execute(
                    constants.SELECT_TEXT_SQL,
                    [witness.work, witness.siglum]).fetchone()
                if row is None:
                    is_valid = False
                    self._logger.warning(
                        'No record (or n-grams) exists for {} in '
                        'the database'.format(filename))
                elif row['checksum'] != witness.get_checksum():
                    is_valid = False
                    self._logger.warning(
                        '{} has changed since its n-grams were '
                        'added to the database'.format(filename))
            if count == 0:
                raise FileNotFoundError(
                    constants.CATALOGUE_WORK_NOT_IN_CORPUS_ERROR.format(
                        name))
        return is_valid
