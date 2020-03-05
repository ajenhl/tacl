#!/usr/bin/env python3

import os
import tempfile

import tacl
from ..tacl_test_case import TaclTestCase


class TEICorpusIntegrationTestCase (TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'data')
        self._cbeta_xml_dir = os.path.join(self._data_dir, 'cbeta_xml',
                                           self._corpus_name)
        self._expected_output_dir = os.path.join(
            self._data_dir, 'expected_corpus_output', self._corpus_name)
        self.maxDiff = None

    def _test_tidy(self, corpus_name):
        corpus_dir = os.path.join(self._cbeta_xml_dir, corpus_name)
        expected_dir = os.path.join(self._expected_output_dir, corpus_name)
        with tempfile.TemporaryDirectory() as actual_dir:
            corpus = tacl.TEICorpusCBETAGitHub(corpus_dir, actual_dir)
            corpus.tidy()
            self._compare_dirs(actual_dir, expected_dir)


class TEICorpusCBETAGitHubIntegrationTestCase (TEICorpusIntegrationTestCase):

    def setUp(self):
        self._corpus_name = 'github'
        super().setUp()

    def test_tidy_basic(self):
        self._test_tidy('basic')

    def test_tidy_extract_commentary(self):
        self._test_tidy('extract-commentary')

    def test_tidy_extract_verse(self):
        self._test_tidy('extract-verse')

    def test_extract_xu_w(self):
        """Tests that cb:div[@type='xu'] and cb:div[@type='w'] are extracted
        correctly."""
        self._test_tidy('extract-xu-w')

    def test_tidy_no_join_texts(self):
        """Tests that works ending in A/B etc are not joined."""
        self._test_tidy('no-join-texts-corpus')

    def test_tidy_T0001(self):
        self._test_tidy('T0001-corpus')

    def test_tidy_T0154(self):
        self._test_tidy('T0154-corpus')

    def test_tidy_T0220(self):
        self._test_tidy('T0220-corpus')

    def test_tidy_T0310(self):
        self._test_tidy('T0310-corpus')

    def test_tidy_T2102(self):
        self._test_tidy('T2102-corpus')
