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
        self._c.execute('PRAGMA synchronous=0')
        self.init_db()

    def add_ngram (self, text_id, ngram, size, count):
        """Adds a TextNGram row specifying the `count` of `ngram`
        appearing in `text_id`.

        Also creates an NGram record if one does not already exist.

        :param text_id: database ID of the Text
        :type text_id: `int`
        :param ngram: n-gram to be added
        :type ngram: `unicode`
        :param size: size of `ngram`
        :type size: `int`
        :param count: number of occurrences of `ngram` in the Text
        :type count: `int`

        """
        # Reuse an existing NGram record, or create a new one.
        self._c.execute('SELECT id FROM NGram WHERE ngram=?', (ngram,))
        row = self._c.fetchone()
        if row is None:
            self._c.execute('INSERT INTO NGram (ngram, size) VALUES (?, ?)',
                            (ngram, size))
            ngram_id = self._c.lastrowid
        else:
            ngram_id = row['id']
        # Add a new TextNGram record.
        self._c.execute('''INSERT INTO TextNGram (text, ngram, count)
                           VALUES (?, ?, ?)''', (text_id, ngram_id, count))

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

    def commit (self):
        self._conn.commit()

    def has_ngrams (self, text_id, size):
        """Returns True if there is at least one TextNGram record
        linking `text_id` with an NGram of size `size`.

        :param text_id: database ID of the Text
        :type text_id: `int`
        :param size: size of the NGram
        :type size: `int`
        :rtype: `bool`

        """
        self._c.execute('''SELECT COUNT(*) FROM TextNGram, NGram
            WHERE text=? AND TextNGram.ngram=NGram.id AND NGram.size=?''',
                        (text_id, size))
        if self._c.fetchone()[0] > 0:
            return True
        return False

    def init_db (self):
        """Creates the database.

        Will not create tables and indices that already exist.

        """
        self._c = self._conn.cursor()
        self._c.execute('''CREATE TABLE IF NOT EXISTS Text (
                               id INTEGER PRIMARY KEY ASC,
                               filename TEXT UNIQUE NOT NULL,
                               checksum INTEGER NOT NULL,
                               label TEXT NOT NULL
                           )''')
        self._c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS TextIndexFilename
                           ON Text (filename)''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS TextIndexLabel
                           ON Text (label)''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS NGram (
                               id INTEGER PRIMARY KEY ASC,
                               ngram TEXT UNIQUE NOT NULL,
                               size INTEGER NOT NULL
                           )''')
        self._c.execute('''CREATE INDEX IF NOT EXISTS NGramIndexSize
                           ON NGram (size)''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS TextNGram (
            text INTEGER NOT NULL REFERENCES Text (id),
            ngram INTEGER NOT NULL REFERENCES NGram (id),
            count INTEGER NOT NULL
            )''')
        self._c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS TextNGramIndex
                           ON TextNGram (text, ngram)''')

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
