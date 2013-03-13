"""Module containing the DBManager class."""

import logging
import os.path
import sqlite3


class DBManager (object):

    def __init__ (self, db_name, use_memory=True, ram=0):
        if db_name == ':memory:':
            self._db_name = db_name
        else:
            self._db_name = os.path.abspath(db_name)
        self._conn = sqlite3.connect(self._db_name)
        self._conn.row_factory = sqlite3.Row
        self._c = self._conn.cursor()
        if use_memory:
            self._c.execute('PRAGMA temp_store=MEMORY')
        if ram:
            cache_size = ram * -1000000
            self._c.execute('PRAGMA cache_size={}'.format(cache_size))
        self._c.execute('PRAGMA count_changes=OFF')
        self._c.execute('PRAGMA foreign_keys=ON')
        self._c.execute('PRAGMA locking_mode=EXCLUSIVE')
        self._c.execute('PRAGMA synchronous=OFF')
        self._parameters = []
        self.init_db()

    def add_indices (self):
        logging.info('Adding database indices')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextNGramIndexText
                           ON TextNGram (text)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextNGramIndexNGram
                           ON TextNGram (ngram)''')
        logging.info('Indices added')

    def add_label (self, filename, label, checksum):
        """Adds `label` to the record for `filename`."""
        self._c.execute('SELECT id, checksum FROM Text WHERE filename=?',
                        (filename,))
        row = self._c.fetchone()
        if row is None:
            logging.warning('No database record for text {}; text will not be included in results'.format(filename))
        else:
            if row['checksum'] != checksum:
                logging.warning('Text {} has changed since its n-grams were added to the database'.format(filename))
            self._c.execute('UPDATE Text SET label=? WHERE id=?',
                            (label, row['id']))

    def add_ngram (self, text_id, ngram, size, count):
        """Adds a TextNGram row specifying the `count` of `ngram`
        appearing in `text_id`.

        :param text_id: database ID of the Text
        :type text_id: `int`
        :param ngram: n-gram to be added
        :type ngram: `unicode`
        :param size: size of `ngram`
        :type size: `int`
        :param count: number of occurrences of `ngram` in the Text
        :type count: `int`

        """
        # Add a new TextNGram record.
        self._parameters.append((text_id, ngram, size, count))

    def add_ngrams (self):
        self._conn.executemany(
            '''INSERT INTO TextNGram (text, ngram, size, count)
               VALUES (?, ?, ?, ?)''', self._parameters)
        self._conn.commit()
        self._parameters = []

    def add_text (self, filename, checksum):
        """Returns the database ID of the Text record for the text at
        `text_path`.

        This may require creating such a record.

        If `checksum` does not match an existing record's checksum,
        the record's checksum is updated and all related TextNGram
        records are deleted.

        """
        # Reuse an existing Text record, or create a new one.
        self._c.execute('SELECT id, checksum FROM Text WHERE filename=?',
                        (filename,))
        row = self._c.fetchone()
        label = ''
        if row is None:
            logging.info('No existing record for text {}; adding one'.format(
                    filename))
            self._c.execute('''INSERT INTO Text (filename, checksum, label)
                               VALUES (?, ?, ?)''',
                            (filename, checksum, label))
            text_id = self._c.lastrowid
        else:
            logging.info('Reusing existing record for text {}'.format(filename))
            # Check that the checksum matches.
            text_id = row['id']
            if row['checksum'] != checksum:
                logging.info('Text {} changed since added to database; updating checksum and deleting n-grams'.format(filename))
                self._c.execute('DELETE FROM TextNGram WHERE text=?',
                                (text_id,))
                self._c.execute('DELETE FROM TextHasNGram WHERE text=?',
                                (text_id,))
            self._c.execute('UPDATE Text SET checksum=?, label=? WHERE id=?',
                            (checksum, label, text_id))
        self._conn.commit()
        return text_id

    def add_text_ngram (self, text_id, size):
        """Adds a TextHasNGram row for `text_id` and `size`."""
        self._c.execute('INSERT INTO TextHasNGram (text, size) VALUES (?, ?)',
                        (text_id, size))

    def analyse (self, table=''):
        logging.info('Starting analysis of database')
        self._c.execute('ANALYZE %s' % table)
        logging.info('Analysis of database complete')

    def clear_labels (self):
        """Clears the labels from all texts."""
        self._c.execute("UPDATE Text SET label=''")

    def counts (self, labels):
        """Returns cursor of n-gram totals by size and text."""
        logging.info('Running counts query')
        label_params = ('?,' * len(labels)).strip(',')
        query = '''SELECT Text.filename, TextNGram.size,
                       COUNT(TextNGram.ngram) as total,
                       SUM(TextNGram.count) as count, Text.label
                   FROM Text CROSS JOIN TextNGram
                   WHERE Text.id = TextNGram.text
                       AND Text.label IN ({})
                   GROUP BY TextNGram.text, TextNGram.size
                   ORDER BY Text.filename, TextNGram.size'''.format(
            label_params)
        logging.debug('Query:\n{}\nLabels: {}'.format(query, labels))
        return self._c.execute(query, labels)

    def diff (self, labels):
        logging.info('Running diff text query')
        label_params = ('?,' * len(labels)).strip(',')
        query = '''SELECT TextNGram.ngram, TextNGram.size, TextNGram.count,
                       Text.filename, Text.label
                   FROM TextNGram, Text
                   WHERE Text.label IN ({})
                       AND TextNGram.text = Text.id
                       AND TextNGram.ngram IN (
                           SELECT TextNGram.ngram
                           FROM Text CROSS JOIN TextNGram
                           WHERE Text.id = TextNGram.text
                               AND Text.label IN ({})
                           GROUP BY TextNGram.ngram
                           HAVING COUNT(DISTINCT Text.label) = 1)'''.format(
            label_params, label_params)
        logging.debug('Query:\n{}\nLabels: {}'.format(query, labels))
        return self._c.execute(query, labels + labels)

    def drop_indices (self):
        logging.info('Dropping database indices')
        self._c.execute('DROP INDEX IF EXISTS TextNGramIndexNGram')
        self._c.execute('DROP INDEX IF EXISTS TextNGramIndexText')

    def has_ngrams (self, text_id, size):
        """Returns True if there the Text with `text_id` has n-grams
        of size `size`.

        :param text_id: database ID of the Text
        :type text_id: `int`
        :param size: size of the NGram
        :type size: `int`
        :rtype: `bool`

        """
        self._c.execute('''SELECT * FROM TextHasNGram
                           WHERE text = ? AND size = ?''', (text_id, size))
        if self._c.fetchone() is not None:
            return True
        return False

    def init_db (self):
        """Creates the database.

        Will not create tables that already exist.

        """
        self._c.execute('''CREATE TABLE IF NOT EXISTS Text (
                               id INTEGER PRIMARY KEY ASC,
                               filename TEXT UNIQUE NOT NULL,
                               checksum TEXT NOT NULL,
                               label TEXT NOT NULL
                           )''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS TextNGram (
            text INTEGER NOT NULL REFERENCES Text (id),
            ngram TEXT NOT NULL,
            size INTEGER NOT NULL,
            count INTEGER NOT NULL
            )''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS TextHasNGram (
                               text INTEGER NOT NULL REFERENCES Text (id),
                               size INTEGER NOT NULL
                           )''')
        self._c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS TextHasNGramIndex
                           ON TextHasNGram (text, size)''')

    def intersection (self, labels):
        logging.info('Running intersection text query')
        number_labels = len(labels)
        label_params = ('?,' * number_labels).strip(',')
        subquery = '''SELECT TextNGram.ngram
                      FROM Text CROSS JOIN TextNGram
                      WHERE Text.label = ?
                          AND Text.id = TextNGram.text'''
        subqueries = ' INTERSECT '.join([subquery] * number_labels)
        query = '''SELECT TextNgram.ngram, TextNGram.size, TextNGram.count,
                       Text.filename, Text.label
                   FROM TextNGram, Text
                   WHERE Text.label IN ({})
                       AND Text.id = TextNGram.text
                       AND TextNGram.ngram IN ({})'''.format(
            label_params, subqueries)
        logging.debug('Query:\n{query}\nLabels: {labels}'.format(
                query=query, labels=labels))
        return self._c.execute(query, labels*2)

    def vacuum (self):
        logging.info('Vacuuming the database')
        self._c.execute('VACUUM')
        logging.info('Vacuuming complete')
