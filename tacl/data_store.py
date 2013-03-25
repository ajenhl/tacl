"""Module containing the DataStore class."""

import csv
import logging
import os.path
import sqlite3

from . import constants


class DataStore (object):

    def __init__ (self, db_name, use_memory=True, ram=0):
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
        logging.info('Adding database indices')
        self._conn.execute(constants.CREATE_INDEX_TEXTNGRAM_SQL)
        logging.info('Indices added')

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
        self._vacuum()

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
        logging.info('Adding n-grams ({} <= n <= {}) for {}'.format(
                minimum, maximum, text.get_filename()))
        for size, ngrams in text.get_ngrams(minimum, maximum):
            self._add_text_size_ngrams(text_id, size, ngrams)

    def _add_text_record (self, text):
        """Adds a Text record for `text`.

        :param text: text to add a record for
        :type text: `Text`

        """
        filename = text.get_filename()
        logging.info('Adding record for text {}'.format(filename))
        cursor = self._conn.execute(constants.INSERT_TEXT_SQL,
                                    [filename, text.get_checksum(), ''])
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
            logging.info('{}-grams are already in the database'.format(
                    size))
        else:
            logging.info('Adding {} unique {}-grams'.format(
                    len(ngrams), size))
            parameters = [[text_id, ngram, size, count]
                          for ngram, count in ngrams.items()]
            self._conn.execute(constants.INSERT_TEXT_HAS_NGRAM_SQL,
                               [text_id, size])
            self._conn.executemany(constants.INSERT_NGRAM_SQL, parameters)
            self._conn.commit()

    def _analyse (self, table=''):
        """Analyses the database, or `table` if it is supplied.

        :param table: optional name of table analyse
        :type table: `str`

        """
        logging.info('Starting analysis of database')
        self._conn.execute(constants.ANALYSE_SQL.format(table))
        logging.info('Analysis of database complete')

    def counts (self, catalogue, fh):
        """Returns `fh` populated with CSV results giving n-gram
        counts of the texts in `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param fh: object to output results to
        :type fh: file-like object
        :rtype: file-like object

        """
        labels = self._set_labels(catalogue)
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_COUNTS_SQL.format(label_placeholders)
        logging.info('Running counts query')
        logging.debug('Query: {}\nLabels: {}'.format(query, labels))
        cursor = self._conn.execute(query, labels)
        return self._csv(cursor, constants.COUNTS_FIELDNAMES, fh)

    def _csv (self, cursor, fieldnames, fh):
        """Writes the rows of `cursor` in CSV format to `fh` and
        returns it.

        :param cursor: database cursor containing data to be be output
        :type cursor: `sqlite3.Cursor`
        :param fieldnames: row headings
        :type fieldnames: `list`
        :param fh: file to write data to
        :type fh: file object
        :rtype: file object

        """
        logging.info('Finished query; outputting results in CSV format')
        writer = csv.writer(fh)
        writer.writerow(fieldnames)
        for row in cursor:
            writer.writerow([row[fieldname] for fieldname in fieldnames])
        logging.info('Finished outputting results')
        return fh

    def _delete_text_ngrams (self, text_id):
        """Deletes all n-grams associated with `text_id` from the data store.

        :param text_id: database ID of text
        :type text_id: `int`

        """
        self._conn.execute(constants.DELETE_TEXT_NGRAMS_SQL, [text_id])
        self._conn.execute(constants.DELETE_TEXT_HAS_NGRAMS_SQL, [text_id])
        self._conn.commit()

    def diff (self, catalogue, fh):
        """Returns `fh` populated with CSV results giving the
        symmetric difference in n-grams between the labelled sets of
        texts in `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param fh: object to output results to
        :type fh: file-like object
        :rtype: file-like object

        """
        labels = self._set_labels(catalogue)
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_DIFF_SQL.format(label_placeholders,
                                                 label_placeholders)
        logging.info('Running diff query')
        logging.debug('Query: {}\nLabels: {}'.format(query, labels))
        cursor = self._conn.execute(query, labels + labels)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, fh)

    def diff_asymmetric (self, catalogue, prime_label, fh):
        """Returns `fh` populated with CSV results giving the
        difference in n-grams between the labelled sets of texts in
        `catalogue`, limited to those texts labelled with
        `prime_label`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param prime_label: label to limit results to
        :type prime_label: `str`
        :param fh: object to output results to
        :type fh: file-like object
        :rtype: file-like object

        """
        labels = self._set_labels(catalogue)
        label_placeholders = self._get_placeholders(labels)
        query = constants.SELECT_DIFF_ASYMMETRIC_SQL.format(label_placeholders)
        logging.info('Running asymmetric diff query')
        logging.debug('Query: {}\nLabels: {}\nPrime label: {}'.format(
                query, labels, prime_label))
        cursor = self._conn.execute(query, [prime_label] + labels)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, fh)

    def diff_supplied (self, catalogue, supplied, fh):
        """Returns `fh` populated with CSV results giving the
        difference in n-grams between the labelled sets of texts in
        `catalogue`, limited to those results present in `supplied`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param supplied: CSV results used to limit query
        :type supplied: file-like object
        :param fh: object to output results to
        :type fh: file-like object
        :rtype: file-like object

        """
        labels = self._set_labels(catalogue)
        supplied_ngrams, supplied_labels = self._process_supplied_results(
            supplied)
        labels = [label for label in labels if label not in supplied_labels]
        label_placeholders = self._get_placeholders(labels)
        all_labels = labels + supplied_labels
        all_label_placeholders = self._get_placeholders(all_labels)
        self._add_temporary_ngrams(supplied_ngrams)
        query = constants.SELECT_DIFF_SUPPLIED_SQL.format(
            all_label_placeholders, label_placeholders)
        logging.info('Running diff query with supplied results')
        logging.debug('Query: {}\nLabels: {}\nSub-labels: {}'.format(
                query, all_labels, labels))
        cursor = self._conn.execute(query, all_labels + labels)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, fh)

    def _drop_indices (self):
        """Drops the database indices relating to n-grams."""
        logging.info('Dropping database indices')
        self._conn.execute(constants.DROP_TEXTNGRAM_INDEX_SQL)
        logging.info('Finished dropping database indices')

    def _get_placeholders (self, items):
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
                logging.info('Text {} has changed since it was added to the ' \
                                 'database'.format(filename))
                self._update_text_record(text, text_id)
                logging.info('Deleting potentially out-of-date n-grams')
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
        logging.info('Creating database schema, if necessary')
        self._conn.execute(constants.CREATE_TABLE_TEXT_SQL)
        self._conn.execute(constants.CREATE_TABLE_TEXTNGRAM_SQL)
        self._conn.execute(constants.CREATE_TABLE_TEXTHASNGRAM_SQL)
        self._conn.execute(constants.CREATE_INDEX_TEXTHASNGRAM_SQL)
        self._conn.execute(constants.CREATE_INDEX_TEXT_SQL)

    def intersection (self, catalogue, fh):
        """Returns `fh` populated with CSV results giving the
        intersection in n-grams of the labelled sets of texts in
        `catalogue`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param fh: object to output results to
        :type fh: file-like object
        :rtype: file-like object

        """
        labels = self._set_labels(catalogue)
        label_placeholders = self._get_placeholders(labels)
        subqueries = ' INTERSECT '.join([constants.SELECT_INTERSECT_SUB_SQL]
                                        * len(labels))
        query = constants.SELECT_INTERSECT_SQL.format(label_placeholders,
                                                      subqueries)
        logging.info('Running intersection query')
        logging.debug('Query: {}\nLabels: {}'.format(query, labels))
        cursor = self._conn.execute(query, labels * 2)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, fh)

    def intersection_supplied (self, catalogue, supplied, fh):
        """Returns `fh` populated with CSV results giving the
        intersection in n-grams between the labelled sets of texts in
        `catalogue`, limited to those results present in `supplied`.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :param supplied: CSV results used to limit query
        :type supplied: file-like object
        :param fh: object to output results to
        :type fh: file-like object
        :rtype: file-like object

        """
        labels = self._set_labels(catalogue)
        supplied_ngrams, supplied_labels = self._process_supplied_results(
            supplied)
        labels = [label for label in labels if label not in supplied_labels]
        all_labels = labels + supplied_labels
        all_label_placeholders = self._get_placeholders(all_labels)
        self._add_temporary_ngrams(supplied_ngrams)
        subqueries = ' INTERSECT '.join([constants.SELECT_INTERSECT_SUB_SQL]
                                        * len(labels))
        query = constants.SELECT_INTERSECT_SUPPLIED_SQL.format(
            all_label_placeholders, subqueries)
        logging.info('Running intersection query with supplied results')
        logging.debug('Query: {}\nLabels: {}\nSub-labels: {}'.format(
                query, all_labels, labels))
        cursor = self._conn.execute(query, all_labels + labels)
        return self._csv(cursor, constants.QUERY_FIELDNAMES, fh)

    def _process_supplied_results (self, input_csv):
        """Returns the unique n-grams and labels used in `input_csv`.

        :param input_csv: query results in CSV format
        :type input_csv: file-like object
        :rtype: `tuple` of `list` of `str`

        """
        logging.info('Processing supplied results')
        reader = csv.DictReader(input_csv)
        ngrams = set()
        labels = set()
        for row in reader:
            ngrams.add(row[constants.NGRAM_FIELDNAME])
            labels.add(row[constants.LABEL_FIELDNAME])
        return list(ngrams), list(labels)

    def _set_labels (self, catalogue):
        """Returns a list of the unique labels in `catalogue`, and
        sets the record of each Text to the corresponding label.

        Texts that do not have a label specified are set to the empty
        string.

        :param catalogue: catalogue matching filenames to labels
        :type catalogue: `Catalogue`
        :rtype: `list`

        """
        self._conn.execute(constants.UPDATE_LABELS_SQL, [''])
        labels = set()
        for filename, label in catalogue.items():
            self._conn.execute(constants.UPDATE_LABEL_SQL, [label, filename])
            labels.add(label)
        self._conn.commit()
        return list(labels)

    def _update_text_record (self, text, text_id):
        """Updates the record with `text_id` with `text`\'s checksum.

        :param text: text to update from
        :type text: `Text`
        :param text_id: database ID of Text record
        :type text_id: `int`

        """
        self._conn.execute(constants.UPDATE_TEXT_SQL,
                           [text.get_checksum(), text_id])
        self._conn.commit()

    def _vacuum (self):
        """Vacuums the database."""
        logging.info('Vacuuming the database')
        self._conn.execute(constants.VACUUM_SQL)
        logging.info('Vacuuming complete')

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
            except FileNotFoundError as err:
                logging.error('Catalogue references {} that does not exist in '
                              'the corpus'.format(filename))
                raise
            row = self._conn.execute(constants.SELECT_TEXT_SQL,
                                              [filename]).fetchone()
            if row is None:
                is_valid = False
                logging.warning('No record (or n-grams) exists for {} in the '
                                'database'.format(filename))
            elif row['checksum'] != checksum:
                is_valid = False
                logging.warning('{} has changed since its n-grams were added '
                                'to the database'.format(filename))
        return is_valid
