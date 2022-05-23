"""Module containing constants."""

TEI_SOURCE_CBETA_GITHUB = 'cbeta-github'
TEI_SOURCE_CHOICES = [TEI_SOURCE_CBETA_GITHUB]

TOKENIZER_CHOICE_CBETA = 'cbeta'
TOKENIZER_CHOICE_LATIN = 'latin'
TOKENIZER_CHOICE_PAGEL = 'pagel'
TOKENIZER_CHOICES = [TOKENIZER_CHOICE_CBETA, TOKENIZER_CHOICE_LATIN,
                     TOKENIZER_CHOICE_PAGEL]
# For the CBETA (Chinese) tokenizer, a token is either a workaround
# (anything in square brackets, as a whole), or a single word
# character. Tokens are grouped together (when constituted into
# n-grams) by an empty string.
TOKENIZER_PATTERN_CBETA = r'\[[^]]*\]|\w'
TOKENIZER_JOINER_CBETA = ''
# For the Latin tokenizer, a token is a continuous sequence of word
# characters. Tokens are grouped together (when constituted into
# n-grams) by a space.
TOKENIZER_PATTERN_LATIN = r'\w+'
TOKENIZER_JOINER_LATIN = ' '
# For the Pagel (Tibetan) tokenizer, a token is a continuous sequence of
# word (plus some punctuation) characters. Tokens are grouped together
# (when constituted into n-grams) by a space.
TOKENIZER_PATTERN_PAGEL = r"[\w'\-+?~]+"
TOKENIZER_JOINER_PAGEL = ' '
TOKENIZERS = {
    TOKENIZER_CHOICE_CBETA: [TOKENIZER_PATTERN_CBETA, TOKENIZER_JOINER_CBETA],
    TOKENIZER_CHOICE_LATIN: [TOKENIZER_PATTERN_LATIN, TOKENIZER_JOINER_LATIN],
    TOKENIZER_CHOICE_PAGEL: [TOKENIZER_PATTERN_PAGEL, TOKENIZER_JOINER_PAGEL],
}

BASE_WITNESS = 'base'
BASE_WITNESS_ID = ''
# XML namespaces.
NAMESPACES = {
    'cb': 'http://www.cbeta.org/ns/1.0',
    'tacl': 'http://github.com/ajenhl/tacl/ns',
    'tei': 'http://www.tei-c.org/ns/1.0',
    'xml': 'http://www.w3.org/XML/1998/namespace'
}
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
LABEL_WORK_COUNT_FIELDNAME = 'label work count'
NGRAM_FIELDNAME = 'ngram'
NGRAMS_FIELDNAME = 'ngrams'
NORMALISED_FIELDNAME = 'normalised ngram'
NUMBER_FIELDNAME = 'number of n-grams'
PERCENTAGE_FIELDNAME = 'percentage'
SIGLA_FIELDNAME = 'sigla'
SIGLUM_FIELDNAME = 'siglum'
SIZE_FIELDNAME = 'size'
TOTAL_COUNT_FIELDNAME = 'total count'
TOTAL_NGRAMS_FIELDNAME = 'total ngrams'
TOTAL_TOKENS_FIELDNAME = 'total tokens'
UNIQUE_NGRAMS_FIELDNAME = 'unique ngrams'
WITNESSES_FIELDNAME = 'witnesses'
WORK_FIELDNAME = 'work'
WORK_COUNTS_FIELDNAME = 'work counts'

QUERY_FIELDNAMES = (NGRAM_FIELDNAME, SIZE_FIELDNAME, WORK_FIELDNAME,
                    SIGLUM_FIELDNAME, COUNT_FIELDNAME, LABEL_FIELDNAME)
COUNTS_FIELDNAMES = (WORK_FIELDNAME, SIGLUM_FIELDNAME, SIZE_FIELDNAME,
                     UNIQUE_NGRAMS_FIELDNAME, TOTAL_NGRAMS_FIELDNAME,
                     TOTAL_TOKENS_FIELDNAME, LABEL_FIELDNAME)
STATISTICS_FIELDNAMES = (WORK_FIELDNAME, SIGLUM_FIELDNAME,
                         COUNT_TOKENS_FIELDNAME, TOTAL_TOKENS_FIELDNAME,
                         PERCENTAGE_FIELDNAME, LABEL_FIELDNAME)

# Those fieldnames whose data in Pandas should be treated as a string
# even if they are numeric.
STRING_FIELDNAMES = (
    LABEL_FIELDNAME, NGRAM_FIELDNAME, SIGLA_FIELDNAME, SIGLUM_FIELDNAME,
    WORK_FIELDNAME
)

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

EXCISE_DESCRIPTION = '''
    Output witness files for each specified work with all of the
    specified n-grams replaced with the supplied replacement text. The
    replacement is done for each n-gram in turn, in descending order
    of n-gram length.'''
EXCISE_HELP = "Remove specified n-grams from specified works' witnesses."
EXCISE_NGRAMS_HELP = '''
    Path to file containing n-grams (one per line) to be replaced.'''
EXCISE_OUTPUT_HELP = 'Path to directory to output transformed files to.'
EXCISE_REPLACEMENT_HELP = '''
    Text to replace n-grams with. This should be one or more valid
    tokens.'''
EXCISE_WORKS_HELP = 'Work whose witnesses will be transformed.'

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
HIGHLIGHT_HELP = '''\
    Output a witness with specified n-grams visually highlighted.'''
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
HIGHLIGHT_RESULTS_HELP = 'Path to CSV results; creates heatmap highlighting.'


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

JOIN_WORKS_CORPUS_HELP = 'Path to corpus of prepared TEI XML texts.'
JOIN_WORKS_DESCRIPTION = '''\
    Join multiple TEI XML works split from the same original work into
    a new single work.'''
JOIN_WORKS_EPILOG = '''\
    Join works is useful when a work has been split into multiple
    parts (likely via tacl prepare) and a new work consisting of some
    of those parts joined togther is wanted.

    The order the works to join are specified determines the order
    they are joined.

    Works are specified via their name, not file path. For example,
    T0006 and not T0006.xml or path/to/corpus/T0006. The same is true
    for the output work name.

    The joined work is output within the specified corpus that
    contains the works being joined.

    Due to the way witnesses are handled, joining works split from
    different original works will almost certainly result in errors or
    incorrect data at later points. Do not do this.'''
JOIN_WORKS_EXISTING_OUTPUT_ERROR = 'Output work {} already exists.'
JOIN_WORKS_HELP = 'Join multiple TEI XML works into a single new work.'
JOIN_WORKS_OUTPUT_HELP = 'Name of work to output the joined works as.'
JOIN_WORKS_WORK_HELP = 'Name of work to join.'

LIFETIME_DESCRIPTION = '''\
    Generate a report on the lifetime of n-grams in a results file.'''
LIFETIME_EPILOG = '''\
    A lifetime report consists of:

    * an HTML table showing the disposition of each n-gram across the
      ordered corpora (with texts and count ranges);

    * an HTML table showing, for each corpus, the n-grams that first
      occurred, only occurred, and last occurred in that corpus; and

    * results files for each category (first occurred in, only
      occurred in , last occurred in) for each corpus.

    This report may be generated from any results file, but is most
    usefully applied to the output of the lifetime script (in the
    tacl-extra package).

    The focus label is informative only, since often multiple lifetime
    reports will be generated, one per corpus, from the same master
    results file, but with specific filtering for the corpus in
    focus.'''
LIFETIME_HELP = 'Generate a report on the lifetime of n-grams.'
LIFETIME_LABEL_HELP = 'Label to mark as the focus of the report.'
LIFETIME_RESULTS_HELP = 'Path to a results file to report on.'

NGRAMS_CATALOGUE_HELP = '''\
    Path to a catalogue file used to restrict which works in the
    corpus are added.'''
NGRAMS_DESCRIPTION = 'Generate n-grams from a corpus.'
NGRAMS_EPILOG = '''\
    This command can be safely interrupted and subsequently rerun;
    witnesses that have already had their n-grams added will be skipped.

    If new witnesses need to be added after a database was generated,
    this command can be run again. However, the speed at which n-grams
    from these new witnesses are added will be much less than to a new
    database, due to the existing indices.

    If a witness has changed or been deleted since a database was
    generated, this command will not update the database. In this
    case, generate a new database or manipulate the existing dataase
    directly to remove the witness and its associated n-grams.

    examples:

      Create a database of 2 to 10-grams from a CBETA corpus.
        tacl ngrams cbeta2-10.db corpus/cbeta/ 2 10

      Create a database of 1 to 7-grams from a Pagel corpus.
        tacl ngrams -t pagel pagel1-7.db corpus/pagel/ 1 7

      Create a database of 1 to 7-grams from a subset of the CBETA corpus.
        tacl ngrams -c dhr-texts.txt cbeta-dhr1-7.db corpus/cbeta/ 1 7

'''
NGRAMS_HELP = 'Generate n-grams from a corpus.'
NGRAMS_MAXIMUM_HELP = 'Maximum size of n-gram to generate (integer).'
NGRAMS_MINIMUM_HELP = 'Minimum size of n-gram to generate (integer).'

NORMALISE_CORPUS_HELP = 'Directory containing corpus to be normalised.'
NORMALISE_DESCRIPTION = '''\
    Create a copy of a corpus normalised according to a supplied mapping.'''
NORMALISE_EPILOG = '''\
    This is a generic normalisation process that is constrained only
    by the possibilities of the mapping format. Lemmatisation could be
    performed in the same way as normalisation of variant characters
    and words.

    LIMITATIONS

    Because the normalised forms in the mapping may only consist of a
    single token, the normalisation and denormalisation processes are
    not able to handle context. Eg, it is not possible to reflect
    "ABA" -> "ACA", where the surrounding "A"s are themselves able to
    be normalised.

    FILES

    The mapping file follows a simple format of comma-separated
    values, with each line having at least two values. The first is
    the normalised form, and all subsequent values on the line being
    the unnormalised forms. During processing, longer unnormalised
    forms are converted first.

    The normalised form is mostly used internally, and so may be
    arbitrary. It may never consist of more than a single token,
    however.'''
NORMALISE_HELP = 'Create a normalised copy of a corpus.'
NORMALISE_MAPPING_HELP = 'Path to mapping file.'
NORMALISE_OUTPUT_HELP = 'Directory to output normalised corpus to.'

PREPARE_DESCRIPTION = '''\
    Convert CBETA TEI XML files (which may have multiple files per
    work) into XML suitable for processing via the tacl strip
    command.'''
PREPARE_EPILOG = '''\
    Existing files are not overwritten by this command.

    The TEI source options are:

    * {}: The CBETA TEI files as distributed on their GitHub repository
      at https://github.com/cbeta-org/xml-p5.git.'''.format(
    TEI_SOURCE_CBETA_GITHUB)
PREPARE_HELP = '''\
    Convert CBETA TEI XML files into an XML form suitable for
    stripping.'''
PREPARE_INPUT_HELP = 'Directory containing XML files to prepare.'
PREPARE_OUTPUT_HELP = 'Directory to output prepared files to.'
PREPARE_SOURCE_HELP = 'Source of TEI files.'

QUERY_DESCRIPTION = '''\
    Run a query specified in a file using supplied parameters,
    outputting the results as CSV.'''
QUERY_HELP = 'Run a query from a file.'
QUERY_PARAMETERS_HELP = 'Parameters to be used in the query.'
QUERY_QUERY_HELP = 'Path to file containing the SQL query to run.'


REPORT_OUTPUT_HELP = 'Directory to output report to.'

RESULTS_ADD_LABEL_COUNT_HELP = '''\
    Output the supplied results with an additional column, "{}",
    giving the total count for each n-gram within the label. For each
    work, the maximum count across all of that work's witnesses is
    used in the sum.'''.format(LABEL_COUNT_FIELDNAME)
RESULTS_ADD_LABEL_WORK_COUNT_HELP = '''\
    Output the supplied results with an additional column, "{}",
    giving the total count of works that contain the n-gram within the
    label. For each work, any number of positive counts across all of
    that work's witnesses is counted as one in the sum.'''.format(
    LABEL_WORK_COUNT_FIELDNAME)
RESULTS_BIFURCATED_EXTEND_HELP = '''\
    Extend results to bifurcation points. Generates results containing
    those n-grams, derived from the original n-grams, that have a
    label count higher than their containing (n+1)-grams, or that have
    a label count of one and the constituent (n-1)-grams have a higher
    label count.'''
RESULTS_BIFURCATED_EXTEND_MAX_HELP = 'Maximum size of n-gram to extend to'
RESULTS_COLLAPSE_WITNESSES_HELP = '''\
    Collapse result rows for multiple witnesses having the same count
    for an n-gram. Instead of the "{}" column, all of the witnesses
    (per work) with the same n-gram count are listed, comma separated,
    in the "{}" column.'''.format(SIGLUM_FIELDNAME, SIGLA_FIELDNAME)
RESULTS_DENORMALISE_CORPUS_HELP = '''\
    Path to directory containing the original (unnormalised)
    corpus. This option must be given along with --denormalise-mapping
    in order for denormalisation to be performed.'''
RESULTS_DENORMALISE_MAPPING_HELP = '''\
    Denormalise result n-grams using mapping at the supplied path. The
    unnormalised corpus must also be specified in the
    --denormalise-corpus option.'''
RESULTS_DESCRIPTION = '''\
    Modify a query results file by adding, removing or otherwise
    manipulating result rows. Outputs the new set of results.'''
RESULTS_EXCISE_HELP = '''\
    Remove all results whose n-gram contains the supplied n-gram
    within it.'''
RESULTS_EXTEND_HELP = '''\
    Extend the results to list the highest size grams that also count
    as matches, going beyond the maximum size recorded in the
    database. This has no effect if the results contain only 1-grams.'''
RESULTS_EPILOG = '''\
    If more than one modifier is specified, they are applied in the
    following order: --extend, --bifurcated-extend,
    --denormalise-corpus, --denormalise_mapping, --reduce,
    --reciprocal, --excise, --zero-fill, --ngrams, --min/max-works,
    --min/max-size, --min/max-count, --min/max-count-work, --remove,
    --relabel, --sort. All of the options that modify the format are
    performed at the end, and only one should be specified. The one
    exception to this is denormalisation, which adds a column to the
    results without disrupting any other operations.

    It is important to be careful with the use of --reduce. Coupled
    with filters such as --max-size, --min-count, etc, many results
    may be discarded without trace (since the reduce occurs
    first). Note too that performing "reduce" on a set of results more
    than once will make the results inaccurate! Denormalisation should
    always be done before reducing results.

    The denormalisation options together produce a set of results with
    all denormalised forms that occur in each witness presented, along
    with an extra column, "{}", giving the normalised form each was
    derived from.

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

    -l/--label causes --min/max-count, --min/max-count-work, and
    --min/max-works to have their requirements apply within that
    labelled subset of results. All n-grams, both within the subset
    and outside it, that meet the criteria are kept, while all other
    n-grams are removed. Note that when applied to diff results, no
    n-grams outside those in the labelled subset will be kept.

    --relabel sets the label for each result row to the label for that
    row's work as specified in the supplied catalogue. If the work is
    not labelled in the catalogue, the label in the results is not
    changed.

    Since this command outputs a valid results file (except when using
    one of those options listed as changing the format), its output
    can be used as input for a subsequent tacl results command. To
    chain commands together without creating an intermediate file,
    pipe the commands together and use - instead of a filename, as:

        tacl results --reciprocal results.csv | tacl results --reduce -

    examples:

      Extend CBETA results and set a minimum total count.
        tacl results -e corpus/cbeta/ --min-count 9 output.csv > mod-output.csv

      Zero-fill CBETA results.
        tacl results -z corpus/cbeta/ output.csv > mod-output.csv

      Reduce Pagel results.
        tacl results --reduce -t pagel output.csv > mod-output.csv

'''.format(NORMALISED_FIELDNAME) + ENCODING_EPILOG
RESULTS_GROUP_BY_NGRAM_HELP = '''\
    Group results by n-gram, providing summary information of the
    works each n-gram appears in. Results are sorted by n-gram and
    then order of occurrence of the label in the supplied
    catalogue.'''
RESULTS_GROUP_BY_WITNESS_HELP = '''\
    Group results by witness, providing summary information of which
    n-grams appear in each witness.'''
RESULTS_HELP = 'Modify a query results file.'
RESULTS_LABEL_HELP = 'Label to restrict prune requirements to'
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
RESULTS_RELABEL_HELP = 'Relabel results according to the supplied catalogue.'
RESULTS_REMOVE_HELP = 'Remove labelled results.'
RESULTS_RESULTS_HELP = 'Path to CSV results; use - for stdin.'
RESULTS_SORT_HELP = 'Sort the results.'
RESULTS_UNSAFE_GROUP_TITLE = 'format changing arguments'
RESULTS_UNSAFE_GROUP_DESCRIPTION = '''\
    These arguments change the format of the results, making them
    potentially unsafe to use other operations on.'''
RESULTS_ZERO_FILL_HELP = '''\
    Add rows with a count of 0 for each n-gram in each witness of a
    work that has at least one witness bearing that n-gram.'''

SEARCH_DESCRIPTION = '''\
    Output results of searching the database for the supplied n-grams
    that occur within labelled witnesses.'''
SEARCH_EPILOG = '''\
    If multiple paths to files containing n-grams are given, the
    combined set of n-grams from all files will be searched for.

    If no path is given, the results will include all n-grams found
    for all of the labelled witnesses in the catalogue.\n\n''' \
        + ENCODING_EPILOG
SEARCH_HELP = 'List witnesses containing at least one of the supplied n-grams.'
SEARCH_NGRAMS_HELP = '''\
    Path to file containing list of n-grams to search for, with one
    n-gram per line.'''

SPLIT_CONF_HELP = '''\
    XML configuration file defining the contents of each witness split
    from the source work.'''
SPLIT_DESCRIPTION = '''\
    Split an existing work into multiple works that are subsets of its
    content.'''
SPLIT_EPILOG = '''\
    Each split configuration file must be named according to the work
    that it defines the splits for (eg, T0278.xml is the name of the
    configuration file for the work T0278). Its format is a simple XML
    structure, as illustrated in the example below:

    <splits delete="true">
      <work>
        <name>T0278-paralleled-earlier</name>
        <parts>
          <part>
            <witnesses>大,宋,元,明,聖</witnesses>
            <start>佛在摩竭提國寂滅道場初始得佛普光法</start>
            <end>最勝或稱能度如是等稱佛名號其數一萬</end>
          </part>
          <part>
            <witnesses>宮</witnesses>
            <start>佛在摩竭提國寂滅道場初始得佛普光法</start>
            <end>最勝或稱能度如是稱佛名號其數一萬</end>
          </part>
          <part>
            <witnesses>ALL</witnesses>
            <start>爾時世尊從兩足相輪放百億光明遍照</start>
            <end>百億色究竟天此世界所有一切悉現</end>
          </part>
        </parts>
      </work>
      <work>
        <name>T0278-ex-earlier-parallels</name>
        <parts>
          <part>
            <witnesses>ALL</witnesses>
            <whole>如此見佛坐蓮華藏師子座上有十佛世界塵數菩薩眷屬圍遶百億閻浮提</whole>
          </part>
          <part>
            <witnesses>ALL</witnesses>
            <start>佛子是為菩薩身口意業能得一切勝妙功</start>
            <end>善哉善哉真佛子快說是法我隨喜</end>
          </part>
        </parts>
      </work>
      <work rename="true">
        <name>Renamed T0278</name>
      </work>
    </splits>

    Each split work is created, under the supplied name, in the corpus
    directory - an error will be raised if there is already a work
    with the same name as the split work. Each of the original work's
    witnesses are recreated, using the subset of its content defined
    in the parts. The parts are processed in the order listed, and a
    witness includes a part only if its siglum is listed in witnesses,
    or the keyword ALL is given in witnesses.

    Each part defines either a start and end piece of text, or a whole
    piece of text. In the former case, the first remaining instance of
    the start text, and everything following it until the first
    remaining instance of the end text, is copied into each applicable
    witness of the new work. In the latter case, the first instance of
    the whole provided text is copied. In both cases, after the
    specified text is copied, it is removed from consideration in the
    future parts of this split work.

    The source work can be output in its entirety under a new name, if
    a "rename" attribute with the value "true" is added to a work
    element, which must contain only a name.

    The source work is left unchanged by the splitting process, unless
    a "delete" attribute with the value "true" is added to the root
    splits element, in which case the work is deleted.'''
SPLIT_HELP = 'Split an existing work into multiple works.'

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

VERBOSE_HELP = '''\
    Display debug information; multiple -v options increase the verbosity.'''


# Error messages.
CATALOGUE_WORK_RELABELLED_ERROR = 'Catalogue file labels "{}" more than once.'
CATALOGUE_WORK_NOT_IN_CORPUS_ERROR = (
    'Catalogue references work "{}" that does not exist in the corpus.')
DUPLICATE_VARIANT_MAPPING_FORM_ERROR = (
    'Normaliser mapping lists "{}" more than once.')
EMPTY_NORMALISED_FORM_ERROR = (
    'Mapping contains an empty normalised form in the row "{}".')
EMPTY_VARIANT_FORM_ERROR = (
    'Normaliser mapping contains an empty variant form for "{}".')
EXCISE_OVERWRITE_WORK_WARNING = ('Output work directory "{}" already exists;'
                                 'existing files may be overwritten.')
INSUFFICIENT_LABELS_QUERY_ERROR = (
    'Not running query with fewer than two defined labels.')
LABEL_NOT_IN_CATALOGUE_ERROR = (
    'Supplied label "{}" is not present in the supplied catalogue.')
MISSING_DATA_STORE_ERROR = (
    'Data store does not exist or is inaccessible at {}.')
MISSING_REQUIRED_COLUMNS_ERROR = (
    'Results file is missing required column(s) {}.')
NGRAM_MINIMUM_SIZE_GREATER_THAN_MAXIMUM_ERROR = (
    'Minimum n-gram size must not be greater than maximum n-gram size.')
NGRAM_SIZE_MUST_BE_INTEGER_ERROR = (
    'N-gram sizes must be given as positive integers.')
NGRAM_SIZE_TOO_SMALL_ERROR = 'Minimum n-gram size is 1.'
NO_VARIANTS_DEFINED_ERROR = 'No variant forms defined in mapping for "{}".'
NON_UTF8_RESULTS_FILE_ERROR = 'Results file "{}" is not encoded as UTF-8.'
SPLIT_DELETE_FAILED = 'Failed to delete work "{}" as directed: {}'
SPLIT_INVALID_WITNESS = ('Part references witness "{}" that does not exist '
                         'in work {}.')
SPLIT_MISSING_END_STRING = 'End string "{}" not found in work "{}" "{}".'
SPLIT_MISSING_START_STRING = 'Start string "{}" not found in work "{}" "{}".'
SPLIT_MISSING_WHOLE_STRING = 'Whole string "{}" not found in work "{}" "{}".'
SPLIT_MISSING_WITNESSES = 'No witnesses specified for part in work "{}".'
SPLIT_MIXED_START_END_STRINGS = ('Start string "{}" comes after end string '
                                 '"{}" in work "{}" "{}".')
SPLIT_OUTPUT_DIRECTORY_EXISTS = ('Output directory for split work "{}" in '
                                 'work {} already exists.')
SPLIT_WORK_NOT_IN_CORPUS_ERROR = 'Work {} does not exist in corpus.'
SUPPLIED_ARGS_LENGTH_MISMATCH_ERROR = (
    'The number of labels supplied does not match the number of results files.'
)
TOO_LONG_NORMALISED_FORM_ERROR = ('Normalised form "{}" is longer than one '
                                  'token, which is prohibited.')


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
    'text INTEGER NOT NULL REFERENCES Text (id) ON DELETE CASCADE, '
    'ngram TEXT NOT NULL, '
    'size INTEGER NOT NULL, '
    'count INTEGER NOT NULL)')
CREATE_TABLE_TEXTHASNGRAM_SQL = (
    'CREATE TABLE IF NOT EXISTS TextHasNGram ('
    'text INTEGER NOT NULL REFERENCES Text (id) ON DELETE CASCADE, '
    'size INTEGER NOT NULL, '
    'count INTEGER NOT NULL)')
CREATE_TEMPORARY_NGRAMS_TABLE_SQL = (
    'CREATE TEMPORARY TABLE InputNGram (ngram TEXT UNIQUE)')
CREATE_TEMPORARY_RESULTS_TABLE_SQL = (
    'CREATE TEMPORARY TABLE InputResults ('
    'ngram TEXT NOT NULL, '
    'size INTEGER NOT NULL, '
    'work TEXT NOT NULL, '
    'siglum TEXT NOT NULL, '
    'count INTEGER NOT NULL, '
    'label TEXT NOT NULL)')
DELETE_TEXT_SQL = 'DELETE FROM Text WHERE id = ?'
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
    'TextHasNGram.size, TextHasNGram.count AS "%s", '
    'Text.token_count + 1 - TextHasNGram.size AS "%s", '
    'Text.token_count AS "%s", Text.label '
    'FROM Text, TextHasNGram '
    'WHERE Text.id = TextHasNGram.text AND Text.label IN ({}) '
    'ORDER BY Text.work, TextHasNGram.size' % (
        UNIQUE_NGRAMS_FIELDNAME, TOTAL_NGRAMS_FIELDNAME,
        TOTAL_TOKENS_FIELDNAME))
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
    'SELECT TextNGram.ngram, TextNGram.size, Text.work, Text.siglum, '
    'TextNGram.count, Text.label '
    'FROM Text, TextNGram '
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text '
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram)')
SELECT_SEARCH_ALL_SQL = (
    'SELECT TextNGram.ngram, TextNGram.size, Text.work, Text.siglum, '
    'TextNGram.count, Text.label '
    'FROM Text, TextNGram '
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text')
SELECT_TEXT_TOKEN_COUNT_SQL = (
    'SELECT Text.token_count FROM Text WHERE Text.work = ?')
SELECT_TEXT_SQL = 'SELECT id, checksum FROM Text WHERE work = ? AND siglum = ?'
SELECT_TEXTS_SQL = 'SELECT id, work, siglum FROM Text'
SELECT_WORK_TEXTS_SQL = 'SELECT id, work, siglum FROM Text WHERE work = ?'
UPDATE_LABEL_SQL = 'UPDATE Text SET label = ? WHERE work = ?'
UPDATE_LABELS_SQL = 'UPDATE Text SET label = ?'
UPDATE_TEXT_SQL = 'UPDATE Text SET checksum = ?, token_count = ? WHERE id = ?'
VACUUM_SQL = 'VACUUM'
