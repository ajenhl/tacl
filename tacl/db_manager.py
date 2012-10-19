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
        self._c.execute('PRAGMA cache_size=10000')
        self._c.execute('PRAGMA count_changes=OFF')
        self._c.execute('PRAGMA locking_mode=EXCLUSIVE')
        self._c.execute('PRAGMA synchronous=OFF')
        self._c.execute('PRAGMA temp_store=MEMORY')
        self.init_db()

    def add_indices (self):
        logging.debug('Adding database indices')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextIndexLabel
                           ON Text (label)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS NGramIndexSize
                           ON NGram (size)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextNGramIndexText
                           ON TextNGram (text)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextNGramIndexNGram
                           ON TextNGram (ngram)''')
        self._c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS TextNGramIndex
                           ON TextNGram (text, ngram)''')

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
        self._c.execute('''INSERT INTO TextNGram
                               (text, ngram, chars, size, count)
                           VALUES (?, '', ?, ?, ?)''',
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
            logging.debug('No existing record for text %s; adding one' %
                          filename)
            self._c.execute('''INSERT INTO Text (filename, checksum, label)
                               VALUES (?, ?, ?)''',
                            (filename, checksum, corpus_label))
            text_id = self._c.lastrowid
        else:
            logging.debug('Reusing existing record for text %s' % filename)
            # Check that the checksum matches.
            text_id = row['id']
            if row['checksum'] != checksum:
                logging.debug('Text %s changed since added to database; updating checksum and deleting NGram references' % filename)
                self._c.execute('DELETE FROM TextNGram WHERE text=?',
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

    def commit (self):
        self._conn.commit()

    def drop_indices (self):
        logging.debug('Dropping database indices')
        self._c.execute('DROP INDEX IF EXISTS TextIndexLabel')
        self._c.execute('DROP INDEX IF EXISTS NGramIndexSize')
        self._c.execute('DROP INDEX IF EXISTS TextNGramIndexNgram')
        self._c.execute('DROP INDEX IF EXISTS TextNGramIndexText')
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
                               checksum INTEGER NOT NULL,
                               label TEXT NOT NULL
                           )''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS NGram (
                               id INTEGER PRIMARY KEY ASC,
                               ngram TEXT UNIQUE NOT NULL,
                               size INTEGER NOT NULL
                           )''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS TextNGram (
            text INTEGER NOT NULL REFERENCES Text (id),
            ngram INTEGER REFERENCES NGram (id),
            chars TEXT,
            size INTEGER,
            count INTEGER NOT NULL
            )''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS TextHasNGram (
                               text INTEGER NOT NULL REFERENCES Text (id),
                               size INTEGER NOT NULL
                           )''')
        self._c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS TextHasNGramIndex
                           ON TextHasNGram (text, size)''')

    def normalise (self):
        """Normalises the data in the database."""
        logging.debug('Normalising the data')
        # First make use of any existing NGram IDs in normalising
        # TextNGram, to avoid trying to create NGram rows that already
        # exist.
        self._normalise_text_ngram()
        # Create any NGram rows that are needed.
        query = "SELECT DISTINCT chars, size FROM TextNGram WHERE chars != ''"
        self._c.execute(query)
        row = self._c.fetchone()
        cursor = self._conn.cursor()
        while row is not None:
            query = 'INSERT INTO NGram (ngram, size) VALUES (?, ?)'
            cursor.execute(query, (row['chars'], row['size']))
            row = self._c.fetchone()
        # Repeat the normalisation of TextNGram, now that there are
        # NGram rows for the remaining unnomralised TextNGram rows.
        self._normalise_text_ngram()

    def _normalise_text_ngram (self):
        query = """UPDATE TextNGram SET ngram = (
                       SELECT NGram.id FROM NGram
                           WHERE NGram.ngram = TextNGram.chars)
                   WHERE chars != ''"""
        self._c.execute(query)
        query = "UPDATE TextNGram SET chars = '', size = '' WHERE ngram != ''"
        self._c.execute(query)

    def diff (self, labels, minimum, maximum, occurrences):
        label_params = ('?,' * len(labels)).strip(',')
        query = '''SELECT Ngram.ngram, SUM(count) count, Text.label
                   FROM NGram, TextNGram, Text
                   WHERE NGram.id = TextNGram.ngram
                       AND TextNGram.text = Text.id
                       AND Text.label IN (%s)
                       AND NGram.size BETWEEN ? AND ?
                       AND NOT EXISTS
                           (SELECT n.ngram FROM NGram n, TextNGram tn, Text t
                            WHERE n.id = NGram.id AND n.id = tn.ngram AND
                                tn.text = t.id AND t.label != Text.label
                                AND t.label != '')
                   GROUP BY NGram.ngram
                   HAVING SUM(count) >= ?
                   ORDER BY count DESC
                   ''' % label_params
        self._c.execute(query, labels + [minimum, maximum, occurrences])
        return self._c.fetchall()

    def diff_text (self, labels, minimum, maximum, occurrences):
        label_params = ('?,' * len(labels)).strip(',')
        query = '''SELECT Ngram.ngram, count, Text.filename, Text.label
                   FROM NGram, TextNGram, Text
                   WHERE NGram.id = TextNGram.ngram
                       AND TextNGram.text = Text.id
                       AND Text.label IN (%s)
                       AND NGram.size BETWEEN ? AND ?
                       AND NOT EXISTS
                           (SELECT n.ngram FROM NGram n, TextNGram tn, Text t
                            WHERE n.id = NGram.id AND n.id = tn.ngram AND
                                tn.text = t.id AND t.label != Text.label
                                AND t.label != '')
                       AND ? <=
                           (SELECT SUM(count) FROM NGram n, TextNGram tn, Text t
                            WHERE n.id = NGram.id AND n.id = tn.ngram AND
                                tn.text = t.id AND t.label IN (%s)
                            GROUP BY n.ngram)
                   ORDER BY NGram.ngram, count DESC
                   ''' % (label_params, label_params)
        self._c.execute(query, labels + [minimum, maximum, occurrences] +
                        labels)
        return self._c.fetchall()

    def intersection (self, labels, minimum, maximum, occurrences):
        subquery = '''AND EXISTS (SELECT Text.label
                                  FROM NGram n, TextNGram, Text
                                  WHERE n.id = NGram.id
                                      AND n.id = TextNGram.ngram
                                      AND TextNGram.text = Text.id
                                      AND Text.label = ?) '''
        query = '''
            SELECT Ngram.ngram, SUM(count) count, 'ALL' label
            FROM NGram, TextNGram, Text
            WHERE NGram.id = TextNGram.ngram
                AND TextNGram.text = Text.id
                AND Text.label != ''
                %s
                AND NGram.size BETWEEN ? AND ?
            GROUP BY NGram.ngram
            HAVING SUM(count) >= ?
            ORDER BY count DESC
            ''' % (subquery * len(labels))
        self._c.execute(query, labels + [minimum, maximum, occurrences])
        return self._c.fetchall()

    def intersection_text (self, labels, minimum, maximum, occurrences):
        label_params = ('?,' * len(labels)).strip(',')
        subquery = '''AND EXISTS (SELECT t.label
                                  FROM NGram n, TextNGram tn, Text t
                                  WHERE n.id = NGram.id
                                      AND n.id = tn.ngram
                                      AND tn.text = t.id
                                      AND t.label = ?) '''
        query = '''
            SELECT Ngram.ngram, count, Text.filename, Text.label
            FROM NGram, TextNGram, Text
            WHERE NGram.id = TextNGram.ngram
                AND TextNGram.text = Text.id
                AND Text.label != ''
                %s
                AND NGram.size BETWEEN ? AND ?
                AND ? <= (SELECT SUM(count) FROM NGram n, TextNGram tn, Text t
                          WHERE n.id = NGram.id AND n.id = tn.ngram AND
                              tn.text = t.id AND t.label IN (%s)
                          GROUP BY n.ngram)
            ORDER BY Ngram.ngram, count DESC
            ''' % (subquery * len(labels), label_params)
        self._c.execute(query, labels + [minimum, maximum, occurrences] +
                        labels)
        return self._c.fetchall()

    def vacuum (self):
        logging.debug('Vacuuming the database')
        self._c.execute('VACUUM')
