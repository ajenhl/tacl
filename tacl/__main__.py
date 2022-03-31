"""Command-line script to perform n-gram analysis of a corpus of
texts."""

import argparse
from importlib.metadata import distribution
import io
import os
import sys

import colorlog

import tacl
import tacl.cli.utils as utils
from tacl import constants, normaliser
from tacl.cli.formatters import ParagraphFormatter
from tacl.exceptions import TACLError


def main():
    parser = generate_parser()
    args = parser.parse_args()
    logger = colorlog.getLogger('tacl')
    if hasattr(args, 'verbose'):
        utils.configure_logging(args.verbose, logger)
    if hasattr(args, 'func'):
        try:
            args.func(args, parser)
        except TACLError as err:
            parser.error(err)
    else:
        parser.print_help()


def align_results(args, parser):
    if args.results == '-':
        results = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',
                                   newline='')
    else:
        results = open(args.results, 'r', encoding='utf-8', newline='')
    tokenizer = utils.get_tokenizer(args)
    corpus = tacl.Corpus(args.corpus, tokenizer)
    report = tacl.SequenceReport(corpus, tokenizer, results)
    report.generate(args.output, args.minimum)


def excise(args, parser):
    logger = colorlog.getLogger('tacl')
    tokenizer = utils.get_tokenizer(args)
    corpus = tacl.Corpus(args.corpus, tokenizer)
    with open(args.ngrams) as fh:
        ngrams = [line.strip() for line in fh.readlines()]
    # It is no issue if the output directory already exists; it is a
    # reasonable use case to create an excised corpus from multiple
    # excise operations.
    try:
        os.mkdir(args.output)
    except FileExistsError:
        pass
    for work in args.works:
        # It is worth warning about writing in existing work
        # directories, however, since that might be unintended. Do not
        # prevent this, however, since it is a reasonable use case.
        try:
            os.mkdir(os.path.join(args.output, work))
        except FileExistsError:
            logger.warning(constants.EXCISE_OVERWRITE_WORK_WARNING, work)
        for witness in corpus.get_witnesses(work):
            path = os.path.join(args.output, witness.get_filename())
            content = witness.excise(ngrams, args.replacement)
            with open(path, 'w') as fh:
                fh.write(content)


def generate_parser():
    """Returns a parser configured with sub-commands and arguments."""
    parser = argparse.ArgumentParser(
        description=constants.TACL_DESCRIPTION,
        formatter_class=ParagraphFormatter)
    parser.add_argument('--version', action='version',
                        version=distribution('tacl').version)
    subparsers = parser.add_subparsers(title='subcommands')
    generate_align_subparser(subparsers)
    generate_catalogue_subparser(subparsers)
    generate_counts_subparser(subparsers)
    generate_diff_subparser(subparsers)
    generate_excise_subparser(subparsers)
    generate_highlight_subparser(subparsers)
    generate_intersect_subparser(subparsers)
    generate_join_works_subparser(subparsers)
    generate_lifetime_subparser(subparsers)
    generate_ngrams_subparser(subparsers)
    generate_normalise_subparser(subparsers)
    generate_prepare_subparser(subparsers)
    generate_query_subparser(subparsers)
    generate_results_subparser(subparsers)
    generate_search_subparser(subparsers)
    generate_split_subparser(subparsers)
    generate_statistics_subparser(subparsers)
    generate_strip_subparser(subparsers)
    generate_supplied_diff_subparser(subparsers)
    generate_supplied_intersect_subparser(subparsers)
    return parser


def generate_align_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to generate aligned
    sequences from a set of results."""
    parser = subparsers.add_parser(
        'align', description=constants.ALIGN_DESCRIPTION,
        epilog=constants.ALIGN_EPILOG,
        formatter_class=ParagraphFormatter, help=constants.ALIGN_HELP)
    parser.set_defaults(func=align_results)
    utils.add_common_arguments(parser)
    parser.add_argument('-m', '--minimum', default=20,
                        help=constants.ALIGN_MINIMUM_SIZE_HELP, type=int)
    utils.add_corpus_arguments(parser)
    parser.add_argument('output', help=constants.ALIGN_OUTPUT_HELP,
                        metavar='OUTPUT')
    parser.add_argument('results', help=constants.RESULTS_RESULTS_HELP,
                        metavar='RESULTS')


def generate_catalogue(args, parser):
    """Generates and saves a catalogue file."""
    catalogue = tacl.Catalogue()
    catalogue.generate(args.corpus, args.label)
    catalogue.save(args.catalogue)


def generate_catalogue_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to generate and save
    a catalogue file."""
    parser = subparsers.add_parser(
        'catalogue', description=constants.CATALOGUE_DESCRIPTION,
        epilog=constants.CATALOGUE_EPILOG,
        formatter_class=ParagraphFormatter, help=constants.CATALOGUE_HELP)
    utils.add_common_arguments(parser)
    parser.set_defaults(func=generate_catalogue)
    parser.add_argument('corpus', help=constants.DB_CORPUS_HELP,
                        metavar='CORPUS')
    utils.add_query_arguments(parser)
    parser.add_argument('-l', '--label', default='',
                        help=constants.CATALOGUE_LABEL_HELP)


def generate_counts_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to make a counts
    query."""
    parser = subparsers.add_parser(
        'counts', description=constants.COUNTS_DESCRIPTION,
        epilog=constants.COUNTS_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.COUNTS_HELP)
    parser.set_defaults(func=ngram_counts)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)


def generate_diff_subparser(subparsers):
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
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)


def generate_excise_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to excise n-grams from
    witnesses."""
    parser = subparsers.add_parser(
        'excise', description=constants.EXCISE_DESCRIPTION,
        help=constants.EXCISE_HELP)
    parser.set_defaults(func=excise)
    utils.add_common_arguments(parser)
    parser.add_argument('ngrams', metavar='NGRAMS',
                        help=constants.EXCISE_NGRAMS_HELP)
    parser.add_argument('replacement', metavar='REPLACEMENT',
                        help=constants.EXCISE_REPLACEMENT_HELP)
    parser.add_argument('output', metavar='OUTPUT',
                        help=constants.EXCISE_OUTPUT_HELP)
    utils.add_corpus_arguments(parser)
    parser.add_argument('works', metavar='WORK',
                        help=constants.EXCISE_WORKS_HELP, nargs='+')


def generate_highlight_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to highlight a witness'
    text with its matches in a result."""
    parser = subparsers.add_parser(
        'highlight', description=constants.HIGHLIGHT_DESCRIPTION,
        epilog=constants.HIGHLIGHT_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.HIGHLIGHT_HELP)
    parser.set_defaults(func=highlight_text)
    utils.add_common_arguments(parser)
    parser.add_argument('-m', '--minus-ngrams', metavar='NGRAMS',
                        help=constants.HIGHLIGHT_MINUS_NGRAMS_HELP)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--ngrams', action='append', metavar='NGRAMS',
                       help=constants.HIGHLIGHT_NGRAMS_HELP)
    group.add_argument('-r', '--results', metavar='RESULTS',
                       help=constants.HIGHLIGHT_RESULTS_HELP)
    parser.add_argument('-l', '--label', action='append', metavar='LABEL',
                        help=constants.HIGHLIGHT_LABEL_HELP)
    utils.add_corpus_arguments(parser)
    parser.add_argument('base_name', help=constants.HIGHLIGHT_BASE_NAME_HELP,
                        metavar='BASE_NAME')
    parser.add_argument('output', metavar='OUTPUT',
                        help=constants.REPORT_OUTPUT_HELP)


def generate_intersect_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to make an
    intersection query."""
    parser = subparsers.add_parser(
        'intersect', description=constants.INTERSECT_DESCRIPTION,
        epilog=constants.INTERSECT_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.INTERSECT_HELP)
    parser.set_defaults(func=ngram_intersection)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)


def generate_join_works_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to join multiple prepared
    works together."""
    parser = subparsers.add_parser(
        'join-works', description=constants.JOIN_WORKS_DESCRIPTION,
        epilog=constants.JOIN_WORKS_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.JOIN_WORKS_HELP)
    parser.set_defaults(func=join_works)
    parser.add_argument('corpus', help=constants.JOIN_WORKS_CORPUS_HELP,
                        metavar='CORPUS')
    parser.add_argument('output', help=constants.JOIN_WORKS_OUTPUT_HELP,
                        metavar='OUTPUT')
    parser.add_argument('works', help=constants.JOIN_WORKS_WORK_HELP,
                        metavar='WORK', nargs='+')


def generate_lifetime_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to make a lifetime report."""
    parser = subparsers.add_parser(
        'lifetime', description=constants.LIFETIME_DESCRIPTION,
        epilog=constants.LIFETIME_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.LIFETIME_HELP)
    parser.set_defaults(func=lifetime_report)
    utils.add_tokenizer_argument(parser)
    utils.add_common_arguments(parser)
    utils.add_query_arguments(parser)
    parser.add_argument('results', help=constants.LIFETIME_RESULTS_HELP,
                        metavar='RESULTS')
    parser.add_argument('label', help=constants.LIFETIME_LABEL_HELP,
                        metavar='LABEL')
    parser.add_argument('output', help=constants.REPORT_OUTPUT_HELP,
                        metavar='OUTPUT')


def generate_ngrams(args, parser):
    """Adds n-grams data to the data store."""
    store = utils.get_data_store(args, must_exist=False)
    corpus = utils.get_corpus(args)
    if args.catalogue:
        catalogue = utils.get_catalogue(args)
    else:
        catalogue = None
    store.add_ngrams(corpus, args.min_size, args.max_size, catalogue)


def generate_ngrams_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to add n-grams data
    to the data store."""
    parser = subparsers.add_parser(
        'ngrams', description=constants.NGRAMS_DESCRIPTION,
        epilog=constants.NGRAMS_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.NGRAMS_HELP)
    parser.set_defaults(func=generate_ngrams)
    utils.add_common_arguments(parser)
    parser.add_argument('-c', '--catalogue', dest='catalogue',
                        help=constants.NGRAMS_CATALOGUE_HELP,
                        metavar='CATALOGUE')
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    parser.add_argument('min_size', help=constants.NGRAMS_MINIMUM_HELP,
                        metavar='MINIMUM', type=int)
    parser.add_argument('max_size', help=constants.NGRAMS_MAXIMUM_HELP,
                        metavar='MAXIMUM', type=int)


def generate_normalise_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to generate a normalised
    corpus from an unnormalised corpus."""
    parser = subparsers.add_parser(
        'normalise', description=constants.NORMALISE_DESCRIPTION,
        epilog=constants.NORMALISE_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.NORMALISE_HELP)
    parser.set_defaults(func=normalise_corpus)
    utils.add_tokenizer_argument(parser)
    utils.add_common_arguments(parser)
    parser.add_argument('corpus', help=constants.NORMALISE_CORPUS_HELP,
                        metavar='CORPUS')
    parser.add_argument('mapping', help=constants.NORMALISE_MAPPING_HELP,
                        metavar='MAPPING')
    parser.add_argument('output', help=constants.NORMALISE_OUTPUT_HELP,
                        metavar='OUTPUT')


def generate_prepare_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to prepare source XML
    files for stripping."""
    parser = subparsers.add_parser(
        'prepare', description=constants.PREPARE_DESCRIPTION,
        epilog=constants.PREPARE_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.PREPARE_HELP)
    parser.set_defaults(func=prepare_xml)
    utils.add_common_arguments(parser)
    parser.add_argument('-s', '--source', dest='source',
                        choices=constants.TEI_SOURCE_CHOICES,
                        default=constants.TEI_SOURCE_CBETA_GITHUB,
                        help=constants.PREPARE_SOURCE_HELP,
                        metavar='SOURCE')
    parser.add_argument('input', help=constants.PREPARE_INPUT_HELP,
                        metavar='INPUT')
    parser.add_argument('output', help=constants.PREPARE_OUTPUT_HELP,
                        metavar='OUTPUT')


def generate_query_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to send SQL to the data
    store and return the results."""
    parser = subparsers.add_parser(
        'query', description=constants.QUERY_DESCRIPTION,
        formatter_class=ParagraphFormatter, help=constants.QUERY_HELP)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser, True)
    parser.add_argument('-q', '--query', help=constants.QUERY_QUERY_HELP,
                        metavar='QUERY', required=True)
    parser.add_argument('-p', '--parameters',
                        help=constants.QUERY_PARAMETERS_HELP,
                        metavar='PARAMETER', nargs='*')
    parser.set_defaults(func=query_data_store)


def generate_results_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to manipulate CSV
    results data."""
    parser = subparsers.add_parser(
        'results', description=constants.RESULTS_DESCRIPTION,
        epilog=constants.RESULTS_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.RESULTS_HELP)
    utils.add_common_arguments(parser)
    parser.set_defaults(func=results)
    be_group = parser.add_argument_group('bifurcated extend')
    be_group.add_argument('-b', '--bifurcated-extend',
                          dest='bifurcated_extend', metavar='CORPUS',
                          help=constants.RESULTS_BIFURCATED_EXTEND_HELP)
    be_group.add_argument('--max-be-count', dest='bifurcated_extend_size',
                          help=constants.RESULTS_BIFURCATED_EXTEND_MAX_HELP,
                          metavar='COUNT', type=int)
    normalise_group = parser.add_argument_group('denormalise')
    normalise_group.add_argument(
        '--denormalise', dest='denormalise_mapping',
        help=constants.RESULTS_DENORMALISE_MAPPING_HELP, metavar='MAPPING')
    normalise_group.add_argument(
        '--denormalised-corpus', dest='denormalised_corpus',
        help=constants.RESULTS_DENORMALISE_CORPUS_HELP, metavar='CORPUS')
    parser.add_argument('-e', '--extend', dest='extend',
                        help=constants.RESULTS_EXTEND_HELP, metavar='CORPUS')
    parser.add_argument('--excise', help=constants.RESULTS_EXCISE_HELP,
                        metavar='NGRAM', type=str)
    parser.add_argument('-l', '--label', dest='label',
                        help=constants.RESULTS_LABEL_HELP, metavar='LABEL')
    parser.add_argument('--min-count', dest='min_count',
                        help=constants.RESULTS_MINIMUM_COUNT_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--max-count', dest='max_count',
                        help=constants.RESULTS_MAXIMUM_COUNT_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--min-count-work', dest='min_count_work',
                        help=constants.RESULTS_MINIMUM_COUNT_WORK_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--max-count-work', dest='max_count_work',
                        help=constants.RESULTS_MAXIMUM_COUNT_WORK_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--min-size', dest='min_size',
                        help=constants.RESULTS_MINIMUM_SIZE_HELP,
                        metavar='SIZE', type=int)
    parser.add_argument('--max-size', dest='max_size',
                        help=constants.RESULTS_MAXIMUM_SIZE_HELP,
                        metavar='SIZE', type=int)
    parser.add_argument('--min-works', dest='min_works',
                        help=constants.RESULTS_MINIMUM_WORK_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--max-works', dest='max_works',
                        help=constants.RESULTS_MAXIMUM_WORK_HELP,
                        metavar='COUNT', type=int)
    parser.add_argument('--ngrams', dest='ngrams',
                        help=constants.RESULTS_NGRAMS_HELP, metavar='NGRAMS')
    parser.add_argument('--reciprocal', action='store_true',
                        help=constants.RESULTS_RECIPROCAL_HELP)
    parser.add_argument('--reduce', action='store_true',
                        help=constants.RESULTS_REDUCE_HELP)
    parser.add_argument('--relabel', help=constants.RESULTS_RELABEL_HELP,
                        metavar='CATALOGUE')
    parser.add_argument('--remove', help=constants.RESULTS_REMOVE_HELP,
                        metavar='LABEL', type=str)
    parser.add_argument('--sort', action='store_true',
                        help=constants.RESULTS_SORT_HELP)
    utils.add_tokenizer_argument(parser)
    parser.add_argument('-z', '--zero-fill', dest='zero_fill',
                        help=constants.RESULTS_ZERO_FILL_HELP,
                        metavar='CORPUS')
    parser.add_argument('results', help=constants.RESULTS_RESULTS_HELP,
                        metavar='RESULTS')
    unsafe_group = parser.add_argument_group(
        constants.RESULTS_UNSAFE_GROUP_TITLE,
        constants.RESULTS_UNSAFE_GROUP_DESCRIPTION)
    unsafe_group.add_argument('--add-label-count', action='store_true',
                              help=constants.RESULTS_ADD_LABEL_COUNT_HELP)
    unsafe_group.add_argument('--add-label-work-count', action='store_true',
                              help=constants.RESULTS_ADD_LABEL_WORK_COUNT_HELP)
    unsafe_group.add_argument('--collapse-witnesses', action='store_true',
                              help=constants.RESULTS_COLLAPSE_WITNESSES_HELP)
    unsafe_group.add_argument('--group-by-ngram', dest='group_by_ngram',
                              help=constants.RESULTS_GROUP_BY_NGRAM_HELP,
                              metavar='CATALOGUE')
    unsafe_group.add_argument('--group-by-witness', action='store_true',
                              help=constants.RESULTS_GROUP_BY_WITNESS_HELP)


def generate_search_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to generate search
    results for a set of n-grams."""
    parser = subparsers.add_parser(
        'search', description=constants.SEARCH_DESCRIPTION,
        epilog=constants.SEARCH_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.SEARCH_HELP)
    parser.set_defaults(func=search_texts)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)
    parser.add_argument('ngrams', help=constants.SEARCH_NGRAMS_HELP,
                        nargs='*', metavar='NGRAMS')


def generate_split_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to generate new corpus
    files by splitting existing ones."""
    parser = subparsers.add_parser(
        'split', description=constants.SPLIT_DESCRIPTION,
        epilog=constants.SPLIT_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.SPLIT_HELP)
    parser.set_defaults(func=split_texts)
    utils.add_common_arguments(parser)
    utils.add_corpus_arguments(parser)
    parser.add_argument('splits', help=constants.SPLIT_CONF_HELP,
                        nargs="+", metavar='CONF')


def generate_statistics(args, parser):
    corpus = utils.get_corpus(args)
    tokenizer = utils.get_tokenizer(args)
    report = tacl.StatisticsReport(corpus, tokenizer, args.results)
    report.generate_statistics()
    report.csv(sys.stdout)


def generate_statistics_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to generate statistics
    from a set of results."""
    parser = subparsers.add_parser(
        'stats', description=constants.STATISTICS_DESCRIPTION,
        formatter_class=ParagraphFormatter, help=constants.STATISTICS_HELP)
    parser.set_defaults(func=generate_statistics)
    utils.add_common_arguments(parser)
    utils.add_corpus_arguments(parser)
    parser.add_argument('results', help=constants.STATISTICS_RESULTS_HELP,
                        metavar='RESULTS')


def generate_strip_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to process prepared files
    for use with the tacl ngrams command."""
    parser = subparsers.add_parser(
        'strip', description=constants.STRIP_DESCRIPTION,
        epilog=constants.STRIP_EPILOG, formatter_class=ParagraphFormatter,
        help=constants.STRIP_HELP)
    parser.set_defaults(func=strip_files)
    utils.add_common_arguments(parser)
    parser.add_argument('input', help=constants.STRIP_INPUT_HELP,
                        metavar='INPUT')
    parser.add_argument('output', help=constants.STRIP_OUTPUT_HELP,
                        metavar='OUTPUT')


def generate_supplied_diff_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to run a diff query using
    the supplied results sets."""
    parser = subparsers.add_parser(
        'sdiff', description=constants.SUPPLIED_DIFF_DESCRIPTION,
        epilog=constants.SUPPLIED_DIFF_EPILOG,
        formatter_class=ParagraphFormatter, help=constants.SUPPLIED_DIFF_HELP)
    parser.set_defaults(func=supplied_diff)
    utils.add_common_arguments(parser)
    utils.add_tokenizer_argument(parser)
    utils.add_db_arguments(parser, True)
    utils.add_supplied_query_arguments(parser)


def generate_supplied_intersect_subparser(subparsers):
    """Adds a sub-command parser to `subparsers` to run an intersect query
    using the supplied results sets."""
    parser = subparsers.add_parser(
        'sintersect', description=constants.SUPPLIED_INTERSECT_DESCRIPTION,
        epilog=constants.SUPPLIED_INTERSECT_EPILOG,
        formatter_class=ParagraphFormatter,
        help=constants.SUPPLIED_INTERSECT_HELP)
    parser.set_defaults(func=supplied_intersect)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser, True)
    utils.add_supplied_query_arguments(parser)


def highlight_text(args, parser):
    """Outputs the result of highlighting a text."""
    tokenizer = utils.get_tokenizer(args)
    corpus = utils.get_corpus(args)
    output_dir = os.path.abspath(args.output)
    if os.path.exists(output_dir):
        parser.exit(status=3, message='Output directory already exists, '
                    'aborting.\n')
    os.makedirs(output_dir, exist_ok=True)
    if args.ngrams:
        if args.label is None or len(args.label) != len(args.ngrams):
            parser.error('There must be as many labels as there are files '
                         'of n-grams')
        report = tacl.NgramHighlightReport(corpus, tokenizer)
        ngrams = []
        for ngram_file in args.ngrams:
            ngrams.append(utils.get_ngrams(ngram_file))
        minus_ngrams = []
        if args.minus_ngrams:
            minus_ngrams = utils.get_ngrams(args.minus_ngrams)
        report.generate(args.output, args.base_name, ngrams, args.label,
                        minus_ngrams)
    else:
        report = tacl.ResultsHighlightReport(corpus, tokenizer)
        report.generate(args.output, args.base_name, args.results)


def join_works(args, parser):
    """Joins works into a single work."""
    joiner = tacl.WorkJoiner(args.corpus)
    joiner.join(args.output, args.works)


def lifetime_report(args, parser):
    """Generates a lifetime report."""
    catalogue = utils.get_catalogue(args)
    tokenizer = utils.get_tokenizer(args)
    results = tacl.Results(args.results, tokenizer)
    output_dir = os.path.abspath(args.output)
    os.makedirs(output_dir, exist_ok=True)
    report = tacl.LifetimeReport()
    report.generate(output_dir, catalogue, results, args.label)


def ngram_counts(args, parser):
    """Outputs the results of performing a counts query."""
    store = utils.get_data_store(args)
    corpus = utils.get_corpus(args)
    catalogue = utils.get_catalogue(args)
    store.validate(corpus, catalogue)
    store.counts(catalogue, sys.stdout)


def ngram_diff(args, parser):
    """Outputs the results of performing a diff query."""
    store = utils.get_data_store(args)
    corpus = utils.get_corpus(args)
    catalogue = utils.get_catalogue(args)
    tokenizer = utils.get_tokenizer(args)
    store.validate(corpus, catalogue)
    if args.asymmetric:
        store.diff_asymmetric(catalogue, args.asymmetric, tokenizer,
                              sys.stdout)
    else:
        store.diff(catalogue, tokenizer, sys.stdout)


def ngram_intersection(args, parser):
    """Outputs the results of performing an intersection query."""
    store = utils.get_data_store(args)
    corpus = utils.get_corpus(args)
    catalogue = utils.get_catalogue(args)
    store.validate(corpus, catalogue)
    store.intersection(catalogue, sys.stdout)


def normalise_corpus(args, parser):
    """Outputs a normalised version of a corpus."""
    corpus = utils.get_corpus(args)
    tokenizer = utils.get_tokenizer(args)
    output_dir = os.path.abspath(args.output)
    if os.path.exists(output_dir):
        parser.exit(status=3, message='Output directory already exists, '
                    'aborting.\n')
    mapping = normaliser.VariantMapping(args.mapping, tokenizer)
    corpus.normalise(mapping, output_dir)


def prepare_xml(args, parser):
    """Prepares XML files for stripping.

    This process creates a single, normalised TEI XML file for each
    work.

    """
    if args.source == constants.TEI_SOURCE_CBETA_GITHUB:
        corpus_class = tacl.TEICorpusCBETAGitHub
    else:
        raise Exception('Unsupported TEI source option provided')
    corpus = corpus_class(args.input, args.output)
    corpus.tidy()


def query_data_store(args, parser):
    """Query the data store using a query from a file."""
    store = utils.get_data_store(args)
    with open(args.query) as fh:
        query = fh.read()
    parameters = args.parameters or ()
    # If the string parameter can be converted to an integer, do so.
    converted_parameters = []
    for parameter in parameters:
        try:
            converted_parameters.append(int(parameter))
        except ValueError:
            converted_parameters.append(parameter)
    store.query(query, converted_parameters, sys.stdout)


def results(args, parser):
    if args.results == '-':
        results_fh = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8',
                                      newline='')
    else:
        results_fh = open(args.results, 'r', encoding='utf-8', newline='')
    tokenizer = utils.get_tokenizer(args)
    results = tacl.Results(results_fh, tokenizer)
    if args.extend:
        corpus = tacl.Corpus(args.extend, tokenizer)
        results.extend(corpus)
    if args.bifurcated_extend:
        if not args.bifurcated_extend_size:
            parser.error('The bifurcated extend option requires that the '
                         '--max-be-count option also be supplied')
        corpus = tacl.Corpus(args.bifurcated_extend, tokenizer)
        results.bifurcated_extend(corpus, args.bifurcated_extend_size)
    if args.denormalised_corpus and args.denormalise_mapping:
        unnormalised_corpus = tacl.Corpus(args.denormalised_corpus, tokenizer)
        mapping = tacl.VariantMapping(args.denormalise_mapping, tokenizer)
        results.denormalise(unnormalised_corpus, mapping)
    elif args.denormalised_corpus or args.denormalise_mapping:
        parser.error('Both --denormalised-corpus and --denormalise-mapping '
                     'must be specified in order to denormalise results')
    if args.reduce:
        results.reduce()
    if args.reciprocal:
        results.reciprocal_remove()
    if args.excise:
        results.excise(args.excise)
    if args.zero_fill:
        corpus = tacl.Corpus(args.zero_fill, tokenizer)
        results.zero_fill(corpus)
    if args.ngrams:
        with open(args.ngrams, encoding='utf-8') as fh:
            ngrams = fh.read().split()
        results.prune_by_ngram(ngrams)
    label = args.label or None
    if args.min_works or args.max_works:
        results.prune_by_work_count(args.min_works, args.max_works, label)
    if args.min_size or args.max_size:
        results.prune_by_ngram_size(args.min_size, args.max_size)
    if args.min_count or args.max_count:
        results.prune_by_ngram_count(args.min_count, args.max_count, label)
    if args.min_count_work or args.max_count_work:
        results.prune_by_ngram_count_per_work(args.min_count_work,
                                              args.max_count_work, label)
    if args.remove:
        results.remove_label(args.remove)
    if args.relabel:
        catalogue = tacl.Catalogue()
        catalogue.load(args.relabel)
        results.relabel(catalogue)
    if args.sort:
        results.sort()
    # Run format-changing operations last.
    if args.add_label_count:
        results.add_label_count()
    if args.add_label_work_count:
        results.add_label_work_count()
    if args.group_by_ngram:
        catalogue = tacl.Catalogue()
        catalogue.load(args.group_by_ngram)
        results.group_by_ngram(catalogue.ordered_labels)
    if args.group_by_witness:
        results.group_by_witness()
    if args.collapse_witnesses:
        results.collapse_witnesses()
    results.csv(sys.stdout)


def search_texts(args, parser):
    """Searches texts for presence of n-grams."""
    store = utils.get_data_store(args)
    corpus = utils.get_corpus(args)
    catalogue = utils.get_catalogue(args)
    store.validate(corpus, catalogue)
    ngrams = []
    for ngram_file in args.ngrams:
        ngrams.extend(utils.get_ngrams(ngram_file))
    store.search(catalogue, ngrams, sys.stdout)


def split_texts(args, parser):
    corpus = utils.get_corpus(args)
    splitter = tacl.Splitter(corpus)
    for split_conf in args.splits:
        splitter.split(split_conf)


def strip_files(args, parser):
    """Processes prepared XML files for use with the tacl ngrams
    command."""
    stripper = tacl.Stripper(args.input, args.output)
    stripper.strip_files()


def supplied_diff(args, parser):
    labels = args.labels
    results = args.supplied
    store = utils.get_data_store(args, must_exist=False)
    tokenizer = utils.get_tokenizer(args)
    store.diff_supplied(results, labels, tokenizer, sys.stdout)


def supplied_intersect(args, parser):
    labels = args.labels
    results = args.supplied
    store = utils.get_data_store(args, must_exist=False)
    store.intersection_supplied(results, labels, sys.stdout)


if __name__ == '__main__':
    main()
