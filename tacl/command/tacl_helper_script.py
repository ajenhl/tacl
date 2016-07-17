import argparse
import logging
import os
import sys

import pandas as pd

import tacl
import tacl.command.utils as utils
from tacl import constants


logger = logging.getLogger('tacl')


def main ():
    parser = generate_parser()
    args = parser.parse_args()
    if hasattr(args, 'verbose'):
        utils.configure_logging(args.verbose, logger)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def collapse_witnesses (args):
    # This split is to make it easier to test the functionality.
    _collapse_witnesses(args.results, sys.stdout)

def _collapse_witnesses (input_fh, output_fh):
    logger.debug('Loading results')
    results = pd.read_csv(input_fh, encoding='utf-8', na_filter=False)
    logger.debug('Loaded results')
    grouped = results.groupby(
        [constants.NAME_FIELDNAME, constants.NGRAM_FIELDNAME,
         constants.COUNT_FIELDNAME], sort=False)
    logger.debug('Grouped results')
    output_rows = []
    for indices in iter(grouped.groups.values()):
        logger.debug('Handling group')
        sigla = []
        for index in indices:
            row_data = dict(results.iloc[index])
            siglum = row_data['siglum']
            if ' ' in siglum:
                siglum = '"{}"'.format(siglum)
            sigla.append(siglum)
        sigla.sort()
        # This does not even try to escape sigla that contain spaces.
        row_data['sigla'] = ' '.join(sigla)
        del row_data['siglum']
        output_rows.append(row_data)
    results = None
    logger.debug('Building new results')
    columns = [constants.NGRAM_FIELDNAME, constants.SIZE_FIELDNAME,
               constants.NAME_FIELDNAME, 'sigla', constants.COUNT_FIELDNAME,
               constants.LABEL_FIELDNAME]
    out_df = pd.DataFrame(output_rows, columns=columns)
    out_df.to_csv(output_fh, encoding='utf-8', index=False)
    return output_fh

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
    generate_collapse_witness_results_subparser(subparsers)
    generate_label_count_subparser(subparsers)
    generate_text_against_corpus_subparser(subparsers)
    generate_text_in_corpus_subparser(subparsers)
    generate_validate_catalogue_subparser(subparsers)
    return parser

def generate_collapse_witness_results_subparser (subparsers):
    parser = subparsers.add_parser(
        'collapse-witnesses',
        description=constants.TACL_HELPER_COLLAPSE_DESCRIPTION,
        help=constants.TACL_HELPER_COLLAPSE_HELP)
    parser.set_defaults(func=collapse_witnesses)
    utils.add_common_arguments(parser)
    parser.add_argument('results', help=constants.TACL_HELPER_RESULTS_HELP,
                        metavar='RESULTS')

def generate_label_count_subparser (subparsers):
    parser = subparsers.add_parser(
        'label-count',
        description=constants.TACL_HELPER_LABEL_COUNT_DESCRIPTION,
        help=constants.TACL_HELPER_LABEL_COUNT_HELP)
    parser.set_defaults(func=label_count)
    utils.add_common_arguments(parser)
    parser.add_argument('results', help=constants.TACL_HELPER_RESULTS_HELP,
                        metavar='RESULTS')

def generate_text_against_corpus_subparser (subparsers):
    parser = subparsers.add_parser(
        'text-against-corpus',
        description=constants.TACL_HELPER_AGAINST_DESCRIPTION,
        help=constants.TACL_HELPER_AGAINST_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=text_against_corpus)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
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
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    parser.add_argument('texts', help=constants.TACL_HELPER_IN_TEXTS_HELP,
                        metavar='FILE_LIST', type=argparse.FileType('r'))
    parser.add_argument('output_dir', help=constants.TACL_HELPER_OUTPUT,
                        metavar='OUTPUT_DIR')

def generate_validate_catalogue_subparser (subparsers):
    parser = subparsers.add_parser(
        'validate-catalogue',
        description=constants.TACL_HELPER_VALIDATE_CATALOGUE_DESCRIPTION,
        help=constants.TACL_HELPER_VALIDATE_CATALOGUE_HELP,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.set_defaults(func=validate_catalogue)
    utils.add_common_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)

def label_count (args):
    results = pd.read_csv(args.results, encoding='utf-8', na_filter=False)
    results.loc[:, 'label count'] = 0
    def add_label_count (df):
        # For each n-gram and label pair, we need the maximum count
        # among all witnesses to each text, and then the sum of those
        # across all texts.
        text_maxima = df.groupby(constants.NAME_FIELDNAME).max()
        df.loc[:, 'label count'] = text_maxima[constants.COUNT_FIELDNAME].sum()
        return df
    out_df = results.groupby(
        [constants.LABEL_FIELDNAME, constants.NGRAM_FIELDNAME]).apply(
            add_label_count)
    out_df.to_csv(sys.stdout, encoding='utf-8', index=False)

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

def validate_catalogue (args):
    try:
        catalogue = utils.get_catalogue(args.catalogue)
    except tacl.exceptions.MalformedCatalogueError as e:
        print('Error: {}'.format(e))
        print('Other errors may be present; re-run this validation after correcting the above problem.')
        sys.exit(1)
    corpus = utils.get_corpus(args)
    has_error = False
    for name in catalogue:
        count = 0
        for text in corpus.get_texts(name):
            count += 1
            break
        if not count:
            has_error = True
            print('Error: Catalogue references text {} that does not '
                  'exist in the corpus'.format(name))
    if has_error:
        sys.exit(1)
