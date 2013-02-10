import logging
import os.path
import sqlite3


class DBManager (object):

    def __init__ (self, db_name):
        if db_name == ':memory:':
            self._db_name = db_name
        else:
            self._db_name = os.path.abspath(db_name)
        self._conn = sqlite3.connect(self._db_name)
        self._conn.row_factory = sqlite3.Row
        self._c = self._conn.cursor()
        self._c.execute('PRAGMA cache_size=2000000')
        self._c.execute('PRAGMA count_changes=OFF')
        self._c.execute('PRAGMA foreign_keys=ON')
        self._c.execute('PRAGMA locking_mode=EXCLUSIVE')
        self._c.execute('PRAGMA synchronous=OFF')
        #self._c.execute('PRAGMA temp_store=MEMORY')
        self.init_db()

    def add_indices (self):
        logging.info('Adding database indices')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextIndex
                           ON Text (id, label)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextNGramIndexSize
                           ON TextNGram (size, ngram)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextNGramIndexNGram
                           ON TextNGram (ngram)''')
        logging.info('Indices added')

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
        self._c.execute('''INSERT INTO TextNGram (text, ngram, size, count)
                           VALUES (?, ?, ?, ?)''',
                        (text_id, ngram, size, count))

    def add_text (self, filename, checksum, corpus_label=''):
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
        if row is None:
            logging.info('No existing record for text %s; adding one' %
                          filename)
            self._c.execute('''INSERT INTO Text (filename, checksum, label)
                               VALUES (?, ?, ?)''',
                            (filename, checksum, corpus_label))
            text_id = self._c.lastrowid
        else:
            logging.info('Reusing existing record for text %s' % filename)
            # Check that the checksum matches.
            text_id = row['id']
            if row['checksum'] != checksum:
                logging.info('Text %s changed since added to database; updating checksum and deleting n-grams' % filename)
                self._c.execute('DELETE FROM TextNGram WHERE text=?',
                                (text_id,))
                self._c.execute('DELETE FROM TextHasNGram WHERE text=?',
                                (text_id,))
            # Rather than also check whether the corpus needs to be
            # updated, and potentially do two updates, just always
            # update the checksum and corpus at once.
            self._c.execute('UPDATE Text SET checksum=?, label=? WHERE id=?',
                            (checksum, corpus_label, text_id))
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

    def commit (self):
        self._conn.commit()

    def drop_indices (self):
        logging.info('Dropping database indices')
        self._c.execute('DROP INDEX IF EXISTS TextNGramIndex')

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

    def diff (self, labels, minimum, maximum, occurrences):
        logging.info('Running diff query')
        label_params = ('?,' * len(labels)).strip(',')
        query = '''SELECT TextNGram.ngram, SUM(TextNGram.count) freq_count,
                       Text.label
                   FROM TextNGram, Text
                   WHERE Text.label IN (%s)
                       AND TextNGram.text = Text.id
                       AND TextNGram.size BETWEEN ? AND ?
                       AND NOT EXISTS
                           (SELECT tn.ngram
                            FROM TextNGram tn, Text t
                            WHERE t.label != Text.label
                                AND t.label != ''
                                AND tn.text = t.id
                                AND TextNGram.ngram = tn.ngram)
                   GROUP BY TextNGram.size, TextNGram.ngram
                   HAVING freq_count >= ?
                   ''' % label_params
        logging.debug('Query:\n{query}\nLabels: {labels}'.format(
                query=query, labels=labels))
        return self._c.execute(query, labels + [minimum, maximum, occurrences])

    def diff_asymmetric (self, label, minimum, maximum, occurrences):
        logging.info('Running asymmetric diff query')
        query = '''SELECT TextNGram.ngram, SUM(TextNGram.count) freq_count,
                       Text.label
                   FROM TextNGram, Text
                   WHERE Text.label = ?
                       AND TextNGram.text = Text.id
                       AND TextNGram.size BETWEEN ? AND ?
                       AND NOT EXISTS
                           (SELECT tn.ngram
                            FROM TextNGram tn, Text t
                            WHERE t.label != ?
                                AND t.label != ''
                                AND tn.text = t.id
                                AND TextNGram.ngram = tn.ngram)
                   GROUP BY TextNGram.size, TextNGram.ngram
                   HAVING freq_count >= ?
                   '''
        logging.debug('Query:\n{query}\nLabel: {label}'.format(
                query=query, label=label))
        return self._c.execute(query, [label, minimum, maximum, label,
                                       occurrences])

    def diff_asymmetric_text (self, label, minimum, maximum):
        logging.info('Running asymmetric diff text query')
        query = '''SELECT TextNGram.ngram, TextNGram.count freq_count,
                       Text.filename, Text.label
                   FROM TextNGram, Text
                   WHERE Text.label = ?
                       AND TextNGram.text = Text.id
                       AND TextNGram.size BETWEEN ? AND ?
                       AND NOT EXISTS
                           (SELECT tn.ngram
                            FROM TextNGram tn, Text t
                            WHERE t.label != ?
                                AND t.label != ''
                                AND tn.text = t.id
                                AND TextNGram.ngram = tn.ngram)
                   ORDER BY TextNGram.size, TextNGram.ngram
                   '''
        logging.debug('Query:\n{query}\nLabel: {label}'.format(
                query=query, label=label))
        return self._c.execute(query, [label, minimum, maximum, label])

    def diff_text (self, labels, minimum, maximum):
        logging.info('Running diff text query')
        label_params = ('?,' * len(labels)).strip(',')
        query = '''SELECT TextNGram.ngram, TextNGram.count freq_count,
                       Text.filename, Text.label
                   FROM TextNGram, Text
                   WHERE Text.label IN (%s)
                       AND TextNGram.size BETWEEN ? AND ?
                       AND TextNGram.text = Text.id
                       AND NOT EXISTS
                           (SELECT tn.ngram
                            FROM TextNGram tn, Text t
                            WHERE t.label != Text.label
                                AND t.label != ''
                                AND tn.text = t.id
                                AND tn.ngram = TextNGram.ngram)
                   ORDER BY TextNGram.size, TextNGram.ngram
                   ''' % label_params
        logging.debug('Query:\n{query}\nLabels: {labels}'.format(
                query=query, labels=labels))
        return self._c.execute(query, labels + [minimum, maximum])

    def intersection (self, labels, minimum, maximum, occurrences):
        logging.info('Running intersection query')
        label_params = ('?,' * len(labels)).strip(',')
        subquery = '''AND EXISTS (SELECT t.label
                                  FROM Text t, TextNGram tn
                                  WHERE t.label = ?
                                      AND t.id = tn.text
                                      AND tn.ngram = TextNGram.ngram) '''
        query = '''
            SELECT TextNGram.ngram, SUM(TextNGram.count) freq_count,
                'ALL' label
            FROM Text, TextNGram
            WHERE Text.label IN (%s)
                AND Text.id = TextNGram.text
                AND TextNGram.size BETWEEN ? AND ?
                %s
            GROUP BY TextNGram.size, TextNGram.ngram
            HAVING freq_count <= ?
            ''' % (label_params, subquery * len(labels))
        logging.debug('Query:\n{query}\nLabels: {labels}'.format(
                query=query, labels=labels))
        return self._c.execute(query, labels + [minimum, maximum] + labels +
                               [occurrences])

    def intersection_text (self, labels, minimum, maximum):
        logging.info('Running intersection text query')
        label_params = ('?,' * len(labels)).strip(',')
        subquery = '''AND EXISTS (SELECT t.label
                                  FROM Text t, TextNGram tn
                                  WHERE t.label = ?
                                      AND tn.text = t.id
                                      AND tn.ngram = TextNGram.ngram) '''
        query = '''
            SELECT TextNgram.ngram, TextNGram.count freq_count, Text.filename,
                Text.label
            FROM TextNGram, Text
            WHERE Text.label IN (%s)
                AND Text.id = TextNGram.text
                AND TextNGram.size BETWEEN ? AND ?
                %s
            ORDER BY TextNGram.size, TextNGram.ngram
            ''' % (label_params, subquery * len(labels))
        logging.debug('Query:\n{query}\nLabels: {labels}'.format(
                query=query, labels=labels))
        return self._c.execute(query, labels + [minimum, maximum] + labels)

    def vacuum (self):
        logging.info('Vacuuming the database')
        self._c.execute('VACUUM')
        logging.info('Vacuuming complete')
