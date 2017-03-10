"""Command-line script to list texts from one sub-corpus (labelled set
of texts defined in a catalogue file) in order of similarity to each
text in that corpus. Takes into account a second sub-corpus of texts
that are similar to those in the first, but not in the way(s) that are
the subject of the investigation."""

import argparse
import logging
import os

import tacl
import tacl.command.utils as utils
from tacl import constants


logger = logging.getLogger('tacl')


def main():
    parser = generate_parser()
    args = parser.parse_args()
    if hasattr(args, 'verbose'):
        utils.configure_logging(args.verbose, logger)
    store = utils.get_data_store(args)
    corpus = utils.get_corpus(args)
    catalogue = utils.get_catalogue(args)
    tokenizer = utils.get_tokenizer(args)
    check_catalogue(catalogue, args.label)
    store.validate(corpus, catalogue)
    output_dir = os.path.abspath(args.output)
    if os.path.exists(output_dir):
        logger.warning('Output directory already exists; any results therein '
                       'will be reused rather than regenerated.')
    os.makedirs(output_dir, exist_ok=True)
    report = tacl.JitCReport(store, corpus, tokenizer)
    report.generate(output_dir, catalogue, args.label)


def check_catalogue(catalogue, label):
    """Raise an exception if `catalogue` contains more than two labels, or
    if `label` is not used in the `catalogue`."""
    labels = set(catalogue.values())
    if label not in labels:
        raise Exception(
            'The specified label "{}" must be present in the catalogue.')
    elif len(labels) != 2:
        raise Exception('The catalogue must specify only two labels.')


def generate_parser():
    parser = argparse.ArgumentParser(description=constants.JITC_DESCRIPTION)
    utils.add_common_arguments(parser)
    utils.add_db_arguments(parser)
    utils.add_corpus_arguments(parser)
    utils.add_query_arguments(parser)
    parser.add_argument('label', help=constants.JITC_LABEL_HELP,
                        metavar='LABEL')
    parser.add_argument('output', help=constants.REPORT_OUTPUT_HELP,
                        metavar='OUTPUT')
    return parser
