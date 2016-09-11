"""Module containing constants."""

TEI_SOURCE_CBETA_2011 = 'cbeta-2011'
TEI_SOURCE_CBETA_GITHUB = 'cbeta-github'
TEI_SOURCE_CHOICES = [TEI_SOURCE_CBETA_2011, TEI_SOURCE_CBETA_GITHUB]

TOKENIZER_CHOICE_CBETA = 'cbeta'
TOKENIZER_CHOICE_PAGEL = 'pagel'
TOKENIZER_CHOICES = [TOKENIZER_CHOICE_CBETA, TOKENIZER_CHOICE_PAGEL]
# For the CBETA (Chinese) tokenizer, a token is either a workaround
# (anything in square brackets, as a whole), or a single word
# character. Tokens are grouped together (when constituted into
# n-grams) by an empty string.
TOKENIZER_PATTERN_CBETA = r'\[[^]]*\]|\w'
TOKENIZER_JOINER_CBETA = ''
# For the Pagel (Tibetan) tokenizer, a token is a continuous set of
# word (plus some punctuation) characters. Tokens are grouped together
# (when constituted into n-grams) by a space.
TOKENIZER_PATTERN_PAGEL = r"[\w'\-+?~]+"
TOKENIZER_JOINER_PAGEL = ' '
TOKENIZERS = {
    TOKENIZER_CHOICE_CBETA: [TOKENIZER_PATTERN_CBETA, TOKENIZER_JOINER_CBETA],
    TOKENIZER_CHOICE_PAGEL: [TOKENIZER_PATTERN_PAGEL, TOKENIZER_JOINER_PAGEL],
}

BASE_WITNESS = 'base'
BASE_WITNESS_ID = ''
# XML namespaces.
NAMESPACES = {'tei': 'http://www.tei-c.org/ns/1.0',
              'xml': 'http://www.w3.org/XML/1998/namespace'}
XML = '{{{}}}'.format(NAMESPACES['xml'])

# Sequencer scoring values.
IDENTICAL_CHARACTER_SCORE = 1
DIFFERENT_CHARACTER_SCORE = -1
OPEN_GAP_PENALTY = -0.5
EXTEND_GAP_PENALTY = -0.1
# The threshold is the ratio between the alignment score and the
# length of the text being aligned below which the alignment is used
# as is, rather than further expanded.
SCORE_THRESHOLD = 0.75

# CSV field names.
COUNT_FIELDNAME = 'count'
COUNT_TOKENS_FIELDNAME = 'matching tokens'
LABEL_FIELDNAME = 'label'
NAME_FIELDNAME = 'text name'
NGRAM_FIELDNAME = 'ngram'
NGRAMS_FIELDNAME = 'ngrams'
NUMBER_FIELDNAME = 'number'
PERCENTAGE_FIELDNAME = 'percentage'
SIGLA_FIELDNAME = 'sigla'
SIGLUM_FIELDNAME = 'siglum'
SIZE_FIELDNAME = 'size'
TOTAL_NGRAMS_FIELDNAME = 'total ngrams'
TOTAL_TOKENS_FIELDNAME = 'total tokens'
UNIQUE_NGRAMS_FIELDNAME = 'unique ngrams'

QUERY_FIELDNAMES = [NGRAM_FIELDNAME, SIZE_FIELDNAME, NAME_FIELDNAME,
                    SIGLUM_FIELDNAME, COUNT_FIELDNAME, LABEL_FIELDNAME]
COUNTS_FIELDNAMES = [NAME_FIELDNAME, SIGLUM_FIELDNAME, SIZE_FIELDNAME,
                     UNIQUE_NGRAMS_FIELDNAME, TOTAL_NGRAMS_FIELDNAME,
                     TOTAL_TOKENS_FIELDNAME, LABEL_FIELDNAME]
SEARCH_FIELDNAMES = [NAME_FIELDNAME, SIGLUM_FIELDNAME, COUNT_FIELDNAME,
                     LABEL_FIELDNAME, NGRAMS_FIELDNAME, NUMBER_FIELDNAME]
STATISTICS_FIELDNAMES = [NAME_FIELDNAME, SIGLUM_FIELDNAME,
                         COUNT_TOKENS_FIELDNAME, TOTAL_TOKENS_FIELDNAME,
                         PERCENTAGE_FIELDNAME, LABEL_FIELDNAME]

# Command-line documentation strings.
ENCODING_EPILOG = '''\
    Due to encoding issues, you may need to set the environment
    variable PYTHONIOENCODING to "utf-8".'''

ALIGN_DESCRIPTION = '''\
    Generates an HTML report giving tables showing aligned sequences
    of text between each text within each label and all of the texts
    in the other labels, within a set of results. This functionality
    is only appropriate for intersect results.'''
ALIGN_EPILOG = ENCODING_EPILOG + '''\
    \n\nThis function requires the Biopython suite of software to be
    installed. It is extremely slow and resource hungry when the
    overlap between two texts is very great.'''
ALIGN_HELP = 'Show aligned sets of matches between two texts side by side.'
ALIGN_MINIMUM_SIZE_HELP = 'Minimum size of n-gram to base sequences around.'
ALIGN_OUTPUT_HELP = 'Directory to output alignment files to.'

ASYMMETRIC_HELP = 'Label of sub-corpus to restrict results to.'

CATALOGUE_CATALOGUE_HELP = 'Path to catalogue file.'
CATALOGUE_DESCRIPTION = 'Generate a catalogue file.'
CATALOGUE_EPILOG = '''\
    This command is just a convenience for generating a base catalogue
    file to then be customised manually.'''
CATALOGUE_HELP = 'Generate a catalogue file.'
CATALOGUE_LABEL_HELP = 'Label to use for all texts.'

COUNTS_DESCRIPTION = 'List counts of n-grams in each labelled text.'
COUNTS_EPILOG = ENCODING_EPILOG
COUNTS_HELP = 'List counts of n-grams in each labelled text.'

DB_CORPUS_HELP = 'Path to corpus.'
DB_DATABASE_HELP = 'Path to database file.'
DB_MEMORY_HELP = '''\
    Use RAM for temporary database storage.

    This may cause an out of memory error, in which case run the
    command without this switch.'''
DB_RAM_HELP = 'Number of gigabytes of RAM to use.'
DB_TOKENIZER_HELP = '''\
    Type of tokenizer to use. The "cbeta" tokenizer is suitable for
    the Chinese CBETA texts (tokens are single characters or
    workaround clusters within square brackets). The "pagel" tokenizer
    is for use with the transliterated Tibetan corpus (tokens are sets
    of word characters plus some punctuation used to transliterate
    characters).'''

DIFF_DESCRIPTION = '''\
    List n-grams unique to each sub-corpus (as defined by the labels
    in the specified catalogue file).'''
DIFF_EPILOG = '''\
    Many of the n-grams that are distinct to each sub-corpus are
    uninteresting - if a 2-gram is distinct, then so is every gram
    larger than 2 that contains that 2-gram. Therefore the results
    output by this command are filtered to keep only the most
    distinctive n-grams, according to the following rules (which apply
    within the context of a given witness):

    * If an n-gram is not composed of any (n-1)-grams found in the
      results, it is kept.

    * If both of the (n-1)-grams that comprise an n-gram are found in
      the results, that n-gram is kept.

    * Otherwise, the n-gram is removed from the results.

    examples:

      Make a diff query against a CBETA corpus.
        tacl diff cbeta2-10.db corpus/cbeta/ dhr-vs-rest.txt > output.csv

      Make an asymmetrical diff query against a CBETA corpus.
        tacl diff -a Dhr cbeta2-10.db corpus/cbeta/ dhr-vs-rest.txt > output.csv

      Make a diff query against a Pagel corpus.
        tacl diff -t pagel pagel1-7.db corpus/pagel/ by-author.txt > output.csv

''' + ENCODING_EPILOG
DIFF_HELP = 'List n-grams unique to each sub-corpus.'

HIGHLIGHT_BASE_NAME_HELP = 'Name of text to display.'
HIGHLIGHT_BASE_SIGLUM_HELP = 'Siglum of text to display.'
HIGHLIGHT_DESCRIPTION = '''\
    Output an HTML document showing a text with supplied n-grams visually
    highlighted.'''
HIGHLIGHT_EPILOG = '''\

    There are two possible outputs available, depending on whether the
    -n or -r option is specified.

    If n-grams are supplied via the -n/--ngrams option, the resulting
    HTML shows the specified witness text with those n-grams
    highlighted. Any n-grams that are specified via the
    -m/--minus-ngrams option will have had its constituent tokens
    unhighlighted.

    If results are supplied via the -r/--results option, the resulting
    HTML contains an interactive heatmap of the results, allowing the
    user to select which witness' matches should be highlighted in the
    text. Multiple selections are possible, and the colour of the
    highlight of a token reflects how many witnesses have matches
    containing that token.

    examples:

      tacl highlight -r intersect.csv corpus/stripped/ T0001 元 > heatmap.html

      tacl highlight -n author_markers.csv corpus/stripped/ T0001 元 > highlight.html'''
HIGHLIGHT_HELP = 'Output a text with its matches visually highlighted.'
HIGHLIGHT_MINUS_NGRAMS_HELP = '''\
    Path to file containing n-grams (one per line) to remove
    highlighting from. This applies only when -n is used.'''
HIGHLIGHT_NGRAMS_HELP = '''\
    Path to file containing n-grams (one per line) to highlight.'''
HIGHLIGHT_RESULTS_HELP = 'Path to CSV results; creates heatmap highlighting'


INTERSECT_DESCRIPTION = '''\
    List n-grams common to all sub-corpora (as defined by the labels
    in the specified catalogue file).'''
INTERSECT_EPILOG = '''\
    examples:

      Make an intersect query against a CBETA corpus.
        tacl intersect cbeta2-10.db corpus/cbeta/ dhr-vs-rest.txt > output.csv

      Make an intersect query against a Pagel corpus.
        tacl intersect -t pagel pagel1-7.db corpus/pagel/ by-author.txt > output.csv

''' + ENCODING_EPILOG
INTERSECT_HELP = 'List n-grams common to all sub-corpora.'

NGRAMS_CATALOGUE_HELP = '''\
    Path to a catalogue file used to restrict which texts in the
    corpus are added'''
NGRAMS_DESCRIPTION = 'Generate n-grams from a corpus.'
NGRAMS_EPILOG = '''\
    This command can be safely interrupted and subsequently rerun;
    texts that have already had their n-grams added will be skipped.

    If new texts need to be added after a database was generated, this
    command can be run again. However, the speed at which n-grams from
    these new texts are added will be much less than to a new
    database, due to the existing indices.

    If a text has changed since a database was generated, this command
    will not update the database. In this case, generate a new
    database or manipulate the existing dataase directly to remove the
    text and its associated n-grams.

    examples:

      Create a database of 2 to 10-grams from a CBETA corpus.
        tacl ngrams cbeta2-10.db corpus/cbeta/ 2 10

      Create a database of 1 to 7-grams from a Pagel corpus.
        tacl ngrams pagel1-7.db corpus/pagel/ 1 7

      Create a database of 1 to 7-grams from a subset of the CBETA corpus.
        tacl ngrams -c dhr-texts.txt cbeta-dhr1-7.db corpus/cbeta/ 1 7

'''
NGRAMS_HELP = 'Generate n-grams from a corpus.'
NGRAMS_MAXIMUM_HELP = 'Maximum size of n-gram to generate (integer).'
NGRAMS_MINIMUM_HELP = 'Minimum size of n-gram to generate (integer).'

PREPARE_DESCRIPTION = '''\
    Convert CBETA TEI XML files (which may have multiple files per
    text) into XML suitable for processing via the tacl strip
    command.'''
PREPARE_EPILOG = '''\
    The TEI source options are:

    * {}: the CBETA TEI files as found on their 2011 DVD release

    * {}: the CBETA TEI files as distruted on their GitHub repository
      at https://github.com/cbeta-org/xml-p5.git'''.format(
          TEI_SOURCE_CBETA_2011, TEI_SOURCE_CBETA_GITHUB)

PREPARE_HELP = '''\
    Convert CBETA TEI XML files into an XML form suitable for
    stripping.'''
PREPARE_INPUT_HELP = 'Directory containing XML files to prepare.'
PREPARE_OUTPUT_HELP = 'Directory to output prepared files to.'
PREPARE_SOURCE_HELP = 'Source of TEI files'

RESULTS_CATALOGUE_HELP = '''\
    Path to the catalogue file used to generate the results'''
RESULTS_DESCRIPTION = '''\
    Modify a query results file by adding, removing or otherwise
    manipulating result rows. Outputs the new set of results.'''
RESULTS_EXTEND_HELP = '''\
    Extend the results to list the highest size grams that also count
    as matches, going beyond the maximum size recorded in the
    database. This has no effect if the results contain only 1-grams.'''
RESULTS_EPILOG = '''\
    If more than one modifier is specified, they are applied in the
    following order: --extend, --reduce, --reciprocal, --zero-fill,
    --ngrams, --min/max-texts, --min/max-size, --min/max-count,
    --min/max-count-text, --remove, --sort.

    It is important to be careful with the use of --reduce. Coupled
    with --max-size, many results may be discarded without trace
    (since the reduce occurs first). Note too that performing "reduce"
    on a set of results more than once will make the results
    inaccurate!

    --extend applies before --reduce because it may generate results
    that are also amenable to reduction.

    --extend applies before --remove because it depends on there being
    at least two labels in the results in order to give correct
    results.

    --min-count and --max-count set the range within which the total
    count of each n-gram, across all texts, must fall. For each text,
    its count is taken as the highest count among its witnesses.

    --min-texts and --max-texts count texts rather than witnesses.

    If both --min-count-text and --max-count-text are specified, only
    those n-grams are kept that have at least one witness whose count
    falls within that range.

    Since this command always outputs a valid results file, its output
    can be used as input for a subsequent tacl results command. To
    chain commands together without creating an intermediate file,
    pipe the commands together and use - instead of a filename, as:

        tacl results --recriprocal results.csv | tacl results --reduce -

    examples:

      Extend CBETA results and set a minimum total count.
        tacl results -e corpus/cbeta/ --min-count 9 output.csv > mod-output.csv

      Zero-fill CBETA results.
        tacl results -c dhr-vs-rest.txt -z corpus/cbeta/ output.csv > mod-output.csv

      Reduce Pagel results.
        tacl results --reduce -t pagel output.csv > mod-output.csv

''' + ENCODING_EPILOG
RESULTS_HELP = 'Modify a query results file.'
RESULTS_MINIMUM_COUNT_HELP = 'Minimum total count per n-gram to include.'
RESULTS_MINIMUM_COUNT_TEXT_HELP = '''\
    Minimum count per n-gram per text to include; if a single witness
    meets this criterion for an n-gram, all instances of that n-gram
    are kept.'''
RESULTS_MAXIMUM_COUNT_HELP = 'Maximum total count per n-gram to include.'
RESULTS_MAXIMUM_COUNT_TEXT_HELP = '''\
    Maximum count per n-gram per text to include; if a single witness
    meets this criterion for an n-gram, all instances of that n-gram
    are kept.'''
RESULTS_MINIMUM_SIZE_HELP = 'Minimum size of n-grams to include.'
RESULTS_MAXIMUM_SIZE_HELP = 'Maximum size of n-grams to include.'
RESULTS_MINIMUM_TEXT_HELP = 'Minimum count of texts containing n-gram to include.'
RESULTS_MAXIMUM_TEXT_HELP = 'Maximum count of texts containing n-gram to include.'
RESULTS_NGRAMS_HELP = 'Path to file containing n-grams (one per line) to exclude.'
RESULTS_RECIPROCAL_HELP = '''\
    Remove n-grams that are not attested by at least one text in each
    labelled set of texts. This can be useful after reducing a set of
    intersection results.'''
RESULTS_REDUCE_HELP = 'Remove n-grams that are contained in larger n-grams.'
RESULTS_REMOVE_HELP = 'Remove labelled results.'
RESULTS_RESULTS_HELP = 'Path to CSV results; use - for stdin.'
RESULTS_SORT_HELP = 'Sort the results.'
RESULTS_ZERO_FILL_HELP = '''\
    Add rows with a count of 0 for each n-gram in each witness of a
    text that has at least one witness bearing that n-gram. The
    catalogue used to generate the results must also be specified with
    the -c option.'''

SEARCH_DESCRIPTION = '''\
    List texts containing at least one of the supplied n-grams, along
    with a total count of how many occurrences of the n-grams are
    present in each text, and the number of n-grams that match in each
    text.

    Specifying a catalogue file will not restrict the search to only
    those labelled texts, but rather adds the labels to any
    appropriate texts in the results.'''
SEARCH_HELP = 'List texts containing at least one of the supplied n-grams.'
SEARCH_NGRAMS_HELP = '''\
    Path to file containing list of n-grams to search for, with one
    n-gram per line.'''

STATISTICS_DESCRIPTION = '''\
    Generate summary statistics for a set of results. This gives, for
    each witness, the total number of tokens and the count of matching
    tokens, and derived from these the percentage of the witness that
    is encompassed by the matches.'''
STATISTICS_HELP = 'Generate summary statistics for a set of results.'
STATISTICS_RESULTS_HELP = 'Path to CSV results.'

STRIP_DESCRIPTION = '''\
    Preprocess a corpus by stripping unwanted material from each
    text.'''
STRIP_EPILOG = '''\
    The CBETA texts are in TEI XML that needs to have the markup and
    metadata removed. If the TEI specifies textual variants, plain
    text versions based on these are also created.'''
STRIP_HELP = 'Generate texts for use with TACL from a corpus of TEI XML.'
STRIP_INPUT_HELP = 'Directory containing files to strip.'
STRIP_OUTPUT_HELP = 'Directory to output stripped files to.'

SUPPLIED_DIFF_DESCRIPTION = '''\
    List n-grams unique to each set of results (as defined by the
    specified results files).'''
SUPPLIED_DIFF_HELP = 'List n-grams unique to each results file.'
SUPPLIED_EPILOG = '''\
    The number of labels supplied must match the number of results
    files. The first label is assigned to all results in the first
    results file, the second label to all results in the second
    results file, etc. The labels specified in the results files are
    replaced with the supplied labels in the output.'''
SUPPLIED_DIFF_EPILOG = SUPPLIED_EPILOG.format('sdiff')
SUPPLIED_INTERSECT_EPILOG = SUPPLIED_EPILOG.format('sintersect')
SUPPLIED_INTERSECT_DESCRIPTION = '''\
    List n-grams common to all sets of results (as defined by the
    specified results files).'''
SUPPLIED_INTERSECT_HELP = 'List n-grams common to all results files.'
SUPPLIED_LABELS_HELP = 'Labels to be assigned in order to the supplied results.'
SUPPLIED_RESULTS_HELP = 'Paths to results files to be used in the query.'

TACL_DESCRIPTION = 'Analyse the text of corpora in various simple ways.'

TACL_HELPER_DESCRIPTION = '''\
    Perform helpful but non-essential tacl-related functions.'''
TACL_HELPER_AGAINST_DESCRIPTION = '''\
    Generate a script to compare each text of a corpus against all the
    texts in another corpus.'''
TACL_HELPER_AGAINST_HELP = '''\
    Generate a script to compare each text of a corpus against all the
    texts in another corpus.'''
TACL_HELPER_AGAINST_A_HELP = '''\
    File containing text names to compare (one per line).'''
TACL_HELPER_AGAINST_B_HELP = '''\
    File containing corpus text names to be compared against (one per
    line).'''
TACL_HELPER_COLLAPSE_DESCRIPTION = '''
    Collapse result rows for multiple witnesses having the same count
    for an n-gram. Instead of the "siglum" column, all of the
    witnesses (per text) with the same n-gram count are listed, space
    separated, in the "sigla" column.'''
TACL_HELPER_COLLAPSE_HELP = 'Collapse result rows for multiple witnesses having the same count for an n-gram'
TACL_HELPER_IN_DESCRIPTION = '''\
    Generate a script to compare each text of a corpus with all the
    other texts of that corpus.'''
TACL_HELPER_IN_HELP = '''\
    Generate a script to compare each text of a corpus with all the
    other texts of that corpus.'''
TACL_HELPER_IN_TEXTS_HELP = '''\
    File containing text names to examine (one per line).'''
TACL_HELPER_LABEL_COUNT_DESCRIPTION = '''\
    Output the supplied results with an additional column, "label
    count", giving the total count for each n-gram within the
    label. The maximum count across all of a text's witnesses is used
    in the sum.'''
TACL_HELPER_LABEL_COUNT_HELP = '''\
    Add a "label count" column to results giving the count per
    label.'''
TACL_HELPER_OUTPUT = 'Output directory for script and catalogue files.'
TACL_HELPER_RESULTS_HELP = 'Path to CSV results'
TACL_HELPER_VALIDATE_CATALOGUE_DESCRIPTION = ''
TACL_HELPER_VALIDATE_CATALOGUE_HELP = ''

VERBOSE_HELP = '''\
    Display debug information; multiple -v options increase the verbosity.'''


# Error messages.
CATALOGUE_TEXT_RELABELLED_ERROR = 'Catalogue file labels "{}" more than once'
INSUFFICIENT_LABELS_QUERY_ERROR = 'Not running query with less than two defined labels'
LABEL_NOT_IN_CATALOGUE_ERROR = 'Supplied label is not present in the supplied catalogue'
SUPPLIED_ARGS_LENGTH_MISMATCH_ERROR = 'The number of labels supplied does not match the number of results files.'


# SQL statements.
ANALYSE_SQL = 'ANALYZE {}'
CREATE_INDEX_INPUT_RESULTS_SQL = 'CREATE INDEX IF NOT EXISTS ' \
        'temp.InputResultsLabel ON InputResults (ngram)'
CREATE_INDEX_TEXT_SQL = 'CREATE INDEX IF NOT EXISTS TextIndexLabel ' \
    'ON Text (label)'
CREATE_INDEX_TEXTHASNGRAM_SQL = 'CREATE UNIQUE INDEX IF NOT EXISTS ' \
    'TextHasNGramIndex ON TextHasNGram (text, size)'
CREATE_INDEX_TEXTNGRAM_SQL = 'CREATE INDEX IF NOT EXISTS ' \
    'TextNGramIndexTextNGram ON TextNGram (text, ngram)'
CREATE_TABLE_TEXT_SQL = 'CREATE TABLE IF NOT EXISTS Text (' \
    'id INTEGER PRIMARY KEY ASC, ' \
    'name TEXT NOT NULL, ' \
    'siglum TEXT NOT NULL, ' \
    'checksum TEXT NOT NULL, ' \
    'token_count INTEGER NOT NULL, ' \
    'label TEXT NOT NULL, ' \
    'UNIQUE (name, siglum))'
CREATE_TABLE_TEXTNGRAM_SQL = 'CREATE TABLE IF NOT EXISTS TextNGram (' \
    'text INTEGER NOT NULL REFERENCES Text (id), ' \
    'ngram TEXT NOT NULL, ' \
    'size INTEGER NOT NULL, ' \
    'count INTEGER NOT NULL)'
CREATE_TABLE_TEXTHASNGRAM_SQL = 'CREATE TABLE IF NOT EXISTS TextHasNGram (' \
    'text INTEGER NOT NULL REFERENCES Text (id), ' \
    'size INTEGER NOT NULL, ' \
    'count INTEGER NOT NULL)'
CREATE_TEMPORARY_NGRAMS_TABLE_SQL = 'CREATE TEMPORARY TABLE InputNGram (' \
    'ngram TEXT)'
CREATE_TEMPORARY_RESULTS_TABLE_SQL = 'CREATE TEMPORARY TABLE InputResults (' \
    'ngram TEXT NOT NULL, ' \
    'size INTEGER NOT NULL, ' \
    'name TEXT NOT NULL, ' \
    'siglum TEXT NOT NULL, ' \
    'count INTEGER NOT NULL, ' \
    'label TEXT NOT NULL)'
DELETE_TEXT_HAS_NGRAMS_SQL = 'DELETE FROM TextHasNGram WHERE text = ?'
DELETE_TEXT_NGRAMS_SQL = 'DELETE FROM TextNGram WHERE text = ?'
DROP_TEMPORARY_NGRAMS_TABLE_SQL = 'DROP TABLE IF EXISTS InputNGram'
DROP_TEMPORARY_RESULTS_TABLE_SQL = 'DROP TABLE IF EXISTS InputResults'
DROP_TEXTNGRAM_INDEX_SQL = 'DROP INDEX IF EXISTS TextNGramIndexTextNGram'
INSERT_NGRAM_SQL = 'INSERT INTO TextNGram (text, ngram, size, count) ' \
    'VALUES (?, ?, ?, ?)'
INSERT_TEXT_HAS_NGRAM_SQL = 'INSERT INTO TextHasNGram (text, size, count) ' \
    'VALUES (?, ?, ?)'
INSERT_TEXT_SQL = 'INSERT INTO Text ' \
    '(name, siglum, checksum, token_count, label) ' \
    'VALUES (?, ?, ?, ?, ?)'
INSERT_TEMPORARY_NGRAM_SQL = 'INSERT INTO temp.InputNGram (ngram) VALUES (?)'
INSERT_TEMPORARY_RESULTS_SQL = 'INSERT INTO temp.InputResults ' \
    '(ngram, size, name, siglum, count, label) ' \
    'VALUES (?, ?, ?, ?, ?, ?)'
PRAGMA_CACHE_SIZE_SQL = 'PRAGMA cache_size={}'
PRAGMA_COUNT_CHANGES_SQL = 'PRAGMA count_changes=OFF'
PRAGMA_FOREIGN_KEYS_SQL = 'PRAGMA foreign_keys=ON'
PRAGMA_LOCKING_MODE_SQL = 'PRAGMA locking_mode=EXCLUSIVE'
PRAGMA_SYNCHRONOUS_SQL = 'PRAGMA synchronous=OFF'
PRAGMA_TEMP_STORE_SQL = 'PRAGMA temp_store=MEMORY'
SELECT_COUNTS_SQL = 'SELECT Text.name AS "text name", Text.siglum, ' \
    'TextHasNGram.size, TextHasNGram.count AS "unique ngrams", ' \
    'Text.token_count + 1 - TextHasNGram.size AS "total ngrams", ' \
    'Text.token_count AS "total tokens", Text.label ' \
    'FROM Text, TextHasNGram ' \
    'WHERE Text.id = TextHasNGram.text AND Text.label IN ({}) ' \
    'ORDER BY Text.name, TextHasNGram.size'
SELECT_DIFF_ASYMMETRIC_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'Text.name AS "text name", Text.siglum, TextNGram.count, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label = ? AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (' \
    'SELECT TextNGram.ngram FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label = ? ' \
    'EXCEPT ' \
    'SELECT TextNGram.ngram FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}))'
SELECT_DIFF_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'Text.name AS "text name", Text.siglum, TextNGram.count, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (' \
    'SELECT TextNGram.ngram FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}) ' \
    'GROUP BY TextNGram.ngram HAVING COUNT(DISTINCT Text.label) = 1)'
SELECT_DIFF_SUPPLIED_SQL = '''SELECT ngram, size, name AS "text name",
siglum, count, label
FROM temp.InputResults
WHERE ngram IN (
SELECT ngram FROM temp.InputResults
GROUP BY ngram HAVING COUNT(DISTINCT label) = 1)'''
SELECT_HAS_NGRAMS_SQL = 'SELECT text FROM TextHasNGram ' \
    'WHERE text = ? AND size = ?'
SELECT_INTERSECT_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'Text.name AS "text name", Text.siglum, TextNGram.count, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN ({})'
SELECT_INTERSECT_SUB_EXTRA_SQL = ' AND TextNGram.ngram IN ({})'
SELECT_INTERSECT_SUB_SQL = 'SELECT TextNGram.ngram ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label = ? AND Text.id = TextNGram.text'
SELECT_INTERSECT_SUPPLIED_SQL = '''SELECT ngram, size, name AS "text name",
siglum, count, label
FROM temp.InputResults
WHERE ngram IN (
SELECT ngram FROM temp.InputResults
GROUP BY ngram HAVING COUNT(DISTINCT label) = ?)'''
SELECT_SEARCH_SQL = 'SELECT Text.name AS "text name", Text.siglum, ' \
    'SUM(TextNGram.count) AS count, ' \
    "Text.label, group_concat(TextNGram.ngram, ', ') AS ngrams, " \
    'count(TextNGram.ngram) AS number ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) ' \
    'GROUP BY TextNGram.text'
SELECT_TEXT_TOKEN_COUNT_SQL = 'SELECT Text.token_count ' \
    'FROM Text WHERE Text.name = ?'
SELECT_TEXT_SQL = 'SELECT id, checksum FROM Text WHERE name = ? AND siglum = ?'
UPDATE_LABEL_SQL = 'UPDATE Text SET label = ? WHERE name = ?'
UPDATE_LABELS_SQL = 'UPDATE Text SET label = ?'
UPDATE_TEXT_SQL = 'UPDATE Text SET checksum = ?, token_count = ? WHERE id = ?'
VACUUM_SQL = 'VACUUM'
