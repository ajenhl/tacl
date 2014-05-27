"""Module containing constants."""

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
FILENAME_FIELDNAME = 'filename'
LABEL_FIELDNAME = 'label'
NGRAM_FIELDNAME = 'ngram'
NGRAMS_FIELDNAME = 'ngrams'
PERCENTAGE_FIELDNAME = 'percentage'
SIZE_FIELDNAME = 'size'
TOTAL_NGRAMS_FIELDNAME = 'total ngrams'
TOTAL_TOKENS_FIELDNAME = 'total tokens'
UNIQUE_NGRAMS_FIELDNAME = 'unique ngrams'

QUERY_FIELDNAMES = [NGRAM_FIELDNAME, SIZE_FIELDNAME, FILENAME_FIELDNAME,
                    COUNT_FIELDNAME, LABEL_FIELDNAME]
COUNTS_FIELDNAMES = [FILENAME_FIELDNAME, SIZE_FIELDNAME,
                     UNIQUE_NGRAMS_FIELDNAME, TOTAL_NGRAMS_FIELDNAME,
                     TOTAL_TOKENS_FIELDNAME, LABEL_FIELDNAME]
SEARCH_FIELDNAMES = [FILENAME_FIELDNAME, COUNT_FIELDNAME, LABEL_FIELDNAME, NGRAMS_FIELDNAME]
STATISTICS_FIELDNAMES = [FILENAME_FIELDNAME, COUNT_TOKENS_FIELDNAME,
                         TOTAL_TOKENS_FIELDNAME, PERCENTAGE_FIELDNAME,
                         LABEL_FIELDNAME]

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

DIFF_DESCRIPTION = 'List n-grams unique to each sub-corpus.'
DIFF_EPILOG = ENCODING_EPILOG
DIFF_HELP = 'List n-grams unique to each sub-corpus.'

HIGHLIGHT_BASE_HELP = 'Filename of text to display.'
HIGHLIGHT_DESCRIPTION = '''\
    Output an HTML document showing a text with its matches visually
    highlighted.'''
HIGHLIGHT_EPILOG = '''\
    The scope of the supplied results may have a dramatic influence on
    the amount of highlighting. Results containing 1-grams are very
    likely to be almost entirely highlighted. Results may be
    restricted by using the tacl report command.'''
HIGHLIGHT_HELP = 'Output a text with its matches visually highlighted.'

INPUT_RESULTS_HELP = '''\
    Path to results file to restrict query to.'''

INTERSECT_DESCRIPTION = 'List n-grams common to all sub-corpora.'
INTERSECT_EPILOG = ENCODING_EPILOG
INTERSECT_HELP = 'List n-grams common to all sub-corpora.'

NGRAMS_DESCRIPTION = 'Generate n-grams from a corpus.'
NGRAMS_HELP = 'Generate n-grams from a corpus.'
NGRAMS_MAXIMUM_HELP = 'Maximum size of n-gram to generate (integer).'
NGRAMS_MINIMUM_HELP = 'Minimum size of n-gram to generate (integer).'

REPORT_DESCRIPTION = '''\
    Modify a query results file by removing certain results. Outputs
    the new set of results. See below for the exceptional statistics
    output.'''
REPORT_EXTEND_HELP = '''\
    Extend the results to list the highest size grams that also count
    as matches, going beyond the maximum size recorded in the
    database. This has no effect on the results of a diff query, or if
    the results contain only 1-grams.'''
REPORT_EPILOG = '''\
    If more than one modifier is specified, they are applied in the
    following order: --extend, --reduce, --reciprocal, --min/max-texts,
    --min/max-size, --min/max-count, --remove.

    It is important to be careful with the use of --reduce. Coupled
    with --max-size, many results may be discarded without trace
    (since the reduce occurs first). Note too that performing "reduce"
    on a set of results more than once will make the results
    inaccurate!

    Since this command always outputs a valid results file, its output
    can be used as input for a subsequent tacl report command. To
    chain commands together without creating an intermediate file,
    pipe the commands together and use - instead of a filename, as:

        tacl report --recriprocal results.csv | tacl report --reduce -

    {}'''.format(ENCODING_EPILOG)
REPORT_HELP = 'Modify a query results file.'
REPORT_MINIMUM_COUNT_HELP = 'Minimum total count of n-gram to include.'
REPORT_MAXIMUM_COUNT_HELP = 'Maximum total count of n-gram to include.'
REPORT_MINIMUM_SIZE_HELP = 'Minimum size of n-grams to include.'
REPORT_MAXIMUM_SIZE_HELP = 'Maximum size of n-grams to include.'
REPORT_MINIMUM_TEXT_HELP = 'Minimum count of texts containing n-gram to include.'
REPORT_MAXIMUM_TEXT_HELP = 'Maximum count of texts containing n-gram to include.'
REPORT_RECIPROCAL_HELP = '''\
    Remove n-grams that are not attested by at least one text in each
    labelled set of texts.'''
REPORT_REDUCE_HELP = 'Remove n-grams that are contained in larger n-grams.'
REPORT_REMOVE_HELP = 'Remove labelled results.'
REPORT_RESULTS_HELP = 'Path to CSV results; use - for stdin.'
REPORT_SORT_HELP = 'Sort the results.'

SEARCH_DESCRIPTION = '''\
    List texts containing at least one of the supplied n-grams, along
    with a count of how many of the n-grams are present in each
    text.'''
SEARCH_HELP = 'List texts containing at least one of the supplied n-grams.'
SEARCH_NGRAMS_HELP = '''\
    Path to file containing list of n-grams to search for, with one
    n-gram per line.'''

STATISTICS_COUNTS_HELP = 'Path to CSV counts (from tacl counts).'
STATISTICS_DESCRIPTION = 'Generate summary statistic for a set of results.'
STATISTICS_EPILOG = '''\
    The output giving the percentage of each text's tokens that are in
    the results depends on those results being reduced. If the
    supplied results file has not been reduced, pass the --reduce
    option.'''
STATISTICS_HELP = 'Generate summary statistics for a set of results.'
STATISTICS_RESULTS_HELP = 'Path to CSV results.'

STRIP_DESCRIPTION = '''\
    Preprocess a corpus by stripping unwanted material from each
    text.'''
STRIP_EPILOG = '''\
    The CBETA texts are in TEI XML that needs to have the markup and
    metadata removed.'''
STRIP_HELP = 'Preprocess a corpus for use with TACL.'
STRIP_INPUT_HELP = 'Directory containing files to strip.'
STRIP_OUTPUT_HELP = 'Directory to output stripped files to.'

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
TACL_HELPER_IN_DESCRIPTION = '''\
    Generate a script to compare each text of a corpus with all the
    other texts of that corpus.'''
TACL_HELPER_IN_HELP = '''\
    Generate a script to compare each text of a corpus with all the
    other texts of that corpus.'''
TACL_HELPER_IN_TEXTS_HELP = '''\
    File containing text names to examine (one per line).'''
TACL_HELPER_OUTPUT = 'Output directory for script and catalogue files.'

VERBOSE_HELP = '''\
    Display debug information; multiple -v options increase the verbosity.'''


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
    'token_count INTEGER NOT NULL, ' \
    'label TEXT NOT NULL)'
CREATE_TABLE_TEXTNGRAM_SQL = 'CREATE TABLE IF NOT EXISTS TextNGram (' \
    'text INTEGER NOT NULL REFERENCES Text (id), ' \
    'ngram TEXT NOT NULL, ' \
    'size INTEGER NOT NULL, ' \
    'count INTEGER NOT NULL)'
CREATE_TABLE_TEXTHASNGRAM_SQL = 'CREATE TABLE IF NOT EXISTS TextHasNGram (' \
    'text INTEGER NOT NULL REFERENCES Text (id), ' \
    'size INTEGER NOT NULL, ' \
    'count INTEGER NOT NULL)'
CREATE_TEMPORARY_TABLE_SQL = 'CREATE TEMPORARY TABLE InputNGram (ngram Text)'
DELETE_TEXT_HAS_NGRAMS_SQL = 'DELETE FROM TextHasNGram WHERE text = ?'
DELETE_TEXT_NGRAMS_SQL = 'DELETE FROM TextNGram WHERE text = ?'
DROP_TEXTNGRAM_INDEX_SQL = 'DROP INDEX IF EXISTS TextNGramIndexTextNGram'
INSERT_NGRAM_SQL = 'INSERT INTO TextNGram (text, ngram, size, count) ' \
    'VALUES (?, ?, ?, ?)'
INSERT_TEXT_HAS_NGRAM_SQL = 'INSERT INTO TextHasNGram (text, size, count) ' \
    'VALUES (?, ?, ?)'
INSERT_TEXT_SQL = 'INSERT INTO Text (filename, checksum, token_count, label) ' \
    'VALUES (?, ?, ?, ?)'
INSERT_TEMPORARY_NGRAM_SQL = 'INSERT INTO temp.InputNGram (ngram) VALUES (?)'
PRAGMA_CACHE_SIZE_SQL = 'PRAGMA cache_size={}'
PRAGMA_COUNT_CHANGES_SQL = 'PRAGMA count_changes=OFF'
PRAGMA_FOREIGN_KEYS_SQL = 'PRAGMA foreign_keys=ON'
PRAGMA_LOCKING_MODE_SQL = 'PRAGMA locking_mode=EXCLUSIVE'
PRAGMA_SYNCHRONOUS_SQL = 'PRAGMA synchronous=OFF'
PRAGMA_TEMP_STORE_SQL = 'PRAGMA temp_store=MEMORY'
SELECT_COUNTS_SQL = 'SELECT Text.filename, TextHasNGram.size, ' \
    'TextHasNGram.count as "unique ngrams", ' \
    'Text.token_count + 1 - TextHasNGram.size as "total ngrams", ' \
    'Text.token_count AS "total tokens", Text.label ' \
    'FROM Text, TextHasNGram ' \
    'WHERE Text.id = TextHasNGram.text AND Text.label IN ({}) ' \
    'ORDER BY Text.filename, TextHasNGram.size'
SELECT_DIFF_ASYMMETRIC_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label = ? AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (' \
    'SELECT TextNGram.ngram FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label = ? ' \
    'EXCEPT ' \
    'SELECT TextNGram.ngram FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}))'
SELECT_DIFF_SQL = 'SELECT TextNGram.ngram, TextNGram.size, TextNGram.count, ' \
    'Text.filename, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (' \
    'SELECT TextNGram.ngram FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text AND Text.label IN ({}) ' \
    'GROUP BY TextNGram.ngram HAVING COUNT(DISTINCT Text.label) = 1)'
SELECT_DIFF_SUPPLIED_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) ' \
    'AND NOT EXISTS (' \
    'SELECT tn.ngram FROM Text t, TextNGram tn ' \
    'WHERE t.id = tn.text AND t.label IN ({}) AND tn.ngram = TextNGram.ngram)'
SELECT_HAS_NGRAMS_SQL = 'SELECT text FROM TextHasNGram ' \
    'WHERE text = ? AND size = ?'
SELECT_INTERSECT_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN ({})'
SELECT_INTERSECT_SUB_EXTRA_SQL = ' AND TextNGram.ngram IN ({})'
SELECT_INTERSECT_SUB_SQL = 'SELECT TextNGram.ngram ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label = ? AND Text.id = TextNGram.text'
SELECT_INTERSECT_SUPPLIED_SQL = 'SELECT TextNGram.ngram, TextNGram.size, ' \
    'TextNGram.count, Text.filename, Text.label ' \
    'FROM Text, TextNGram ' \
    'WHERE Text.label IN ({}) AND Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) ' \
    'AND TextNGram.ngram IN ({})'
SELECT_SEARCH_SQL = 'SELECT Text.filename, COUNT(TextNGram.ngram) AS count, ' \
    "Text.label, group_concat(TextNGram.ngram, ', ') AS ngrams " \
    'FROM Text, TextNGram ' \
    'WHERE Text.id = TextNGram.text ' \
    'AND TextNGram.ngram IN (SELECT ngram FROM temp.InputNGram) ' \
    'GROUP BY TextNGram.text'
SELECT_TEXT_TOKEN_COUNT_SQL = 'SELECT Text.token_count ' \
    'FROM Text WHERE Text.filename = ?'
SELECT_TEXT_SQL = 'SELECT id, checksum FROM Text WHERE filename = ?'
UPDATE_LABEL_SQL = 'UPDATE Text SET label = ? WHERE filename = ?'
UPDATE_LABELS_SQL = 'UPDATE Text SET label = ?'
UPDATE_TEXT_SQL = 'UPDATE Text SET checksum = ?, token_count = ? WHERE id = ?'
VACUUM_SQL = 'VACUUM'

HIGHLIGHT_TEMPLATE = '''<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>{base_filename} with matches from each other text highlighted</title>
    <style>
      body {{ margin-left: 4em; color: black; background-color: white; }}
      div.text-list {{ float: right; width: 15em; margin-left: 3em; }}
      ul {{ list-style-type: none; }}
    </style>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script>
  </head>
  <body>
    <h1>{base_filename} with matches from each other text highlighted</h1>

    <div class="text-list">{text_list}</div>

    <div class="text">{text}</div>

    <script>
      var n = 10;
      var xr = 0;
      var xg = 0;
      var xb = 255;
      var yr = 255;
      var yg = 0;
      var yb = 0;
      var max = $("input").length;

      function recalculateHeat (textname, change) {{
        $("span[data-texts~='" + textname + "']").each(function () {{
          $(this).attr("data-count", function () {{
            return parseInt($(this).attr("data-count")) + change;
          }});
          val = parseInt($(this).attr("data-count"));
          if (val == 0) {{
              clr = 'rgb(0,0,0)';
          }} else {{
              pos = parseInt((Math.round((val/max)*n)).toFixed(0));
              red = parseInt((xr + (( pos * (yr - xr)) / (n-1))).toFixed(0));
              green = parseInt((xg + (( pos * (yg - xg)) / (n-1))).toFixed(0));
              blue = parseInt((xb + (( pos * (yb - xb)) / (n-1))).toFixed(0));
              clr = 'rgb('+red+','+green+','+blue+')';
          }}
          $(this).css({{color:clr}});
        }});
      }}

      $(document).ready(function () {{
        $("input").on("click", function (event) {{
          var $textname = $(this).val();
          var $change;
          if ($(this).prop('checked')) {{
            $change = 1;
          }} else {{
            $change = -1;
          }}
          recalculateHeat($textname, $change);
        }});
      }});
    </script>
  </body>
</html>'''

FILE_SEQUENCES_HTML = '''<html lang="zh">
  <head>
    <meta charset="UTF-8">
    <title lang="en">Alignment between {f1} and {f2}</title>
    <style>
      :lang(en) {{ overflow-wrap: normal; word-break: normal; }}
      :lang(zh) {{ overflow-wrap: break-word; word-break: break-all; }}
      table {{ border-style: dotted; border-width: 1px; margin-bottom: 3em; }}
      td {{ border-style: dotted; border-width: 1px; line-height: 1.5;
            padding: 0.5em; vertical-align: top; }}
      .match {{ font-weight: bold; }}
    </style>
  </head>
  <body>
    <h1 lang="en">Alignment between {f1} and {f2}</h1>

    <table>
      <thead>
        <tr>
          <th>{f1}</th>
          <th>{f2}</th>
        </tr>
      </thead>
      <tbody>
        {sequences}
      </tbody>
    </table>
  </body>
</html>'''

SEQUENCE_HTML = '''<tr>
  <td>{}</td>
  <td>{}</td>
</tr>'''
