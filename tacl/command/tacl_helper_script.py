import argparse
import os
import sys

import colorlog

import tacl
import tacl.command.utils as utils
from tacl import constants


logger = colorlog.getLogger('tacl')


def main():
    parser = generate_parser()
    args = parser.parse_args()
    if hasattr(args, 'verbose'):
        utils.configure_logging(args.verbose, logger)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


def collapse_witnesses(args):
    results = tacl.Results(args.results, utils.get_tokenizer(args))
    results.collapse_witnesses()
    results.csv(sys.stdout)


def _copy_options(args):
    """Returns a string form of the options in `args`."""
    options = []
    if args.memory:
        options.append('--memory')
    if args.ram:
        options.append('--ram {}'.format(args.ram))
    if args.verbose:
        options.append('-{}'.format('v' * args.verbose))
    return ' ' + ' '.join(options)


def generate_parser():
    parser = argparse.ArgumentParser(
        description=constants.TACL_HELPER_DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(title='subcommands')
    generate_collapse_witness_results_subparser(subparsers)
    generate_label_count_subparser(subparsers)
    generate_work_against_corpus_subparser(subparsers)
    generate_work_in_corpus_subparser(subparsers)
    generate_validate_catalogue_subparser(subparsers)
    return parser


def generate_collapse_witness_results_subparser(subparsers):
    parser = subparsers.add_parser(
        'collapse-witnesses',
        description=constants.TACL_HELPER_COLLAPSE_DESCRIPTION,
        help=constants.TACL_HELPER_COLLAPSE_HELP)
    parser.set_defaults(func=collapse_witnesses)
    utils.add_common_arguments(parser)
    utils.add_tokenizer_argument(parser)
    parser.add_argument('results', help=constants.TACL_HELPER_RESULTS_HELP,
                        metavar='RESULTS')


def generate_label_count_subparser(subparsers):
    parser = subparsers.add_parser(
        'label-count',
        description=constants.TACL_HELPER_LABEL_COUNT_DESCRIPTION,
        help=constants.TACL_HELPER_LABEL_COUNT_HELP)
    parser.set_defaults(func=label_count)
    utils.add_common_arguments(parser)
    utils.add_tokenizer_argument(parser)
    parser.add_argument('results', help=constants.TACL_HELPER_RESULTS_HELP,
                        metavar='RESULTS')


def generate_work_against_corpus_subparser(subparsers):
    parser = subparsers.add_parser(
        'work-against-corpus',
        description=constants.TACL_HELPER_AGAINST_DESCRIPTION,
        help=constants.TACL_HELPER_AGAINST_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=work_against_corpus)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    parser.add_argument('a_works', help=constants.TACL_HELPER_AGAINST_A_HELP,
                        metavar='FILES_LIST', type=argparse.FileType('r'))
    parser.add_argument('b_works', help=constants.TACL_HELPER_AGAINST_B_HELP,
                        metavar='CORPUS_FILES_LIST',
                        type=argparse.FileType('r'))
    parser.add_argument('output_dir', help=constants.TACL_HELPER_OUTPUT,
                        metavar='OUTPUT_DIR')


def generate_work_in_corpus_subparser(subparsers):
    parser = subparsers.add_parser(
        'work-in-corpus', description=constants.TACL_HELPER_IN_DESCRIPTION,
        help=constants.TACL_HELPER_IN_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=work_in_corpus)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    parser.add_argument('works', help=constants.TACL_HELPER_IN_TEXTS_HELP,
                        metavar='FILE_LIST', type=argparse.FileType('r'))
    parser.add_argument('output_dir', help=constants.TACL_HELPER_OUTPUT,
                        metavar='OUTPUT_DIR')


def generate_validate_catalogue_subparser(subparsers):
    parser = subparsers.add_parser(
        'validate-catalogue',
        description=constants.TACL_HELPER_VALIDATE_CATALOGUE_DESCRIPTION,
        help=constants.TACL_HELPER_VALIDATE_CATALOGUE_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=validate_catalogue)
    utils.add_common_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)


def label_count(args):
    results = tacl.Results(args.results, utils.get_tokenizer(args))
    results.add_label_count()
    results.csv(sys.stdout)


def work_against_corpus(args):
    a_works = args.a_works.read().strip().split()
    b_works = args.b_works.read().strip().split()
    output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    catalogue = tacl.Catalogue({work: 'REST' for work in b_works})
    commands = []
    options = _copy_options(args)
    for work in a_works:
        catalogue_path = os.path.join(
            output_dir, '{}-catalogue.txt'.format(work))
        results_path = os.path.join(
            output_dir, '{}-results.csv'.format(work))
        reduced_path = os.path.join(
            output_dir, '{}-reduced.csv'.format(work))
        catalogue[work] = 'A'
        catalogue.save(catalogue_path)
        query_command = 'tacl intersect{} {} {} {} > {}\n'.format(
            options, args.db, args.corpus, catalogue_path, results_path)
        report_command = 'tacl report --reduce --remove REST {} > {}\n'.format(
            results_path, reduced_path)
        commands.extend((query_command, report_command))
        del catalogue[work]
    commands_path = os.path.join(output_dir, 'commands')
    with open(commands_path, 'w') as fh:
        fh.writelines(commands)


def work_in_corpus(args):
    works = args.works.read().strip().split()
    output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    catalogue = tacl.Catalogue({work: 'REST' for work in works})
    commands = []
    options = _copy_options(args)
    for work in works:
        catalogue_path = os.path.join(output_dir,
                                      '{}-catalogue.txt'.format(work))
        results_path = os.path.join(output_dir,
                                    '{}-results.csv'.format(work))
        reduced_path = os.path.join(output_dir,
                                    '{}-reduced.csv'.format(work))
        catalogue[work] = 'A'
        catalogue.save(catalogue_path)
        query_command = 'tacl intersect{} {} {} {} > {}\n'.format(
            options, args.db, args.corpus, catalogue_path, results_path)
        report_command = 'tacl report --reduce --remove REST {} > {}\n'.format(
            results_path, reduced_path)
        commands.extend((query_command, report_command))
        catalogue[work] = 'REST'
    commands_path = os.path.join(output_dir, 'commands')
    with open(commands_path, 'w') as fh:
        fh.writelines(commands)


def validate_catalogue(args):
    try:
        catalogue = utils.get_catalogue(args.catalogue)
    except tacl.exceptions.MalformedCatalogueError as e:
        print('Error: {}'.format(e))
        print('Other errors may be present; re-run this validation after '
              'correcting the above problem.')
        sys.exit(1)
    corpus = utils.get_corpus(args)
    has_error = False
    for name in catalogue:
        count = 0
        for work in corpus.get_witnesses(name):
            count += 1
            break
        if not count:
            has_error = True
            print('Error: Catalogue references work {} that does not '
                  'exist in the corpus'.format(name))
    if has_error:
        sys.exit(1)
