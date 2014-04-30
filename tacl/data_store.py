"""Module containing the DataStore class."""

import csv
import logging
import os.path
import sqlite3

from . import constants


class DataStore:

    """Class representing the data store for text data.

    It provides an interface to the underlying database, with methods
    to add and query data.

    """

    def __init__ (self, db_name, use_memory=True, ram=0):
        self._logger = logging.getLogger(__name__)
        if db_name == ':memory:':
            self._db_name = db_name
        else:
            self._db_name = os.path.abspath(db_name)
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

    def _add_indices (self):
        """Adds the database indices relating to n-grams."""
        self._logger.info('Adding database indices')
        self._conn.execute(constants.CREATE_INDEX_TEXTNGRAM_SQL)
        self._logger.info('Indices added')

    def add_ngrams (self, corpus, minimum, maximum):
        """Adds n-gram data from `corpus` to the data store.

        :param corpus: corpus of texts
        :type corpus: `Corpus`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`

        """
        self._initialise_database()
        for text in corpus.get_texts():
            self._add_text_ngrams(text, minimum, maximum)
        self._add_indices()
        self._analyse()

    def _add_temporary_ngrams (self, ngrams):
        """Adds `ngrams` to a temporary table."""
        self._conn.execute(constants.CREATE_TEMPORARY_TABLE_SQL)
        self._conn.executemany(constants.INSERT_TEMPORARY_NGRAM_SQL,
                               [(ngram,) for ngram in ngrams])

    def _add_text_ngrams (self, text, minimum, maximum):
        """Adds n-gram data from `text` to the data store.

        :param text: text to get n-grams from
        :type text: `Text`
        :param minimum: minimum n-gram size
        :type minimum: `int`
        :param maximum: maximum n-gram size
        :type maximum: `int`

        """
        text_id = self._get_text_id(text)
        self._logger.info('Adding n-grams ({} <= n <= {}) for {}'.format(
            minimum, maximum, text.get_filename()))
        for size, ngrams in text.get_ngrams(minimum, maximum):
            self._add_text_size_ngrams(text_id, size, ngrams)

    def _add_text_record (self, text):
        """Adds a Text record for `text`.

        :param text: text to add a record for
        :type text: `Text`

        """
        filename = text.get_filename()
        self._logger.info('Adding record for text {}'.format(filename))
        checksum = text.get_checksum()
        token_count = len(text.get_tokens())
        cursor = self._conn.execute(constants.INSERT_TEXT_SQL,
                                    [filename, checksum, token_count, ''])
        self._conn.commit()
        return cursor.lastrowid

    def _add_text_size_ngrams (self, text_id, size, ngrams):
        """Adds `ngrams`, that are of size `size`, to the data store.

        The added `ngrams` are associated with `text_id`.

        :param text_id: database ID of text associated with `ngrams`
        :type text_id: `int`
        :param size: size of n-grams
        :type size: `int`
        :param ngrams: n-grams to be added
        :type ngrams: `collections.Counter`

        """
        if self._has_ngrams(text_id, size):
            self._logger.info('{}-grams are already in the database'.format(
                size))
        else:
            unique_ngrams = len(ngrams)
            self._logger.info('Adding {} unique {}-grams'.format(
                unique_ngrams, size))
            parameters = [[text_id, ngram, size, count]
                          for ngram, count in ngrams.items()]
            self._conn.execute(constants.INSERT_TEXT_HAS_NGRAM_SQL,
                               [text_id, size, unique_ngrams])
            self._conn.executemany(constants.INSERT_NGRAM_SQL, parameters)
            self._conn.commit()

    def _analyse (self, table=''):
        """Analyses the database, or `table` if it is supplied.

        :param table: optional name of table analyse
        :type table: `str`

        """
        self._logger.info('Starting analysis of database')
        self._conn.execute(constants.ANALYSE_SQL.format(table))
        self._logger.info('Analysis of database complete')

    def counts (self, catalogue, output_fh):
        """Returns `output_fh` populated with CSV results giving
        n-gram counts of the texts in `catalogue`.

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

    def _csv (self, cursor, fieldnames, output_fh):
        """Writes the rows of `cursor` in CSV format to `output_fh`
        and returns it.

        :param cursor: database cursor containing data to be be output
        :type cursor: `sqlite3.Cursor`
        :param fieldnames: row headings
        :type fieldnames: `list`
        :param output_fh: file to write data to
        :type output_fh: file object
        :rtype: file object

        """
        self._logger.info('Finished query; outputting results in CSV format')
        writer = csv.writer(output_fh)
        writer.writerow(fieldnames)
        for row in cursor:
            writer.writerow([row[fieldname] for fieldname in fieldnames])
        self._logger.info('Finished outputting results')
        return output_fh

    def _delete_text_ngrams (self, text_id):
        """Deletes all n-grams associated with `text_id` from the data
        store.

        :param text_id: database ID of text
        :type text_id: `int`

        """
        self._conn.execute(constants.DELETE_TEXT_NGRAMS_SQL, [text_id])
        self._conn.execute(constants.DELETE_TEXT_HAS_NGRAMS_SQL, [text_id])
        self._conn.commit()

    def diff (self, catalogue, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        symmetric difference in n-grams between the labelled sets of
        texts in `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = list(self._set_labels(catalogue))
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_DIFF_SQL.format(label_placeholders,
                                                 label_placeholders)
        parameters = labels + labels
        self._logger.info('Running diff query')
        self._logger.debug('Query: {}\nLabels: {}'.format(query, labels))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def diff_asymmetric (self, catalogue, prime_label, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        difference in n-grams between the labelled sets of texts in
        `catalogue`, limited to those texts labelled with
        `prime_label`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param prime_label: label to limit results to
        :type prime_label: `str`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = list(self._set_labels(catalogue))
        labels.remove(prime_label)
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_DIFF_ASYMMETRIC_SQL.format(label_placeholders)
        parameters = [prime_label, prime_label] + labels
        self._logger.info('Running asymmetric diff query')
        self._logger.debug('Query: {}\nLabels: {}\nPrime label: {}'.format(
            query, labels, prime_label))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def diff_supplied (self, catalogue, supplied, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        difference in n-grams between the labelled sets of texts in
        `catalogue`, limited to those results present in `supplied`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param supplied: CSV results used to limit query
        :type supplied: file-like object
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = list(self._set_labels(catalogue))
        supplied_ngrams, supplied_labels = self._process_supplied_results(
            supplied)
        labels = [label for label in labels if label not in supplied_labels]
        label_placeholders = self._get_placeholders(labels)
        all_labels = labels + supplied_labels
        all_label_placeholders = self._get_placeholders(all_labels)
        self._add_temporary_ngrams(supplied_ngrams)
        query = constants.SELECT_DIFF_SUPPLIED_SQL.format(
            all_label_placeholders, label_placeholders)
        parameters = all_labels + labels
        self._logger.info('Running diff query with supplied results')
        self._logger.debug('Query: {}\nLabels: {}\nSub-labels: {}'.format(
            query, all_labels, labels))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def _drop_indices (self):
        """Drops the database indices relating to n-grams."""
        self._logger.info('Dropping database indices')
        self._conn.execute(constants.DROP_TEXTNGRAM_INDEX_SQL)
        self._logger.info('Finished dropping database indices')

    @staticmethod
    def _get_intersection_subquery (labels):
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
    def _get_placeholders (items):
        """Returns a string of placeholders, one for each item in
        `items`.

        :param items: items to create placeholders for
        :type items: `list`
        :rtype: `str`

        """
        return ('?,' * len(items)).strip(',')

    def _get_text_id (self, text):
        """Returns the database ID of the Text record for `text`.

        This may require creating such a record.

        If `text`\'s checksum does not match an existing record's
        checksum, the record's checksum is updated and all associated
        TextNGram and TextHasNGram records are deleted.

        :param text: text to add a record for
        :type text: `.Text`
        :rtype: `int`

        """
        filename = text.get_filename()
        text_record = self._conn.execute(constants.SELECT_TEXT_SQL,
                                         [filename]).fetchone()
        if text_record is None:
            text_id = self._add_text_record(text)
        else:
            text_id = text_record['id']
            if text_record['checksum'] != text.get_checksum():
                self._logger.info('Text {} has changed since it was added to '
                                  'the database'.format(filename))
                self._update_text_record(text, text_id)
                self._logger.info('Deleting potentially out-of-date n-grams')
                self._delete_text_ngrams(text_id)
        return text_id

    def _has_ngrams (self, text_id, size):
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

    def _initialise_database (self):
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

    def intersection (self, catalogue, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        intersection in n-grams of the labelled sets of texts in
        `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = self._sort_labels(self._set_labels(catalogue))
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

    def intersection_supplied (self, catalogue, supplied, output_fh):
        """Returns `output_fh` populated with CSV results giving the
        intersection in n-grams between the labelled sets of texts in
        `catalogue`, limited to those results present in `supplied`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param supplied: CSV results used to limit query
        :type supplied: file-like object
        :param output_fh: object to output results to
        :type output_fh: file-like object
        :rtype: file-like object

        """
        labels = self._sort_labels(self._set_labels(catalogue))
        supplied_ngrams, supplied_labels = self._process_supplied_results(
            supplied)
        labels = [label for label in labels if label not in supplied_labels]
        all_labels = labels + supplied_labels
        all_label_placeholders = self._get_placeholders(all_labels)
        self._add_temporary_ngrams(supplied_ngrams)
        subquery = self._get_intersection_subquery(labels)
        query = constants.SELECT_INTERSECT_SUPPLIED_SQL.format(
            all_label_placeholders, subquery)
        parameters = all_labels + labels
        self._logger.info('Running intersection query with supplied results')
        self._logger.debug('Query: {}\nLabels: {}\nSub-labels: {}'.format(
            query, all_labels, labels))
        self._log_query_plan(query, parameters)
        cursor = self._conn.execute(query, parameters)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, output_fh)

    def _log_query_plan (self, query, parameters):
        cursor = self._conn.execute('EXPLAIN QUERY PLAN ' + query, parameters)
        query_plan = 'Query plan:\n'
        for row in cursor.fetchall():
            query_plan += '|'.join([str(value) for value in row]) + '\n'
        self._logger.debug(query_plan)

    def _process_supplied_results (self, input_csv):
        """Returns the unique n-grams and labels used in `input_csv`.

        :param input_csv: query results in CSV format
        :type input_csv: file-like object
        :rtype: `tuple` of `list` of `str`

        """
        self._logger.info('Processing supplied results')
        reader = csv.DictReader(input_csv)
        ngrams = set()
        labels = set()
        for row in reader:
            ngrams.add(row[constants.NGRAM_FIELDNAME])
            labels.add(row[constants.LABEL_FIELDNAME])
        return list(ngrams), list(labels)

    def search (self, catalogue, ngrams, output_fh):
        self._set_labels(catalogue)
        self._add_temporary_ngrams(ngrams)
        query = constants.SELECT_SEARCH_SQL
        self._logger.info('Running search query')
        self._logger.debug('Query: {}\nN-grams: {}'.format(
            query, ', '.join(ngrams)))
        self._log_query_plan(query, [])
        cursor = self._conn.execute(query)
        return self._csv(cursor, constants.SEARCH_FIELDNAMES, output_fh)

    def _set_labels (self, catalogue):
        """Returns a dictionary of the unique labels in `catalogue` and the
        number of their associated texts, and sets the record of each
        Text to the corresponding label.

        Texts that do not have a label specified are set to the empty
        string.

        Token counts are included in the results to allow for
        semi-accurate sorting based on corpora size.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :rtype: `dict`

        """
        self._conn.execute(constants.UPDATE_LABELS_SQL, [''])
        labels = {}
        for filename, label in catalogue.items():
            self._conn.execute(constants.UPDATE_LABEL_SQL, [label, filename])
            cursor = self._conn.execute(constants.SELECT_TEXT_TOKEN_COUNT_SQL,
                                        [filename])
            token_count = cursor.fetchone()['token_count']
            labels[label] = labels.get(label, 0) + token_count
        self._conn.commit()
        return labels

    @staticmethod
    def _sort_labels (label_data):
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

    def _update_text_record (self, text, text_id):
        """Updates the record with `text_id` with `text`\'s checksum and
        token count.

        :param text: text to update from
        :type text: `Text`
        :param text_id: database ID of Text record
        :type text_id: `int`

        """
        checksum = text.get_checksum()
        token_count = len(text.get_tokens())
        self._conn.execute(constants.UPDATE_TEXT_SQL,
                           [checksum, token_count, text_id])
        self._conn.commit()

    def validate (self, corpus, catalogue):
        """Returns True if all of the files labelled in `catalogue`
        are up-to-date in the database.

        :param corpus: corpus of texts
        :type corpus: `Corpus`
        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :rtype: `bool`

        """
        is_valid = True
        for filename in catalogue:
            try:
                checksum = corpus.get_text(filename).get_checksum()
            except FileNotFoundError:
                self._logger.error('Catalogue references {} that does not '
                                   'exist in the corpus'.format(filename))
                raise
            row = self._conn.execute(constants.SELECT_TEXT_SQL,
                                     [filename]).fetchone()
            if row is None:
                is_valid = False
                self._logger.warn('No record (or n-grams) exists for {} in '
                                     'the database'.format(filename))
            elif row['checksum'] != checksum:
                is_valid = False
                self._logger.warn('{} has changed since its n-grams were '
                                     'added to the database'.format(filename))
        return is_valid
