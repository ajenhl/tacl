"""Command-line script to perform n-gram analysis of a corpus of
texts."""

import argparse
import io
import logging
import sys

import tacl
from tacl import constants
from tacl.command.formatters import ParagraphFormatter


logger = logging.getLogger('tacl')


def main ():
    parser = generate_parser()
    args = parser.parse_args()
    if hasattr(args, 'verbose'):
        configure_logging(args.verbose)
    if hasattr(args, 'func'):
        args.func(args, parser)
    else:
        parser.print_help()

def add_common_arguments (parser):
    """Adds common arguments for all parsers."""
    parser.add_argument('-v', '--verbose', action='count',
                        help=constants.VERBOSE_HELP)

def add_corpus_arguments (parser):
    """Adds common arguments for commands making use of a corpus to
    `parser`."""
    add_tokenizer_argument(parser)
    parser.add_argument('corpus', help=constants.DB_CORPUS_HELP,
                        metavar='CORPUS')

def add_db_arguments (parser, db_option=False):
    """Adds common arguments for the database sub-commands to
    `parser`.

    `db_option` provides a means to work around
    https://bugs.python.org/issue9338 whereby a positional argument
    that follows an optional argument with nargs='+' will not be
    recognised. When `db_optional` is True, create the database
    argument as a required optional argument, rather than a positional
    argument.

    """
    parser.add_argument('-m', '--memory', action='store_true',
                        help=constants.DB_MEMORY_HELP)
    parser.add_argument('-r', '--ram', default=3, help=constants.DB_RAM_HELP,
                        type=int)
    if db_option:
        parser.add_argument('-d', '--db', help=constants.DB_DATABASE_HELP,
                            metavar='DATABASE', required=True)
    else:
        parser.add_argument('db', help=constants.DB_DATABASE_HELP,
                            metavar='DATABASE')

def add_query_arguments (parser):
    """Adds common arguments for query sub-commonads to `parser`."""
    parser.add_argument('catalogue', help=constants.CATALOGUE_CATALOGUE_HELP,
                        metavar='CATALOGUE')

def add_supplied_query_arguments (parser):
    """Adds common arguments for supplied query sub-commands to
    `parser`."""
    parser.add_argument('-l', '--labels', help=constants.SUPPLIED_LABELS_HELP,
                        nargs='+', required=True)
    parser.add_argument('-s', '--supplied', help=constants.SUPPLIED_RESULTS_HELP,
                        metavar='RESULTS', nargs='+', required=True)

def add_tokenizer_argument (parser):
    parser.add_argument('-t', '--tokenizer', choices=constants.TOKENIZER_CHOICES,
                        default=constants.TOKENIZER_CHOICE_CBETA,
                        help=constants.DB_TOKENIZER_HELP)

def align_results (args, parser):
    if args.results == '-':
        results = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',
                                   newline='')
    else:
        results = open(args.results, 'r', encoding='utf-8', newline='')
    tokenizer = get_tokenizer(args)
    corpus = tacl.Corpus(args.corpus, tokenizer)
    s = tacl.Sequencer(corpus, tokenizer, results, args.output)
    s.generate_sequences(args.minimum)

def configure_logging (verbose):
    """Configures the logging used."""
    if not verbose:
        log_level = logging.WARNING
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def generate_parser ():
    """Returns a parser configured with sub-commands and arguments."""
    parser = argparse.ArgumentParser(
        description=constants.TACL_DESCRIPTION,
        formatter_class=ParagraphFormatter)
    subparsers = parser.add_subparsers(title='subcommands')
    generate_align_subparser(subparsers)
    generate_catalogue_subparser(subparsers)
    generate_counts_subparser(subparsers)
    generate_diff_subparser(subparsers)
    generate_highlight_subparser(subparsers)
    generate_intersect_subparser(subparsers)
    generate_ngrams_subparser(subparsers)
    generate_prepare_subparser(subparsers)
    generate_report_subparser(subparsers)
    generate_supplied_diff_subparser(subparsers)
    generate_search_subparser(subparsers)
    generate_supplied_intersect_subparser(subparsers)
    generate_statistics_subparser(subparsers)
    generate_strip_subparser(subparsers)
    return parser

def generate_align_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to generate aligned
    sequences from a set of results."""
    parser = subparsers.add_parser(
        'align', description=constants.ALIGN_DESCRIPTION,
        epilog=constants.ALIGN_EPILOG,
        formatter_class=ParagraphFormatter, help=constants.ALIGN_HELP)
    parser.set_defaults(func=align_results)
    add_common_arguments(parser)
    parser.add_argument('-m', '--minimum', default=20,
                        help=constants.ALIGN_MINIMUM_SIZE_HELP, type=int)
    add_corpus_arguments(parser)
    parser.add_argument('output', help=constants.ALIGN_OUTPUT_HELP,
                        metavar='OUTPUT')
    parser.add_argument('results', help=constants.REPORT_RESULTS_HELP,
                        metavar='RESULTS')

def generate_catalogue (args, parser):
    """Generates and saves a catalogue file."""
    catalogue = tacl.Catalogue()
    catalogue.generate(args.corpus, args.label)
    catalogue.save(args.catalogue)

def generate_catalogue_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to generate and save
    a catalogue file."""
    parser = subparsers.add_parser(
        'catalogue', description=constants.CATALOGUE_DESCRIPTION,
        epilog=constants.CATALOGUE_EPILOG,
        formatter_class=ParagraphFormatter, help=constants.CATALOGUE_HELP)
    add_common_arguments(parser)
    parser.set_defaults(func=generate_catalogue)
    parser.add_argument('corpus', help=constants.DB_CORPUS_HELP,
                        metavar='CORPUS')
    add_query_arguments(parser)
    parser.add_argument('-l', '--label', default='',
                        help=constants.CATALOGUE_LABEL_HELP)

def generate_counts_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to make a counts
    query."""
    parser = subparsers.add_parser(
        'counts', description=constants.COUNTS_DESCRIPTION,
        epilog=constants.COUNTS_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.COUNTS_HELP)
    parser.set_defaults(func=ngram_counts)
    add_common_arguments(parser)
    add_db_arguments(parser)
    add_corpus_arguments(parser)
    add_query_arguments(parser)

def generate_diff_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to make a diff
    query."""
    parser = subparsers.add_parser(
        'diff', description=constants.DIFF_DESCRIPTION,
        epilog=constants.DIFF_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.DIFF_HELP)
    parser.set_defaults(func=ngram_diff)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--asymmetric', help=constants.ASYMMETRIC_HELP,
                       metavar='LABEL')
    add_common_arguments(parser)
    add_db_arguments(parser)
    add_corpus_arguments(parser)
    add_query_arguments(parser)

def generate_highlight_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to highlight a text with
    its matches in a result."""
    parser = subparsers.add_parser(
        'highlight', description=constants.HIGHLIGHT_DESCRIPTION,
        epilog=constants.HIGHLIGHT_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.HIGHLIGHT_HELP)
    parser.set_defaults(func=highlight_text)
    add_common_arguments(parser)
    add_corpus_arguments(parser)
    parser.add_argument('results', help=constants.STATISTICS_RESULTS_HELP,
                        metavar='RESULTS')
    parser.add_argument('base_name', help=constants.HIGHLIGHT_BASE_NAME_HELP,
                        metavar='BASE_NAME')
    parser.add_argument('base_siglum', metavar='BASE_SIGLUM',
                        help=constants.HIGHLIGHT_BASE_SIGLUM_HELP)

def generate_intersect_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to make an
    intersection query."""
    parser = subparsers.add_parser(
        'intersect', description=constants.INTERSECT_DESCRIPTION,
        epilog=constants.INTERSECT_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.INTERSECT_HELP)
    parser.set_defaults(func=ngram_intersection)
    add_common_arguments(parser)
    add_db_arguments(parser)
    add_corpus_arguments(parser)
    add_query_arguments(parser)

def generate_ngrams (args, parser):
    """Adds n-grams data to the data store."""
    store = get_data_store(args)
    corpus = get_corpus(args)
    store.add_ngrams(corpus, args.min_size, args.max_size)

def generate_ngrams_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to add n-grams data
    to the data store."""
    parser = subparsers.add_parser(
        'ngrams', description=constants.NGRAMS_DESCRIPTION,
        formatter_class=ParagraphFormatter, help=constants.NGRAMS_HELP)
    parser.set_defaults(func=generate_ngrams)
    add_common_arguments(parser)
    add_db_arguments(parser)
    add_corpus_arguments(parser)
    parser.add_argument('min_size', help=constants.NGRAMS_MINIMUM_HELP,
                        metavar='MINIMUM', type=int)
    parser.add_argument('max_size', help=constants.NGRAMS_MAXIMUM_HELP,
                        metavar='MAXIMUM', type=int)

def generate_prepare_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to prepare source XML
    files for stripping."""
    parser = subparsers.add_parser(
        'prepare', description=constants.PREPARE_DESCRIPTION,
        formatter_class=ParagraphFormatter, help=constants.PREPARE_HELP)
    parser.set_defaults(func=prepare_xml)
    add_common_arguments(parser)
    parser.add_argument('input', help=constants.PREPARE_INPUT_HELP,
                        metavar='INPUT')
    parser.add_argument('output', help=constants.PREPARE_OUTPUT_HELP,
                        metavar='OUTPUT')

def generate_report_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to manipulate CSV
    results data."""
    parser = subparsers.add_parser(
        'report', description=constants.REPORT_DESCRIPTION,
        epilog=constants.REPORT_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.REPORT_HELP)
    add_common_arguments(parser)
    parser.set_defaults(func=report)
    parser.add_argument('-c', '--catalogue', dest='catalogue',
                        help=constants.REPORT_CATALOGUE_HELP,
                        metavar='CATALOGUE')
    parser.add_argument('-e', '--extend', dest='extend',
                        help=constants.REPORT_EXTEND_HELP, metavar='CORPUS')
    parser.add_argument('--min-count', dest='min_count',
                        help=constants.REPORT_MINIMUM_COUNT_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--max-count', dest='max_count',
                        help=constants.REPORT_MAXIMUM_COUNT_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--min-size', dest='min_size',
                        help=constants.REPORT_MINIMUM_SIZE_HELP, metavar='SIZE',
                        type=int)
    parser.add_argument('--max-size', dest='max_size',
                        help=constants.REPORT_MAXIMUM_SIZE_HELP, metavar='SIZE',
                        type=int)
    parser.add_argument('--min-texts', dest='min_texts',
                        help=constants.REPORT_MINIMUM_TEXT_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--max-texts', dest='max_texts',
                        help=constants.REPORT_MAXIMUM_TEXT_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--reciprocal', action='store_true',
                        help=constants.REPORT_RECIPROCAL_HELP)
    parser.add_argument('--reduce', action='store_true',
                        help=constants.REPORT_REDUCE_HELP)
    parser.add_argument('--remove', help=constants.REPORT_REMOVE_HELP,
                        metavar='LABEL', type=str)
    parser.add_argument('--sort', action='store_true',
                        help=constants.REPORT_SORT_HELP)
    add_tokenizer_argument(parser)
    parser.add_argument('-z', '--zero-fill', dest='zero_fill',
                        help=constants.REPORT_ZERO_FILL_HELP, metavar='CORPUS')
    parser.add_argument('results', help=constants.REPORT_RESULTS_HELP,
                        metavar='RESULTS')

def generate_search_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to generate search
    results for a set of n-grams."""
    parser = subparsers.add_parser(
        'search', description=constants.SEARCH_DESCRIPTION,
        formatter_class=ParagraphFormatter, help=constants.SEARCH_HELP)
    parser.set_defaults(func=search_texts)
    add_common_arguments(parser)
    add_db_arguments(parser)
    add_corpus_arguments(parser)
    parser.add_argument('-c', '--catalogue', metavar='CATALOGUE',
                        help=constants.CATALOGUE_CATALOGUE_HELP)
    parser.add_argument('ngrams', help=constants.SEARCH_NGRAMS_HELP,
                        metavar='NGRAMS')

def generate_statistics (args, parser):
    corpus = get_corpus(args)
    tokenizer = get_tokenizer(args)
    report = tacl.StatisticsReport(corpus, tokenizer, args.results)
    report.generate_statistics()
    report.csv(sys.stdout)

def generate_statistics_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to generate statistics
    from a set of results."""
    parser = subparsers.add_parser(
        'stats', description=constants.STATISTICS_DESCRIPTION,
        formatter_class=ParagraphFormatter, help=constants.STATISTICS_HELP)
    parser.set_defaults(func=generate_statistics)
    add_common_arguments(parser)
    add_corpus_arguments(parser)
    parser.add_argument('results', help=constants.STATISTICS_RESULTS_HELP,
                        metavar='RESULTS')

def generate_strip_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to process original
    texts for use with the tacl ngrams command."""
    parser = subparsers.add_parser(
        'strip', description=constants.STRIP_DESCRIPTION,
        epilog=constants.STRIP_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.STRIP_HELP)
    parser.set_defaults(func=strip_texts)
    add_common_arguments(parser)
    parser.add_argument('input', help=constants.STRIP_INPUT_HELP,
                        metavar='INPUT')
    parser.add_argument('output', help=constants.STRIP_OUTPUT_HELP,
                        metavar='OUTPUT')

def generate_supplied_diff_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to run a diff query using
    the supplied results sets."""
    parser = subparsers.add_parser(
        'sdiff', description=constants.SUPPLIED_DIFF_DESCRIPTION,
        epilog=constants.SUPPLIED_DIFF_EPILOG,
        formatter_class=ParagraphFormatter, help=constants.SUPPLIED_DIFF_HELP)
    parser.set_defaults(func=supplied_diff)
    add_common_arguments(parser)
    add_db_arguments(parser, True)
    add_supplied_query_arguments(parser)

def generate_supplied_intersect_subparser (subparsers):
    """Adds a sub-command parser to `subparsers` to run an intersect query
    using the supplied results sets."""
    parser = subparsers.add_parser(
        'sintersect', description=constants.SUPPLIED_INTERSECT_DESCRIPTION,
        epilog=constants.SUPPLIED_INTERSECT_EPILOG,
        formatter_class=ParagraphFormatter,
        help=constants.SUPPLIED_INTERSECT_HELP)
    parser.set_defaults(func=supplied_intersect)
    add_common_arguments(parser)
    add_db_arguments(parser, True)
    add_supplied_query_arguments(parser)

def get_corpus (args):
    """Returns a `tacl.Corpus`."""
    tokenizer = get_tokenizer(args)
    return tacl.Corpus(args.corpus, tokenizer)

def get_catalogue (path):
    """Returns a `tacl.Catalogue`."""
    catalogue = tacl.Catalogue()
    catalogue.load(path)
    return catalogue

def get_data_store (args):
    """Returns a `tacl.DataStore`."""
    return tacl.DataStore(args.db, args.memory, args.ram)

def get_input_fh (arg):
    """Returns an open file of CSV data, or None if `arg` is None."""
    input_fh = None
    if arg:
        input_fh = open(arg, 'r', encoding='utf-8', newline='')
    return input_fh

def get_tokenizer (args):
    return tacl.Tokenizer(*constants.TOKENIZERS[args.tokenizer])

def highlight_text (args, parser):
    """Outputs the result of highlighting a text."""
    tokenizer = get_tokenizer(args)
    corpus = get_corpus(args)
    highlighter = tacl.Highlighter(corpus, tokenizer)
    text = highlighter.highlight(args.results, args.base_name, args.base_siglum)
    print(text)

def ngram_counts (args, parser):
    """Outputs the results of performing a counts query."""
    store = get_data_store(args)
    corpus = get_corpus(args)
    catalogue = get_catalogue(args.catalogue)
    store.validate(corpus, catalogue)
    store.counts(catalogue, sys.stdout)

def ngram_diff (args, parser):
    """Outputs the results of performing a diff query."""
    store = get_data_store(args)
    corpus = get_corpus(args)
    catalogue = get_catalogue(args.catalogue)
    store.validate(corpus, catalogue)
    if args.asymmetric:
        store.diff_asymmetric(catalogue, args.asymmetric, sys.stdout)
    else:
        store.diff(catalogue, sys.stdout)

def ngram_intersection (args, parser):
    """Outputs the results of performing an intersection query."""
    store = get_data_store(args)
    corpus = get_corpus(args)
    catalogue = get_catalogue(args.catalogue)
    store.validate(corpus, catalogue)
    store.intersection(catalogue, sys.stdout)

def prepare_xml (args, parser):
    """Prepares XML texts for stripping.

    This process creates a single, normalised TEI XML file for each
    text.

    """
    corpus = tacl.TEICorpus(args.input, args.output)
    corpus.tidy()

def report (args, parser):
    if args.results == '-':
        results = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',
                                   newline='')
    else:
        results = open(args.results, 'r', encoding='utf-8', newline='')
    tokenizer = get_tokenizer(args)
    report = tacl.Report(results, tokenizer)
    if args.extend:
        corpus = tacl.Corpus(args.extend, tokenizer)
        report.extend(corpus)
    if args.reduce:
        report.reduce()
    if args.reciprocal:
        report.reciprocal_remove()
    if args.zero_fill:
        if not args.catalogue:
            parser.error('The zero-fill option requires that the -c option also be supplied.')
        corpus = tacl.Corpus(args.zero_fill, tokenizer)
        catalogue = get_catalogue(args.catalogue)
        report.zero_fill(corpus, catalogue)
    if args.min_texts or args.max_texts:
        report.prune_by_text_count(args.min_texts, args.max_texts)
    if args.min_size or args.max_size:
        report.prune_by_ngram_size(args.min_size, args.max_size)
    if args.min_count or args.max_count:
        report.prune_by_ngram_count(args.min_count, args.max_count)
    if args.remove:
        report.remove_label(args.remove)
    if args.sort:
        report.sort()
    report.csv(sys.stdout)

def search_texts (args, parser):
    """Searches texts for presence of n-grams."""
    store = get_data_store(args)
    corpus = get_corpus(args)
    catalogue = tacl.Catalogue()
    if args.catalogue:
        catalogue.load(args.catalogue)
    store.validate(corpus, catalogue)
    with open(args.ngrams, 'r', encoding='utf-8') as fh:
        ngrams = [ngram.strip() for ngram in fh.readlines()]
    store.search(catalogue, ngrams, sys.stdout)

def strip_texts (args, parser):
    """Processes prepared XML texts for use with the tacl ngrams
    command."""
    stripper = tacl.Stripper(args.input, args.output)
    stripper.strip_files()

def supplied_diff (args, parser):
    labels = args.labels
    results = args.supplied
    store = get_data_store(args)
    store.diff_supplied(results, labels, sys.stdout)

def supplied_intersect (args, parser):
    labels = args.labels
    results = args.supplied
    store = get_data_store(args)
    store.intersection_supplied(results, labels, sys.stdout)
