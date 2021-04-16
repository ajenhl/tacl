"""Functions useful when writing command-line scripts that interact
with tacl."""

import logging

import colorlog

import tacl
from tacl import constants


def add_common_arguments(parser):
    """Adds common arguments for all parsers."""
    parser.add_argument('-v', '--verbose', action='count',
                        help=constants.VERBOSE_HELP)


def add_corpus_arguments(parser):
    """Adds common arguments for commands making use of a corpus to
    `parser`."""
    add_tokenizer_argument(parser)
    parser.add_argument('corpus', help=constants.DB_CORPUS_HELP,
                        metavar='CORPUS')


def add_db_arguments(parser, db_option=False):
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


def add_query_arguments(parser):
    """Adds common arguments for query sub-commonads to `parser`."""
    parser.add_argument('catalogue', help=constants.CATALOGUE_CATALOGUE_HELP,
                        metavar='CATALOGUE')


def add_supplied_query_arguments(parser):
    """Adds common arguments for supplied query sub-commands to
    `parser`."""
    parser.add_argument('-l', '--labels', help=constants.SUPPLIED_LABELS_HELP,
                        nargs='+', required=True)
    parser.add_argument('-s', '--supplied',
                        help=constants.SUPPLIED_RESULTS_HELP,
                        metavar='RESULTS', nargs='+', required=True)


def add_tokenizer_argument(parser):
    parser.add_argument('-t', '--tokenizer',
                        choices=constants.TOKENIZER_CHOICES,
                        default=constants.TOKENIZER_CHOICE_CBETA,
                        help=constants.DB_TOKENIZER_HELP)


def configure_logging(verbose, logger):
    """Configures the logging used."""
    if not verbose:
        log_level = logging.WARNING
    elif verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger.setLevel(log_level)
    ch = colorlog.StreamHandler()
    ch.setLevel(log_level)
    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s %(name)s %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def get_catalogue(args):
    """Returns a `tacl.Catalogue`."""
    catalogue = tacl.Catalogue()
    catalogue.load(args.catalogue)
    return catalogue


def get_corpus(args):
    """Returns a `tacl.Corpus`."""
    tokenizer = get_tokenizer(args)
    return tacl.Corpus(args.corpus, tokenizer)


def get_data_store(args, must_exist=True):
    """Returns a `tacl.DataStore`."""
    return tacl.DataStore(args.db, args.memory, args.ram,
                          must_exist=must_exist)


def get_ngrams(path):
    """Returns a list of n-grams read from the file at `path`."""
    with open(path, encoding='utf-8') as fh:
        ngrams = [ngram.strip() for ngram in fh.readlines()]
    return ngrams


def get_tokenizer(args):
    return tacl.Tokenizer(*constants.TOKENIZERS[args.tokenizer])
