import argparse
import logging
import os

import tacl
from tacl import constants


def main ():
    parser = generate_parser()
    args = parser.parse_args()
    if hasattr(args, 'verbose'):
        configure_logging(args.verbose)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def add_common_arguments (parser):
    """Adds common arguments for all parsers."""
    parser.add_argument('-v', '--verbose', action='count',
                        help=constants.VERBOSE_HELP)

def add_db_arguments (parser):
    """Adds common arguments for the database subcommands to `parser`."""
    parser.add_argument('-m', '--memory', action='store_true',
                        help=constants.DB_MEMORY_HELP)
    parser.add_argument('-r', '--ram', default=3, help=constants.DB_RAM_HELP,
                        type=int)
    parser.add_argument('db', help=constants.DB_DATABASE_HELP,
                        metavar='DATABASE')
    parser.add_argument('corpus', help=constants.DB_CORPUS_HELP,
                        metavar='CORPUS')

def configure_logging (verbose):
    logger = logging.getLogger('tacl')
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


def _copy_options (args):
    """Returns a string form of the options in `args`."""
    options = []
    if args.memory:
        options.append('--memory')
    if args.ram:
        options.append('--ram {}'.format(args.ram))
    if args.verbose:
        options.append('-{}'.format('v' * args.verbose))
    return ' ' + ' '.join(options)

def generate_parser ():
    parser = argparse.ArgumentParser(
        description=constants.TACL_HELPER_DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(title='subcommands')
    generate_text_against_corpus_subparser(subparsers)
    generate_text_in_corpus_subparser(subparsers)
    return parser

def generate_text_against_corpus_subparser (subparsers):
    parser = subparsers.add_parser(
        'text-against-corpus',
        description=constants.TACL_HELPER_AGAINST_DESCRIPTION,
        help=constants.TACL_HELPER_AGAINST_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=text_against_corpus)
    add_common_arguments(parser)
    add_db_arguments(parser)
    parser.add_argument('a_texts', help=constants.TACL_HELPER_AGAINST_A_HELP,
                        metavar='FILES_LIST', type=argparse.FileType('r'))
    parser.add_argument('b_texts', help=constants.TACL_HELPER_AGAINST_B_HELP,
                        metavar='CORPUS_FILES_LIST',
                        type=argparse.FileType('r'))
    parser.add_argument('output_dir', help=constants.TACL_HELPER_OUTPUT,
                        metavar='OUTPUT_DIR')

def generate_text_in_corpus_subparser (subparsers):
    parser = subparsers.add_parser(
        'text-in-corpus', description=constants.TACL_HELPER_IN_DESCRIPTION,
        help=constants.TACL_HELPER_IN_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=text_in_corpus)
    add_common_arguments(parser)
    add_db_arguments(parser)
    parser.add_argument('texts', help=constants.TACL_HELPER_IN_TEXTS_HELP,
                        metavar='FILE_LIST', type=argparse.FileType('r'))
    parser.add_argument('output_dir', help=constants.TACL_HELPER_OUTPUT,
                        metavar='OUTPUT_DIR')

def text_against_corpus (args):
    a_texts = args.a_texts.read().strip().split()
    b_texts = args.b_texts.read().strip().split()
    output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    catalogue = tacl.Catalogue({text : 'REST' for text in b_texts})
    commands = []
    options = _copy_options(args)
    for text in a_texts:
        text_name = os.path.splitext(text)[0]
        catalogue_path = os.path.join(
            output_dir, '{}-catalogue.txt'.format(text_name))
        results_path = os.path.join(
            output_dir, '{}-results.csv'.format(text_name))
        reduced_path = os.path.join(
            output_dir, '{}-reduced.csv'.format(text_name))
        catalogue[text] = 'A'
        catalogue.save(catalogue_path)
        query_command = 'tacl intersect{} {} {} {} > {}\n'.format(
            options, args.db, args.corpus, catalogue_path, results_path)
        report_command = 'tacl report --reduce --remove REST {} > {}\n'.format(
            results_path, reduced_path)
        commands.extend((query_command, report_command))
        del catalogue[text]
    commands_path = os.path.join(output_dir, 'commands')
    with open(commands_path, 'w') as fh:
        fh.writelines(commands)

def text_in_corpus (args):
    texts = args.texts.read().strip().split()
    output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    catalogue = tacl.Catalogue({text : 'REST' for text in texts})
    commands = []
    options = _copy_options(args)
    for text in texts:
        text_name = os.path.splitext(text)[0]
        catalogue_path = os.path.join(output_dir,
                                      '{}-catalogue.txt'.format(text_name))
        results_path = os.path.join(output_dir,
                                    '{}-results.csv'.format(text_name))
        reduced_path = os.path.join(output_dir,
                                    '{}-reduced.csv'.format(text_name))
        catalogue[text] = 'A'
        catalogue.save(catalogue_path)
        query_command = 'tacl intersect{} {} {} {} > {}\n'.format(
            options, args.db, args.corpus, catalogue_path, results_path)
        report_command = 'tacl report --reduce --remove REST {} > {}\n'.format(
            results_path, reduced_path)
        commands.extend((query_command, report_command))
        catalogue[text] = 'REST'
    commands_path = os.path.join(output_dir, 'commands')
    with open(commands_path, 'w') as fh:
        fh.writelines(commands)
