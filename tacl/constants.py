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
LABEL_COUNT_FIELDNAME = 'label count'
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
WORK_FIELDNAME = 'work'

QUERY_FIELDNAMES = [NGRAM_FIELDNAME, SIZE_FIELDNAME, WORK_FIELDNAME,
                    SIGLUM_FIELDNAME, COUNT_FIELDNAME, LABEL_FIELDNAME]
COUNTS_FIELDNAMES = [WORK_FIELDNAME, SIGLUM_FIELDNAME, SIZE_FIELDNAME,
                     UNIQUE_NGRAMS_FIELDNAME, TOTAL_NGRAMS_FIELDNAME,
                     TOTAL_TOKENS_FIELDNAME, LABEL_FIELDNAME]
SEARCH_FIELDNAMES = [WORK_FIELDNAME, SIGLUM_FIELDNAME, COUNT_FIELDNAME,
                     LABEL_FIELDNAME, NGRAMS_FIELDNAME, NUMBER_FIELDNAME]
STATISTICS_FIELDNAMES = [WORK_FIELDNAME, SIGLUM_FIELDNAME,
                         COUNT_TOKENS_FIELDNAME, TOTAL_TOKENS_FIELDNAME,
                         PERCENTAGE_FIELDNAME, LABEL_FIELDNAME]

# Command-line documentation strings.
ENCODING_EPILOG = '''\
    Due to encoding issues, you may need to set the environment
    variable PYTHONIOENCODING to "utf-8".'''

ALIGN_DESCRIPTION = '''\
    Generates an HTML report giving tables showing aligned sequences
    of text between each witness within each label and all of the
    witnesses in the other labels, within a set of results. This
    functionality is only appropriate for intersect results.'''
ALIGN_EPILOG = ENCODING_EPILOG + '''\
    \n\nThis function requires the Biopython suite of software to be
    installed. It is extremely slow and resource hungry when the
    overlap between two witnesses is very great.'''
ALIGN_HELP = 'Show aligned sets of matches between two witnesses side by side.'
ALIGN_MINIMUM_SIZE_HELP = 'Minimum size of n-gram to base sequences around.'
ALIGN_OUTPUT_HELP = 'Directory to output alignment files to.'

ASYMMETRIC_HELP = 'Label of sub-corpus to restrict results to.'

CATALOGUE_CATALOGUE_HELP = 'Path to catalogue file.'
CATALOGUE_DESCRIPTION = 'Generate a catalogue file.'
CATALOGUE_EPILOG = '''\
    This command is just a convenience for generating a base catalogue
    file to then be customised manually.'''
CATALOGUE_HELP = 'Generate a catalogue file.'
CATALOGUE_LABEL_HELP = 'Label to use for all works.'

COUNTS_DESCRIPTION = 'List counts of n-grams in each labelled witness.'
COUNTS_EPILOG = ENCODING_EPILOG
COUNTS_HELP = 'List counts of n-grams in each labelled witness.'

DB_CORPUS_HELP = 'Path to corpus.'
DB_DATABASE_HELP = 'Path to database file.'
DB_MEMORY_HELP = '''\
    Use RAM for temporary database storage.

    This may cause an out of memory error, in which case run the
    command without this switch.'''
DB_RAM_HELP = 'Number of gigabytes of RAM to use.'
DB_TOKENIZER_HELP = '''\
    Type of tokenizer to use. The "cbeta" tokenizer is suitable for
    the Chinese CBETA corpus (tokens are single characters or
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

HIGHLIGHT_BASE_NAME_HELP = 'Name of work to display.'
HIGHLIGHT_DESCRIPTION = '''\
    Output an HTML report for each witness to a work, showing the text
    of that witness with supplied n-grams visually highlighted.'''
HIGHLIGHT_EPILOG = '''\
    There are two possible outputs available, depending on whether the
    -n or -r option is specified.

    If n-grams are supplied via the -n/--ngrams option, the resulting
    HTML reports show the specified work's witness texts with those
    n-grams highlighted. Any n-grams that are specified via the
    -m/--minus-ngrams option will have had its constituent tokens
    unhighlighted. The -n/--ngrams option may be specified multiple
    times; each file's n-grams will be highlighted in a distinct
    colour. The -l/--labels option can be used with -n/--ngrams in
    order to provide labels for groups of n-grams. There must be as
    many instances of -l/--labels as there are of -n/--ngrams. The
    order of the labels matches the order of the n-grams files.

    If results are supplied via the -r/--results option, the resulting
    HTML reports contain an interactive heatmap of the results, allowing the
    user to select which witness' matches should be highlighted in the
    text. Multiple selections are possible, and the colour of the
    highlight of a token reflects how many witnesses have matches
    containing that token.

    examples:

      tacl highlight -r intersect.csv corpus/stripped/ T0001 report_dir

      tacl highlight -n author_markers.csv corpus/stripped/ T0001 report_dir

      tacl highlight -n Dhr_markers.csv -n ZQ_markers.csv corpus/stripped/ -l Dharmaraksa -l "Zhi Qian" T0474 report_dir'''
HIGHLIGHT_HELP = 'Output a witness with its matches visually highlighted.'
HIGHLIGHT_LABEL_HELP = '''\
    Label used to identify the n-grams from a file specified by
    -n/--ngrams. This option may be specified multiple times, and
    provided as many times as the -n/--ngrams option.'''
HIGHLIGHT_MINUS_NGRAMS_HELP = '''\
    Path to file containing n-grams (one per line) to remove
    highlighting from. This applies only when -n is used.'''
HIGHLIGHT_NGRAMS_HELP = '''\
    Path to file containing n-grams (one per line) to highlight. This
    option may be specified multiple times; the n-grams in each file
    will be displayed in a distinct colour.'''
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

JITC_DESCRIPTION = '''\
    Generate a report showing the amount of overlap between a set of
    works, ignoring those parts that overlap with works in a second
    set of works.'''
JITC_LABEL_HELP = 'Label of works to compare with each other'

NGRAMS_CATALOGUE_HELP = '''\
    Path to a catalogue file used to restrict which works in the
    corpus are added'''
NGRAMS_DESCRIPTION = 'Generate n-grams from a corpus.'
NGRAMS_EPILOG = '''\
    This command can be safely interrupted and subsequently rerun;
    witnesses that have already had their n-grams added will be skipped.

    If new witnesses need to be added after a database was generated,
    this command can be run again. However, the speed at which n-grams
    from these new witnesses are added will be much less than to a new
    database, due to the existing indices.

    If a witness has changed since a database was generated, this
    command will not update the database. In this case, generate a new
    database or manipulate the existing dataase directly to remove the
    witness and its associated n-grams.

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
    work) into XML suitable for processing via the tacl strip
    command.'''
PREPARE_EPILOG = '''\
    The TEI source options are:

    * {}: the CBETA TEI files as found on their 2011 DVD release

    * {}: the CBETA TEI files as distributed on their GitHub repository
      at https://github.com/cbeta-org/xml-p5.git'''.format(
          TEI_SOURCE_CBETA_2011, TEI_SOURCE_CBETA_GITHUB)
PREPARE_HELP = '''\
    Convert CBETA TEI XML files into an XML form suitable for
    stripping.'''
PREPARE_INPUT_HELP = 'Directory containing XML files to prepare.'
PREPARE_OUTPUT_HELP = 'Directory to output prepared files to.'
PREPARE_SOURCE_HELP = 'Source of TEI files'

REPORT_OUTPUT_HELP = 'Directory to output report to'

RESULTS_BIFURCATED_EXTEND_HELP = '''\
    Extend results to bifurcation points. Generates results containing
    those n-grams, derived from the original n-grams, that have a
    label count higher than their containing (n+1)-grams, or that have
    a label count of one and the constituent (n-1)-grams have a higher
    label count.'''
RESULTS_BIFURCATED_EXTEND_MAX_HELP = 'Maximum size of n-gram to extend to'
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
    following order: --extend, --bifurcated-extend, --reduce,
    --reciprocal, --zero-fill, --ngrams, --min/max-works,
    --min/max-size, --min/max-count, --min/max-count-work, --remove,
    --sort.

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
    count of each n-gram, across all works, must fall. For each work,
    its count is taken as the highest count among its witnesses.

    --min-works and --max-works count works rather than witnesses.

    If both --min-count-work and --max-count-work are specified, only
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
RESULTS_MINIMUM_COUNT_WORK_HELP = '''\
    Minimum count per n-gram per work to include; if a single witness
    meets this criterion for an n-gram, all instances of that n-gram
    are kept.'''
RESULTS_MAXIMUM_COUNT_HELP = 'Maximum total count per n-gram to include.'
RESULTS_MAXIMUM_COUNT_WORK_HELP = '''\
    Maximum count per n-gram per work to include; if a single witness
    meets this criterion for an n-gram, all instances of that n-gram
    are kept.'''
RESULTS_MINIMUM_SIZE_HELP = 'Minimum size of n-grams to include.'
RESULTS_MAXIMUM_SIZE_HELP = 'Maximum size of n-grams to include.'
RESULTS_MINIMUM_WORK_HELP = (
    'Minimum count of works containing n-gram to include.')
RESULTS_MAXIMUM_WORK_HELP = (
    'Maximum count of works containing n-gram to include.')
RESULTS_NGRAMS_HELP = (
    'Path to file containing n-grams (one per line) to exclude.')
RESULTS_RECIPROCAL_HELP = '''\
    Remove n-grams that are not attested by at least one work in each
    labelled set of works. This can be useful after reducing a set of
    intersection results.'''
RESULTS_REDUCE_HELP = 'Remove n-grams that are contained in larger n-grams.'
RESULTS_REMOVE_HELP = 'Remove labelled results.'
RESULTS_RESULTS_HELP = 'Path to CSV results; use - for stdin.'
RESULTS_SORT_HELP = 'Sort the results.'
RESULTS_ZERO_FILL_HELP = '''\
    Add rows with a count of 0 for each n-gram in each witness of a
    work that has at least one witness bearing that n-gram. The
    catalogue used to generate the results must also be specified with
    the -c option.'''

SEARCH_DESCRIPTION = '''\
    List witnesses containing at least one of the supplied n-grams,
    along with a total count of how many occurrences of the n-grams
    are present in each witness, and the number of n-grams that match
    in each witness.

    Specifying a catalogue file will not restrict the search to only
    those labelled works, but rather adds the labels to any
    appropriate witnesses in the results.'''
SEARCH_HELP = 'List witnesses containing at least one of the supplied n-grams.'
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
    file, creating a plain text file for each attested witness.'''
STRIP_EPILOG = '''\
    This command operates on files in an augmented TEI XML format that
    is quite close to that used in the CBETA GitHub files.'''
STRIP_HELP = 'Generate files for use with TACL from a corpus of TEI XML.'
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
    replaced with the supplied labels in the output.

    examples:

        tacl {cmd} -d cbeta2-10.db -l A B -s results1.csv results2.csv > output.csv'''
SUPPLIED_DIFF_EPILOG = SUPPLIED_EPILOG.format(cmd='sdiff')
SUPPLIED_INTERSECT_EPILOG = SUPPLIED_EPILOG.format(cmd='sintersect')
SUPPLIED_INTERSECT_DESCRIPTION = '''\
    List n-grams common to all sets of results (as defined by the
    specified results files).'''
SUPPLIED_INTERSECT_HELP = 'List n-grams common to all results files.'
SUPPLIED_LABELS_HELP = (
    'Labels to be assigned in order to the supplied results.')
SUPPLIED_RESULTS_HELP = 'Paths to results files to be used in the query.'

TACL_DESCRIPTION = 'Analyse the text of corpora in various simple ways.'

TACL_HELPER_AGAINST_DESCRIPTION = '''\
    Generate a script to compare each work in a corpus against all the
    works in another corpus.'''
TACL_HELPER_AGAINST_HELP = '''\
    Generate a script to compare each work in a corpus against all the
    works in another corpus.'''
TACL_HELPER_AGAINST_A_HELP = '''\
    File containing corpus work names to compare (one per line).'''
TACL_HELPER_AGAINST_B_HELP = '''\
    File containing corpus work names to be compared against (one per
    line).'''
TACL_HELPER_COLLAPSE_DESCRIPTION = '''
    Collapse result rows for multiple witnesses having the same count
    for an n-gram. Instead of the "siglum" column, all of the
    witnesses (per work) with the same n-gram count are listed, space
    separated, in the "sigla" column.'''
TACL_HELPER_COLLAPSE_HELP = (
    'Collapse result rows for witnesses having the same count for an n-gram')
TACL_HELPER_DESCRIPTION = '''\
    Perform helpful but non-essential tacl-related functions.'''
TACL_HELPER_IN_DESCRIPTION = '''\
    Generate a script to compare each work in a corpus with all the
    other works in that corpus.'''
TACL_HELPER_IN_HELP = '''\
    Generate a script to compare each work in a corpus with all the
    other works in that corpus.'''
TACL_HELPER_IN_TEXTS_HELP = '''\
    File containing work names to examine (one per line).'''
TACL_HELPER_LABEL_COUNT_DESCRIPTION = '''\
    Output the supplied results with an additional column, "label
    count", giving the total count for each n-gram within the
    label. For each work, the maximum count across all of that work's
    witnesses is used in the sum.'''
TACL_HELPER_LABEL_COUNT_HELP = '''\
    Add a "label count" column to results giving the count per
    label.'''
TACL_HELPER_OUTPUT = 'Output directory for script and catalogue files.'
TACL_HELPER_RESULTS_HELP = 'Path to CSV results'
TACL_HELPER_VALIDATE_CATALOGUE_DESCRIPTION = '''\
    Report any errors in the specified catalogue file. Errors that can
    be detected are referencse to works that do not exist in the
    specified corpus and the same work being listed more than once.'''
TACL_HELPER_VALIDATE_CATALOGUE_HELP = 'Report errors in a catalogue file.'

VERBOSE_HELP = '''\
    Display debug information; multiple -v options increase the verbosity.'''


# Error messages.
CATALOGUE_WORK_RELABELLED_ERROR = 'Catalogue file labels "{}" more than once'
INSUFFICIENT_LABELS_QUERY_ERROR = (
    'Not running query with less than two defined labels')
LABEL_NOT_IN_CATALOGUE_ERROR = (
    'Supplied label is not present in the supplied catalogue')
SUPPLIED_ARGS_LENGTH_MISMATCH_ERROR = (
    'The number of labels supplied does not match the number of results files.'
)


# SQL statements.
ANALYSE_SQL = 'ANALYZE {}'
CREATE_INDEX_INPUT_RESULTS_SQL = (
    'CREATE INDEX IF NOT EXISTS temp.InputResultsLabel '
    'ON InputResults (ngram)')
CREATE_INDEX_TEXT_SQL = (
    'CREATE INDEX IF NOT EXISTS TextIndexLabel ON Text (label)')
CREATE_INDEX_TEXTHASNGRAM_SQL = (
    'CREATE UNIQUE INDEX IF NOT EXISTS TextHasNGramIndex '
    'ON TextHasNGram (text, size)')
CREATE_INDEX_TEXTNGRAM_SQL = (
    'CREATE INDEX IF NOT EXISTS TextNGramIndexTextNGram '
    'ON TextNGram (text, ngram)')
CREATE_TABLE_TEXT_SQL = (
    'CREATE TABLE IF NOT EXISTS Text ('
    'id INTEGER PRIMARY KEY ASC, '
    'work TEXT NOT NULL, '
    'siglum TEXT NOT NULL, '
    'checksum TEXT NOT NULL, '
    'token_count INTEGER NOT NULL, '
    'label TEXT NOT NULL, '
    'UNIQUE (work, siglum))')
CREATE_TABLE_TEXTNGRAM_SQL = (
    'CREATE TABLE IF NOT EXISTS TextNGram ('
    'text INTEGER NOT NULL REFERENCES Text (id), '
    'ngram TEXT NOT NULL, '
    'size INTEGER NOT NULL, '
    'count INTEGER NOT NULL)')
CREATE_TABLE_TEXTHASNGRAM_SQL = (
    'CREATE TABLE IF NOT EXISTS TextHasNGram ('
    'text INTEGER NOT NULL REFERENCES Text (id), '
    'size INTEGER NOT NULL, '
    'count INTEGER NOT NULL)')
CREATE_TEMPORARY_NGRAMS_TABLE_SQL = (
    'CREATE TEMPORARY TABLE InputNGram (ngram TEXT)')
CREATE_TEMPORARY_RESULTS_TABLE_SQL = (
    'CREATE TEMPORARY TABLE InputResults ('
    'ngram TEXT NOT NULL, '
    'size INTEGER NOT NULL, '
    'work TEXT NOT NULL, '
    'siglum TEXT NOT NULL, '
    'count INTEGER NOT NULL, '
    'label TEXT NOT NULL)')
DELETE_TEXT_HAS_NGRAMS_SQL = 'DELETE FROM TextHasNGram WHERE text = ?'
DELETE_TEXT_NGRAMS_SQL = 'DELETE FROM TextNGram WHERE text = ?'
DROP_TEMPORARY_NGRAMS_TABLE_SQL = 'DROP TABLE IF EXISTS InputNGram'
DROP_TEMPORARY_RESULTS_TABLE_SQL = 'DROP TABLE IF EXISTS InputResults'
DROP_TEXTNGRAM_INDEX_SQL = 'DROP INDEX IF EXISTS TextNGramIndexTextNGram'
INSERT_NGRAM_SQL = (
    'INSERT INTO TextNGram (text, ngram, size, count) VALUES (?, ?, ?, ?)')
INSERT_TEXT_HAS_NGRAM_SQL = (
    'INSERT INTO TextHasNGram (text, size, count) VALUES (?, ?, ?)')
INSERT_TEXT_SQL = (
    'INSERT INTO Text (work, siglum, checksum, token_count, label) '
    'VALUES (?, ?, ?, ?, ?)')
INSERT_TEMPORARY_NGRAM_SQL = 'INSERT INTO temp.InputNGram (ngram) VALUES (?)'
INSERT_TEMPORARY_RESULTS_SQL = (
    'INSERT INTO temp.InputResults '
    '(ngram, size, work, siglum, count, label) '
    'VALUES (?, ?, ?, ?, ?, ?)')
PRAGMA_CACHE_SIZE_SQL = 'PRAGMA cache_size={}'
PRAGMA_COUNT_CHANGES_SQL = 'PRAGMA count_changes=OFF'
PRAGMA_FOREIGN_KEYS_SQL = 'PRAGMA foreign_keys=ON'
PRAGMA_LOCKING_MODE_SQL = 'PRAGMA locking_mode=EXCLUSIVE'
PRAGMA_SYNCHRONOUS_SQL = 'PRAGMA synchronous=OFF'
PRAGMA_TEMP_STORE_SQL = 'PRAGMA temp_store=MEMORY'
SELECT_COUNTS_SQL = (
    'SELECT Text.work, Text.siglum, '
    'TextHasNGram.size, TextHasNGram.count AS "unique ngrams", '
    'Text.token_count + 1 - TextHasNGram.size AS "total ngrams", '
    'Text.token_count AS "total tokens", Text.label '
    'FROM Text, TextHasNGram '
    'WHERE Text.id = TextHasNGram.text AND Text.label IN ({}) '
    'ORDER BY Text.work, TextHasNGram.size')
SELECT_DIFF_ASYMMETRIC_SQL = (
    'SELECT TextNGram.ngram, TextNGram.size, '
    'Text.work, Text.siglum, TextNGram.count, Text.label '
    'FROM Text, TextNGram '
    'WHERE Text.label = ? AND Text.id = TextNGram.text '
    'AND TextNGram.ngram IN ('
    'SELECT TextNGram.ngram FROM Text, TextNGram '
    'WHERE Text.id = TextNGram.text AND Text.label = ? '
    'EXCEPT '
    'SELECT TextNGram.ngram FROM Text, TextNGram '
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}))')
SELECT_DIFF_SQL = (
    'SELECT TextNGram.ngram, TextNGram.size, Text.work, Text.siglum, '
    'TextNGram.count, Text.label '
    'FROM Text, TextNGram '
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text '
    'AND TextNGram.ngram IN ('
    'SELECT TextNGram.ngram FROM Text, TextNGram '
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}) '
    'GROUP BY TextNGram.ngram HAVING COUNT(DISTINCT Text.label) = 1)')
SELECT_DIFF_SUPPLIED_SQL = (
    'SELECT ngram, size, work, siglum, count, label '
    'FROM temp.InputResults '
    'WHERE ngram IN ('
    'SELECT ngram FROM temp.InputResults '
    'GROUP BY ngram HAVING COUNT(DISTINCT label) = 1)')
SELECT_HAS_NGRAMS_SQL = (
    'SELECT text FROM TextHasNGram WHERE text = ? AND size = ?')
SELECT_INTERSECT_SQL = (
    'SELECT TextNGram.ngram, TextNGram.size, '
    'Text.work, Text.siglum, TextNGram.count, Text.label '
    'FROM Text, TextNGram '
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text '
    'AND TextNGram.ngram IN ({})')
SELECT_INTERSECT_SUB_EXTRA_SQL = ' AND TextNGram.ngram IN ({})'
SELECT_INTERSECT_SUB_SQL = (
    'SELECT TextNGram.ngram '
    'FROM Text, TextNGram '
    'WHERE Text.label = ? AND Text.id = TextNGram.text')
SELECT_INTERSECT_SUPPLIED_SQL = (
    'SELECT ngram, size, work, siglum, count, label '
    'FROM temp.InputResults '
    'WHERE ngram IN ('
    'SELECT ngram FROM temp.InputResults '
    'GROUP BY ngram HAVING COUNT(DISTINCT label) = ?)')
SELECT_SEARCH_SQL = (
    'SELECT Text.work, Text.siglum, SUM(TextNGram.count) AS count, '
    "Text.label, group_concat(TextNGram.ngram, ', ') AS ngrams, "
    'count(TextNGram.ngram) AS number '
    'FROM Text, TextNGram '
    'WHERE Text.id = TextNGram.text '
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) '
    'GROUP BY TextNGram.text')
SELECT_TEXT_TOKEN_COUNT_SQL = (
    'SELECT Text.token_count FROM Text WHERE Text.work = ?')
SELECT_TEXT_SQL = 'SELECT id, checksum FROM Text WHERE work = ? AND siglum = ?'
UPDATE_LABEL_SQL = 'UPDATE Text SET label = ? WHERE work = ?'
UPDATE_LABELS_SQL = 'UPDATE Text SET label = ?'
UPDATE_TEXT_SQL = 'UPDATE Text SET checksum = ?, token_count = ? WHERE id = ?'
VACUUM_SQL = 'VACUUM'
