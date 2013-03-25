"""Module containing constants."""

# A token is either a workaround (anything in square brackets, as
# a whole), or a single word character.
TOKENIZER_PATTERN = r'\[[^]]*\]|\w'

# CSV field names.
COUNT_FIELDNAME = 'count'
FILENAME_FIELDNAME = 'filename'
LABEL_FIELDNAME = 'label'
NGRAM_FIELDNAME = 'ngram'
SIZE_FIELDNAME = 'size'
TOTAL_FIELDNAME = 'total'

QUERY_FIELDNAMES = [NGRAM_FIELDNAME, SIZE_FIELDNAME, FILENAME_FIELDNAME,
                    COUNT_FIELDNAME, LABEL_FIELDNAME]
COUNTS_FIELDNAMES = [FILENAME_FIELDNAME, SIZE_FIELDNAME, TOTAL_FIELDNAME,
                     COUNT_FIELDNAME, LABEL_FIELDNAME]

# Command-line documentation strings.
ENCODING_EPILOG = '''\
    Due to encoding issues, you may need to set the environment
    variable PYTHONIOENCODING to "utf-8".'''

ASYMMETRIC_HELP = 'label of sub-corpus to restrict results to'

CATALOGUE_CATALOGUE_HELP = 'path to catalogue file'
CATALOGUE_DESCRIPTION = 'Generate a catalogue file.'
CATALOGUE_EPILOG = '''\
    This command is just a convenience for generating a base catalogue
    file to then be customised manually.'''
CATALOGUE_HELP = 'generate a catalogue file'
CATALOGUE_LABEL_HELP = 'label to use for all texts'

COUNTS_DESCRIPTION = 'List counts of n-grams in each labelled text.'
COUNTS_EPILOG = ENCODING_EPILOG
COUNTS_HELP = 'list counts of n-grams in each labelled text'

DB_CORPUS_HELP = 'path to corpus'
DB_DATABASE_HELP = 'path to database file'
DB_MEMORY_HELP = 'use RAM for temporary database storage'
DB_RAM_HELP = 'number of gigabytes of RAM to use'

DIFF_DESCRIPTION = 'List n-grams unique to each sub-corpus.'
DIFF_EPILOG = ENCODING_EPILOG
DIFF_HELP = 'list n-grams unique to each sub-corpus'

INPUT_RESULTS_HELP = 'path to results file to restrict query to'

INTERSECT_DESCRIPTION = 'List n-grams common to all sub-corpora.'
INTERSECT_EPILOG = ENCODING_EPILOG
INTERSECT_HELP = 'list n-grams common to all sub-corpora'

NGRAMS_DESCRIPTION = 'Generate n-grams from a corpus.'
NGRAMS_HELP = 'generate n-grams from a corpus'
NGRAMS_INDEX_HELP = 'drop indices before adding n-grams'
NGRAMS_MAXIMUM_HELP = 'maximum size of n-gram to generate (integer)'
NGRAMS_MINIMUM_HELP = 'minimum size of n-gram to generate (integer)'

REPORT_DESCRIPTION = '''\
    Modify a query results file by removing certain results. Outputs
    the new set of results.'''
REPORT_EPILOG = '''\
    If more than one modifier is specified, they are applied in the
    following order: --reduce, --reciprocal, --min/max-texts,
    --min/max-size, --min/max-count, --remove.

    Since this command always outputs a valid results file, its output
    can be used as input for a subsequent tacl report command. To
    chain commands together without creating an intermediate file,
    pipe the commands together and use - instead of a filename, as:

        tacl report --recriprocal results.csv | tacl report --reduce -

    {}'''.format(ENCODING_EPILOG)
REPORT_HELP = 'modify a query results file'
REPORT_MINIMUM_COUNT_HELP = 'minimum total count of n-gram to include'
REPORT_MAXIMUM_COUNT_HELP = 'maximum total count of n-gram to include'
REPORT_MINIMUM_SIZE_HELP = 'minimum size of n-grams to include'
REPORT_MAXIMUM_SIZE_HELP = 'maximum size of n-grams to include'
REPORT_MINIMUM_TEXT_HELP = 'minimum count of texts containing n-gram to include'
REPORT_MAXIMUM_TEXT_HELP = 'maximum count of texts containing n-gram to include'
REPORT_RECIPROCAL_HELP = '''\
    remove n-grams that are not attested by at least one text in each
    labelled set of texts'''
REPORT_REDUCE_HELP = 'remove n-grams that are contained in larger n-grams'
REPORT_REMOVE_HELP = 'remove labelled results'
REPORT_RESULTS_HELP = 'path to CSV results; use - for stdin'

STRIP_DESCRIPTION = '''\
    Preprocess a corpus by stripping unwanted material from each
    text.'''
STRIP_EPILOG = '''\
    The CBETA texts are in TEI XML that needs to have the markup and
    metadata removed.'''
STRIP_HELP = 'preprocess a corpus for use with TACL'
STRIP_INPUT_HELP = 'directory containing files to strip'
STRIP_OUTPUT_HELP = 'directory to output stripped files to'

TACL_DESCRIPTION = 'Analyse the text of corpora in various simple ways.'

TACL_HELPER_DESCRIPTION = '''\
    Perform helpful but non-essential tacl-related functions.'''
TACL_HELPER_AGAINST_DESCRIPTION = '''\
    Generate a script to compare each text of a corpus against all the
    texts in another corpus.'''
TACL_HELPER_AGAINST_HELP = '''\
    generate a script to compare each text of a corpus against all the
    texts in another corpus'''
TACL_HELPER_AGAINST_A_HELP = '''\
    file containing text names to compare (one per line)'''
TACL_HELPER_AGAINST_B_HELP = '''\
    file containing corpus text names to be compared against (one per
    line)'''
TACL_HELPER_IN_DESCRIPTION = '''\
    Generate a script to compare each text of a corpus with all the
    other texts of that corpus.'''
TACL_HELPER_IN_HELP = '''\
    generate a script to compare each text of a corpus with all the
    other texts of that corpus'''
TACL_HELPER_IN_TEXTS_HELP = '''\
    file containing text names to examine (one per line)'''
TACL_HELPER_OUTPUT = 'output directory for script and catalogue files'

VERBOSE_HELP = '''\
    display debug information; multiple -v options increase the verbosity'''


# SQL statements.
ANALYSE_SQL = 'ANALYZE {}'
CREATE_INDEX_TEXT_SQL = 'CREATE INDEX IF NOT EXISTS TextIndexLabel ' \
    'ON Text (label)'
CREATE_INDEX_TEXTHASNGRAM_SQL = 'CREATE UNIQUE INDEX IF NOT EXISTS ' \
    'TextHasNGramIndex ON TextHasNGram (text, size)'
CREATE_INDEX_TEXTNGRAM_SQL = 'CREATE INDEX IF NOT EXISTS ' \
    'TextNGramIndexTextNGram ON TextNGram (text, ngram)'
CREATE_TABLE_TEXT_SQL = 'CREATE TABLE IF NOT EXISTS Text (' \
    'id INTEGER PRIMARY KEY ASC, ' \
    'filename TEXT UNIQUE NOT NULL, ' \
    'checksum TEXT NOT NULL, ' \
    'label TEXT NOT NULL)'
CREATE_TABLE_TEXTNGRAM_SQL = 'CREATE TABLE IF NOT EXISTS TextNGram (' \
    'text INTEGER NOT NULL REFERENCES Text (id), ' \
    'ngram TEXT NOT NULL, ' \
    'size INTEGER NOT NULL, ' \
    'count INTEGER NOT NULL)'
CREATE_TABLE_TEXTHASNGRAM_SQL = 'CREATE TABLE IF NOT EXISTS TextHasNGram (' \
    'text INTEGER NOT NULL REFERENCES Text (id), ' \
    'size INTEGER NOT NULL)'
CREATE_TEMPORARY_TABLE_SQL = 'CREATE TEMPORARY TABLE InputNGram (ngram Text)'
DELETE_TEXT_HAS_NGRAMS_SQL = 'DELETE FROM TextHasNGram WHERE text = ?'
DELETE_TEXT_NGRAMS_SQL = 'DELETE FROM TextNGram WHERE text = ?'
DROP_TEXTNGRAM_INDEX_SQL = 'DROP INDEX IF EXISTS TextNGramIndexTextNGram'
INSERT_NGRAM_SQL = 'INSERT INTO TextNGram (text, ngram, size, count) ' \
    'VALUES (?, ?, ?, ?)'
INSERT_TEXT_HAS_NGRAM_SQL = 'INSERT INTO TextHasNGram (text, size) ' \
    'VALUES (?, ?)'
INSERT_TEXT_SQL = 'INSERT INTO Text (filename, checksum, label) ' \
    'VALUES (?, ?, ?)'
INSERT_TEMPORARY_NGRAM_SQL = 'INSERT INTO temp.InputNGram (ngram) VALUES (?)'
PRAGMA_CACHE_SIZE_SQL = 'PRAGMA cache_size={}'
PRAGMA_COUNT_CHANGES_SQL = 'PRAGMA count_changes=OFF'
PRAGMA_FOREIGN_KEYS_SQL = 'PRAGMA foreign_keys=ON'
PRAGMA_LOCKING_MODE_SQL = 'PRAGMA locking_mode=EXCLUSIVE'
PRAGMA_SYNCHRONOUS_SQL = 'PRAGMA synchronous=OFF'
PRAGMA_TEMP_STORE_SQL = 'PRAGMA temp_store=MEMORY'
SELECT_COUNTS_SQL = 'SELECT Text.filename, TextNGram.size, ' \
    'COUNT(TextNGram.ngram) as total, SUM(TextNGram.count) as count, ' \
    'Text.label FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}) ' \
    'GROUP BY TextNGram.text, TextNGram.size ' \
    'ORDER BY Text.filename, TextNGram.size'
SELECT_DIFF_ASYMMETRIC_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.label IN (?) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (' \
    'SELECT TextNGram.ngram FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}) ' \
    'GROUP BY TextNGram.ngram HAVING COUNT(DISTINCT Text.label) = 1)'
SELECT_DIFF_SQL = 'SELECT TextNGram.ngram, TextNGram.size, TextNGram.count, ' \
    'Text.filename, Text.label ' \
    'FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (' \
    'SELECT TextNGram.ngram FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}) ' \
    'GROUP BY TextNGram.ngram HAVING COUNT(DISTINCT Text.label) = 1)'
SELECT_DIFF_SUPPLIED_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) ' \
    'AND NOT EXISTS (' \
    'SELECT tn.ngram FROM Text t CROSS JOIN TextNGram tn ' \
    'WHERE t.id = tn.text AND t.label IN ({}) AND tn.ngram = TextNGram.ngram)'
SELECT_HAS_NGRAMS_SQL = 'SELECT * FROM TextHasNGram ' \
    'WHERE text = ? AND size = ?'
SELECT_INTERSECT_SQL = 'SELECT TextNgram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN ({})'
SELECT_INTERSECT_SUB_SQL = 'SELECT TextNGram.ngram ' \
    'FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.label = ? AND Text.id = TextNGram.text'
SELECT_INTERSECT_SUPPLIED_SQL = 'SELECT TextNgram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text CROSS JOIN TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) ' \
    'AND TextNGram.ngram IN ({})'
SELECT_TEXT_SQL = 'SELECT id, checksum FROM Text WHERE filename = ?'
UPDATE_LABEL_SQL = 'UPDATE Text SET label = ? WHERE filename = ?'
UPDATE_LABELS_SQL = 'UPDATE Text SET label = ?'
UPDATE_TEXT_SQL = 'UPDATE Text SET checksum = ? WHERE id = ?'
VACUUM_SQL = 'VACUUM'
