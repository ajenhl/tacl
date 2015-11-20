#!/usr/bin/env python3

import io
import os
import shlex
import sqlite3
import subprocess
import unittest

from ..tacl_test_case import TaclTestCase

from tacl import constants


class TaclScriptIntegrationTestCase (TaclTestCase):

    """Tests of the tacl command-line script.

    These tests duplicate much of
    integration_tests/data_store_test.py, due to not being able to
    mock out the tacl library classes in a subprocess.

    """

    def setUp (self):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self._corpus_dir = os.path.join(self._data_dir, 'stripped')
        self._db_path = os.path.join(self._data_dir, 'test.db')
        self._catalogue_path = os.path.join(self._data_dir, 'catalogue.txt')
        self._ngrams_path = os.path.join(self._data_dir, 'search_ngrams.txt')
        self._supplied_path = os.path.join(self._data_dir, 'supplied_input')
        # Since ngrams need to be added to a database for many of
        # these tests, define the command here.
        minimum = 1
        maximum = 3
        ngrams_command = 'tacl ngrams {} {} {} {}'.format(
            self._db_path, self._corpus_dir, minimum, maximum)
        self._ngrams_command_args = shlex.split(ngrams_command)
        if os.path.exists(self._db_path):
            raise Exception('{} exists; aborting tests that would create ' \
                                'this file'.format(self._db_path))

    def tearDown (self):
        if os.path.exists(self._db_path):
            os.remove(self._db_path)

    def test_add_ngrams_cbeta (self):
        subprocess.call(self._ngrams_command_args)
        conn = sqlite3.connect(self._db_path)
        actual_rows = conn.execute(
            'SELECT Text.name, Text.siglum, Text.checksum, Text.label, '
            'TextNGram.ngram, TextNGram.size, TextNGram.count '
            'FROM Text, TextNGram WHERE Text.id = TextNGram.text').fetchall()
        expected_rows = [
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 't', 1, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'h', 1, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'e', 1, 3),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'n', 1, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'w', 1, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'th', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'he', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'en', 2, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'nw', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'we', 2, 2),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'ew', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'nt', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'the', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'hen', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'enw', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'nwe', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'wew', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'ewe', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'wen', 3, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '', 'ent', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 't', 1, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'h', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'e', 1, 3),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'w', 1, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'n', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'th', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'he', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'ew', 2, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'we', 2, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'en', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'nt', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'the', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'hew', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'ewe', 3, 2),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'wew', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'wen', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'ent', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 't', 1, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'h', 1, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'e', 1, 4),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 's', 1, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'n', 1, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'th', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'he', 2, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'es', 2, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'se', 2, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'eh', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'en', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'nt', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'the', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'hes', 3, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ese', 3, 2),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'seh', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ehe', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'sen', 3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '', 'ent', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 't', 1, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'h', 1, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'e', 1, 3),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'w', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 's', 1, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'n', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'th', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'he', 2, 2),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ew', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ws', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'sh', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'es', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'se', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'en', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'nt', 2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'the', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'hew', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ews', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'wsh', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'she', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'hes', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ese', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'sen', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'ent', 3, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 't', 1, 2),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'h', 1, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'a', 1, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'th', 2, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'ha', 2, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'at', 2, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'tha', 3, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '', 'hat', 3, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'h', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'e', 1, 2),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'n', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 's', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'he', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'en', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'ns', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'se', 2, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'hen', 3, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'ens', 3, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '', 'nse', 3, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'w', 1, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'e', 1, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'l', 1, 2),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'we', 2, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'el', 2, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'll', 2, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'wel', 3, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '', 'ell', 3, 1)]
        self.assertEqual(set(actual_rows), set(expected_rows))
        actual_rows = conn.execute(
            'SELECT Text.name, Text.siglum, TextHasNGram.size '
            'FROM Text, TextHasNGram '
            'WHERE Text.id = TextHasNGram.text').fetchall()
        expected_rows = [
            ('T1', 'base', 1), ('T1', 'base', 2), ('T1', 'base', 3),
            ('T1', 'a', 1), ('T1', 'a', 2), ('T1', 'a', 3),
            ('T2', 'base', 1), ('T2', 'base', 2), ('T2', 'base', 3),
            ('T2', 'a', 1), ('T2', 'a', 2), ('T2', 'a', 3),
            ('T3', 'base', 1), ('T3', 'base', 2), ('T3', 'base', 3),
            ('T4', 'base', 1), ('T4', 'base', 2), ('T4', 'base', 3),
            ('T5', 'base', 1), ('T5', 'base', 2), ('T5', 'base', 3),
            ]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_add_ngrams_pagel (self):
        ngrams_command = 'tacl ngrams -t {} {} {} {} {}'.format(
            constants.TOKENIZER_CHOICE_PAGEL, self._db_path,
            self._corpus_dir, 1, 3)
        subprocess.call(shlex.split(ngrams_command))
        conn = sqlite3.connect(self._db_path)
        actual_rows = conn.execute(
            'SELECT Text.name, Text.siglum, Text.checksum, Text.label, '
            'TextNGram.ngram, TextNGram.size, TextNGram.count '
            'FROM Text, TextNGram WHERE Text.id = TextNGram.text').fetchall()
        expected_rows = [
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '',
             'then', 1, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '',
             'we', 1, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '',
             'went', 1, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '',
             'then we', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '',
             'we went', 2, 1),
            ('T1', 'base', '705c89d665a5300516fe7314f84ebce0', '',
             'then we went', 3, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'the', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'we', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'went', 1, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'the we', 2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'we went',
             2, 1),
            ('T1', 'a', 'e898b184b8d4d3ab5fea9d79fd645135', '', 'the we went',
             3, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '',
             'these', 1, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '',
             'he', 1, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '',
             'sent', 1, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '',
             'these he', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '',
             'he sent', 2, 1),
            ('T2', 'base', 'ccefdfb4379dd0829a8fa79a9e07f2e0', '',
             'these he sent', 3, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'thews', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'he', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'sent', 1, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'thews he',
             2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'he sent',
             2, 1),
            ('T2', 'a', '08e0878f03b63bdbc25d4cce082329e4', '', 'thews he sent',
             3, 1),
            ('T3', 'base', 'bb34469a937a77ae77c2aeb67248c43c', '',
             'that', 1, 1),
            ('T4', 'base', '3a0dede3266ed7d2e44cfd7ac38632d5', '',
             'hense', 1, 1),
            ('T5', 'base', '1b42a11f5f647e53d20da8c8f57a9f02', '',
             'well', 1, 1),
        ]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_counts (self):
        subprocess.call(self._ngrams_command_args)
        counts_command = 'tacl counts {} {} {}'.format(
            self._db_path, self._corpus_dir, self._catalogue_path)
        data = subprocess.check_output(shlex.split(counts_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_rows = [
            ('T1', 'base', '1', '5', '10', '10', 'A'),
            ('T1', 'base', '2', '7', '9', '10', 'A'),
            ('T1', 'base', '3', '8', '8', '10', 'A'),
            ('T1', 'a', '1', '5', '9', '9', 'A'),
            ('T1', 'a', '2', '6', '8', '9', 'A'),
            ('T1', 'a', '3', '6', '7', '9', 'A'),
            ('T2', 'base', '1', '5', '11', '11', 'B'),
            ('T2', 'base', '2', '7', '10', '11', 'B'),
            ('T2', 'base', '3', '7', '9', '11', 'B'),
            ('T2', 'a', '1', '6', '11', '11', 'B'),
            ('T2', 'a', '2', '9', '10', '11', 'B'),
            ('T2', 'a', '3', '9', '9', '11', 'B'),
            ('T3', 'base', '1', '3', '4', '4', 'C'),
            ('T3', 'base', '2', '3', '3', '4', 'C'),
            ('T3', 'base', '3', '2', '2', '4', 'C'),
            ('T5', 'base', '1', '3', '4', '4', 'A'),
            ('T5', 'base', '2', '3', '3', '4', 'A'),
            ('T5', 'base', '3', '2', '2', '4', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff (self):
        subprocess.call(self._ngrams_command_args)
        diff_command = 'tacl diff {} {} {}'.format(
            self._db_path, self._corpus_dir, self._catalogue_path)
        data = subprocess.check_output(shlex.split(diff_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_rows = [
            ('s', '1', 'T2', 'base', '2', 'B'),
            ('s', '1', 'T2', 'a', '2', 'B'),
            ('a', '1', 'T3', 'base', '1', 'C'),
            ('l', '1', 'T5', 'base', '2', 'A'),
            ('nw', '2', 'T1', 'base', '1', 'A'),
            ('we', '2', 'T1', 'base', '2', 'A'),
            ('we', '2', 'T1', 'a', '2', 'A'),
            ('we', '2', 'T5', 'base', '1', 'A'),
            ('es', '2', 'T2', 'base', '2', 'B'),
            ('es', '2', 'T2', 'a', '1', 'B'),
            ('se', '2', 'T2', 'base', '2', 'B'),
            ('se', '2', 'T2', 'a', '1', 'B'),
            ('ws', '2', 'T2', 'a', '1', 'B'),
            ('sh', '2', 'T2', 'a', '1', 'B'),
            ('eh', '2', 'T2', 'base', '1', 'B'),
            ('ha', '2', 'T3', 'base', '1', 'C'),
            ('at', '2', 'T3', 'base', '1', 'C'),
            ('el', '2', 'T5', 'base', '1', 'A'),
            ('ll', '2', 'T5', 'base', '1', 'A'),
            ('hen', '3', 'T1', 'base', '1', 'A'),
            ('enw', '3', 'T1', 'base', '1', 'A'),
            ('nwe', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'a', '1', 'A'),
            ('ewe', '3', 'T1', 'base', '1', 'A'),
            ('ewe', '3', 'T1', 'a', '2', 'A'),
            ('wen', '3', 'T1', 'base', '1', 'A'),
            ('wen', '3', 'T1', 'a', '1', 'A'),
            ('hes', '3', 'T2', 'base', '2', 'B'),
            ('hes', '3', 'T2', 'a', '1', 'B'),
            ('ese', '3', 'T2', 'base', '2', 'B'),
            ('ese', '3', 'T2', 'a', '1', 'B'),
            ('ews', '3', 'T2', 'a', '1', 'B'),
            ('seh', '3', 'T2', 'base', '1', 'B'),
            ('wsh', '3', 'T2', 'a', '1', 'B'),
            ('ehe', '3', 'T2', 'base', '1', 'B'),
            ('she', '3', 'T2', 'a', '1', 'B'),
            ('sen', '3', 'T2', 'base', '1', 'B'),
            ('sen', '3', 'T2', 'a', '1', 'B'),
            ('tha', '3', 'T3', 'base', '1', 'C'),
            ('hat', '3', 'T3', 'base', '1', 'C'),
            ('wel', '3', 'T5', 'base', '1', 'A'),
            ('ell', '3', 'T5', 'base', '1', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_asymmetric (self):
        subprocess.call(self._ngrams_command_args)
        diff_command = 'tacl diff -a {} {} {} {}'.format(
            'A', self._db_path, self._corpus_dir, self._catalogue_path)
        data = subprocess.check_output(shlex.split(diff_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_rows = [
            ('l', '1', 'T5', 'base', '2', 'A'),
            ('nw', '2', 'T1', 'base', '1', 'A'),
            ('we', '2', 'T1', 'base', '2', 'A'),
            ('we', '2', 'T1', 'a', '2', 'A'),
            ('we', '2', 'T5', 'base', '1', 'A'),
            ('el', '2', 'T5', 'base', '1', 'A'),
            ('ll', '2', 'T5', 'base', '1', 'A'),
            ('hen', '3', 'T1', 'base', '1', 'A'),
            ('enw', '3', 'T1', 'base', '1', 'A'),
            ('nwe', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'base', '1', 'A'),
            ('wew', '3', 'T1', 'a', '1', 'A'),
            ('ewe', '3', 'T1', 'base', '1', 'A'),
            ('ewe', '3', 'T1', 'a', '2', 'A'),
            ('wen', '3', 'T1', 'base', '1', 'A'),
            ('wen', '3', 'T1', 'a', '1', 'A'),
            ('wel', '3', 'T5', 'base', '1', 'A'),
            ('ell', '3', 'T5', 'base', '1', 'A')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_diff_supplied (self):
        supplied_dir = os.path.join(self._data_dir, 'supplied_input')
        results1 = os.path.join(supplied_dir, 'diff_input_1.csv')
        results2 = os.path.join(supplied_dir, 'diff_input_2.csv')
        results3 = os.path.join(supplied_dir, 'diff_input_3.csv')
        diff_command = 'tacl sdiff -d {} -l A B C -s {} {} {}'.format(
            self._db_path, results1, results2, results3)
        data = subprocess.check_output(shlex.split(diff_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_rows = [
            ('過失', '2', 'T0005', 'base', '5', 'A'),
            ('過失', '2', 'T0003', '大', '2', 'A'),
            ('皆不', '2', 'T0004', 'base', '1', 'A'),
            ('皆不', '2', 'T0002', '大', '1', 'A'),
            ('皆不', '2', 'T0003', '大', '1', 'A'),
            ('棄捨', '2', 'T0004', '元', '4', 'A'),
            ('棄捨', '2', 'T0003', 'base', '2', 'A'),
            ('七佛', '2', 'T0006', 'base', '3', 'B'),
            ('七佛', '2', 'T0004', '元', '3', 'B'),
            ('七佛', '2', 'T0002', '大', '2', 'B'),
            ('人子', '2', 'T0004', '元', '1', 'C'),
            ('人子', '2', 'T0007', 'base', '1', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection (self):
        subprocess.call(self._ngrams_command_args)
        intersect_command = 'tacl intersect {} {} {}'.format(
            self._db_path, self._corpus_dir, self._catalogue_path)
        data = subprocess.check_output(shlex.split(intersect_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_rows = [
            ('t', '1', 'T1', 'base', '2', 'A'),
            ('t', '1', 'T1', 'a', '2', 'A'),
            ('t', '1', 'T2', 'base', '2', 'B'),
            ('t', '1', 'T2', 'a', '2', 'B'),
            ('t', '1', 'T3', 'base', '2', 'C'),
            ('h', '1', 'T1', 'base', '1', 'A'),
            ('h', '1', 'T1', 'a', '1', 'A'),
            ('h', '1', 'T2', 'base', '2', 'B'),
            ('h', '1', 'T2', 'a', '2', 'B'),
            ('h', '1', 'T3', 'base', '1', 'C'),
            ('th', '2', 'T1', 'base', '1', 'A'),
            ('th', '2', 'T1', 'a', '1', 'A'),
            ('th', '2', 'T2', 'base', '1', 'B'),
            ('th', '2', 'T2', 'a', '1', 'B'),
            ('th', '2', 'T3', 'base', '1', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_intersection_supplied (self):
        supplied_dir = os.path.join(self._data_dir, 'supplied_input')
        results1 = os.path.join(supplied_dir, 'intersect_input_1.csv')
        results2 = os.path.join(supplied_dir, 'intersect_input_2.csv')
        results3 = os.path.join(supplied_dir, 'intersect_input_3.csv')
        intersect_command = 'tacl sintersect -d {} -l A B C -s {} {} {}'.format(
            self._db_path, results1, results2, results3)
        data = subprocess.check_output(shlex.split(intersect_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        expected_rows = [
            ('龍皆起前', '4', 'T0033', '元', '1', 'A'),
            ('龍皆起前', '4', 'T0034', '明', '2', 'A'),
            ('龍皆起前', '4', 'T0002', 'base', '3', 'B'),
            ('龍皆起前', '4', 'T0052', 'base', '2', 'C'),
            ('[月*劦]生', '2', 'T0002', '明', '10', 'A'),
            ('[月*劦]生', '2', 'T0002', 'base', '10', 'A'),
            ('[月*劦]生', '2', 'T0023', '大', '2', 'B'),
            ('[月*劦]生', '2', 'T0053', '大', '2', 'C')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_search (self):
        subprocess.call(self._ngrams_command_args)
        search_command = 'tacl search {} {} {}'.format(
            self._db_path, self._corpus_dir, self._ngrams_path)
        data = subprocess.check_output(shlex.split(search_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        # The SQLite3 documentation says that the order of
        # concatenated tokens (as seen in the fourth element in each
        # row) is arbitrary, which means this test may sometimes fail
        # in its current form.
        expected_rows = [
            ('T1', 'base', '1', '', 'he', '1'),
            ('T1', 'a', '1', '', 'he', '1'),
            ('T2', 'base', '4', '', 'ese, he', '2'),
            ('T2', 'a', '3', '', 'ese, he', '2'),
            ('T4', 'base', '1', '', 'he', '1')]
        self.assertEqual(set(actual_rows), set(expected_rows))

    def test_search_with_catalogue (self):
        subprocess.call(self._ngrams_command_args)
        catalogue_path = os.path.join(self._data_dir, 'search_catalogue.txt')
        search_command = 'tacl search -c {} {} {} {}'.format(
            catalogue_path, self._db_path, self._corpus_dir, self._ngrams_path)
        data = subprocess.check_output(shlex.split(search_command))
        actual_rows = self._get_rows_from_csv(io.StringIO(data.decode('utf-8')))
        # The SQLite3 documentation says that the order of
        # concatenated tokens (as seen in the fourth element in each
        # row) is arbitrary, which means this test may sometimes fail
        # in its current form.
        expected_rows = [
            ('T1', 'base', '1', 'A', 'he', '1'),
            ('T1', 'a', '1', 'A', 'he', '1'),
            ('T2', 'base', '4', '', 'ese, he', '2'),
            ('T2', 'a', '3', '', 'ese, he', '2'),
            ('T4', 'base', '1', 'B', 'he', '1')]
        self.assertEqual(set(actual_rows), set(expected_rows))


if __name__ == '__main__':
    unittest.main()
