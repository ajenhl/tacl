#!/usr/bin/env python3

import collections
import io
import sqlite3
import unittest
from unittest.mock import call, MagicMock, sentinel

import pandas as pd

import tacl
from tacl.exceptions import MalformedQueryError
from .tacl_test_case import TaclTestCase


class DataStoreTestCase (TaclTestCase):

    """Unit tests of the DataStore class."""

    def test_add_indices(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        store._add_indices()
        store._conn.execute.assert_called_once_with(
            tacl.constants.CREATE_INDEX_TEXTNGRAM_SQL)

    def test_add_ngrams(self):
        add_indices = self._create_patch('tacl.DataStore._add_indices')
        add_text_ngrams = self._create_patch('tacl.DataStore._add_text_ngrams')
        analyse = self._create_patch('tacl.DataStore._analyse')
        initialise = self._create_patch('tacl.DataStore._initialise_database')
        text1 = MagicMock(spec_set=tacl.WitnessText)
        text2 = MagicMock(spec_set=tacl.WitnessText)
        corpus = MagicMock(spec_set=tacl.Corpus)
        corpus.get_witnesses = MagicMock(name='get_witnesses')
        corpus.get_witnesses.return_value = iter([text1, text2])
        store = tacl.DataStore(':memory:')
        store.add_ngrams(corpus, 2, 3)
        initialise.assert_called_once_with(store)
        corpus.get_witnesses.assert_called_once_with()
        self.assertEqual(add_text_ngrams.mock_calls,
                         [call(store, text1, 2, 3), call(store, text2, 2, 3)])
        add_indices.assert_called_once_with(store)
        analyse.assert_called_once_with(store)

    def test_add_ngrams_with_catalogue(self):
        add_indices = self._create_patch('tacl.DataStore._add_indices')
        add_text_ngrams = self._create_patch('tacl.DataStore._add_text_ngrams')
        analyse = self._create_patch('tacl.DataStore._analyse')
        initialise = self._create_patch('tacl.DataStore._initialise_database')
        text1 = MagicMock(spec_set=tacl.WitnessText)
        text1.get_names = MagicMock(name='get_names')
        text1.get_names.return_value = ['T1', 'base']
        text2 = MagicMock(spec_set=tacl.WitnessText)
        text2.get_names = MagicMock(name='get_names')
        text2.get_names.return_value = ['T2', 'base']
        corpus = MagicMock(spec_set=tacl.Corpus)
        corpus.get_witnesses = MagicMock(name='get_witnesses')
        corpus.get_witnesses.return_value = iter([text1, text2])
        store = tacl.DataStore(':memory:')
        catalogue = tacl.Catalogue()
        catalogue['T1'] = 'A'
        store.add_ngrams(corpus, 2, 3, catalogue)
        initialise.assert_called_once_with(store)
        corpus.get_witnesses.assert_called_once_with()
        text1.get_names.assert_called_once_with()
        text2.get_names.assert_called_once_with()
        add_text_ngrams.assert_called_once_with(store, text1, 2, 3)
        add_indices.assert_called_once_with(store)
        analyse.assert_called_once_with(store)

    def test_add_temporary_ngrams(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        store._add_temporary_ngrams([sentinel.ngram1, sentinel.ngram2])
        self.assertEqual(
            store._conn.mock_calls,
            [call.execute(tacl.constants.DROP_TEMPORARY_NGRAMS_TABLE_SQL),
             call.execute(tacl.constants.CREATE_TEMPORARY_NGRAMS_TABLE_SQL),
             call.executemany(tacl.constants.INSERT_TEMPORARY_NGRAM_SQL,
                              [(sentinel.ngram1,), (sentinel.ngram2,)])])

    def test_add_temporary_ngrams_twice(self):
        # Test that multiple calls to the method succeed.
        store = tacl.DataStore(':memory:')
        input_ngrams = ['禁律', '律藏也']
        store._add_temporary_ngrams(input_ngrams)
        cursor = store._conn.execute('SELECT * FROM InputNGram')
        expected_ngrams = set(input_ngrams)
        actual_ngrams = set([row['ngram'] for row in cursor.fetchall()])
        self.assertEqual(actual_ngrams, expected_ngrams)
        input_ngrams = ['每', '以示']
        store._add_temporary_ngrams(input_ngrams)
        cursor = store._conn.execute('SELECT * FROM InputNGram')
        expected_ngrams = set(input_ngrams)
        actual_ngrams = set([row['ngram'] for row in cursor.fetchall()])
        self.assertEqual(actual_ngrams, expected_ngrams)

    def test_add_text_ngrams_existing(self):
        get_text_id = self._create_patch('tacl.DataStore._get_text_id')
        get_text_id.return_value = sentinel.text_id
        has_ngrams = self._create_patch('tacl.DataStore._has_ngrams')
        has_ngrams.return_value = True
        add_text_size_ngrams = self._create_patch(
            'tacl.DataStore._add_text_size_ngrams')
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_ngrams.return_value = [(2, sentinel.two_grams),
                                        (3, sentinel.three_grams)]
        store = tacl.DataStore(':memory:')
        store._add_text_ngrams(text, 2, 3)
        get_text_id.assert_called_once_with(store, text)
        has_ngrams.assert_has_calls([
            call(store, sentinel.text_id, 2),
            call(store, sentinel.text_id, 3)])
        text.get_ngrams.assert_called_once_with(2, 3, [2, 3])
        add_text_size_ngrams.assert_has_calls([])

    def test_add_text_ngrams_not_existing(self):
        get_text_id = self._create_patch('tacl.DataStore._get_text_id')
        get_text_id.return_value = sentinel.text_id
        has_ngrams = self._create_patch('tacl.DataStore._has_ngrams')
        has_ngrams.return_value = False
        add_text_size_ngrams = self._create_patch(
            'tacl.DataStore._add_text_size_ngrams')
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_ngrams.return_value = [(2, sentinel.two_grams),
                                        (3, sentinel.three_grams)]
        store = tacl.DataStore(':memory:')
        store._add_text_ngrams(text, 2, 3)
        get_text_id.assert_called_once_with(store, text)
        has_ngrams.assert_has_calls([
            call(store, sentinel.text_id, 2),
            call(store, sentinel.text_id, 3)])
        text.get_ngrams.assert_called_once_with(2, 3, [])
        add_text_size_ngrams.assert_has_calls([
            call(store, sentinel.text_id, 2, sentinel.two_grams),
            call(store, sentinel.text_id, 3, sentinel.three_grams)])

    def test_add_text_record(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock()
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_checksum.return_value = sentinel.checksum
        text.get_filename.return_value = sentinel.filename
        text.get_names.return_value = (sentinel.name, sentinel.siglum)
        tokens = [sentinel.token]
        text.get_tokens.return_value = tokens
        cursor = store._conn.execute.return_value
        cursor.lastrowid = sentinel.text_id
        actual_text_id = store._add_text_record(text)
        text.get_checksum.assert_called_once_with()
        text.get_filename.assert_called_once_with()
        text.get_tokens.assert_called_once_with()
        store._conn.execute.assert_called_once_with(
            tacl.constants.INSERT_TEXT_SQL,
            [sentinel.name, sentinel.siglum, sentinel.checksum, len(tokens), ''])
        store._conn.commit.assert_called_once_with()
        self.assertEqual(actual_text_id, sentinel.text_id)

    def test_add_text_size_ngrams(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        size = 1
        ngrams = collections.OrderedDict([('a', 2), ('b', 1)])
        store._add_text_size_ngrams(sentinel.text_id, size, ngrams)
        self.assertEqual(
            store._conn.mock_calls,
            [call.execute(tacl.constants.INSERT_TEXT_HAS_NGRAM_SQL,
                          [sentinel.text_id, size, len(ngrams)]),
             call.executemany(tacl.constants.INSERT_NGRAM_SQL,
                              [[sentinel.text_id, 'a', size, 2],
                               [sentinel.text_id, 'b', size, 1]]),
             call.commit()])

    def test_analyse(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        store._analyse()
        store._conn.execute.assert_called_once_with(
            tacl.constants.ANALYSE_SQL.format(''))
        store._conn.reset_mock()
        store._analyse(sentinel.table)
        store._conn.execute.assert_called_once_with(
            tacl.constants.ANALYSE_SQL.format(sentinel.table))

    def test_counts(self):
        labels = [sentinel.label]
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = labels
        get_placeholders = self._create_patch(
            'tacl.DataStore._get_placeholders', False)
        get_placeholders.return_value = sentinel.placeholders
        input_fh = MagicMock(name='fh')
        csv = self._create_patch('tacl.DataStore._csv', False)
        csv.return_value = input_fh
        catalogue = MagicMock(name='catalogue')
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        output_fh = store.counts(catalogue, input_fh)
        set_labels.assert_called_once_with(store, catalogue)
        get_placeholders.assert_called_once_with(labels)
        sql = tacl.constants.SELECT_COUNTS_SQL.format(sentinel.placeholders)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(sql, [sentinel.label])])
        csv.assert_called_once_with(cursor, tacl.constants.COUNTS_FIELDNAMES,
                                    input_fh)
        self.assertEqual(input_fh, output_fh)

    def test_csv(self):
        pass

    def test_delete_text_ngrams(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        store._delete_text_ngrams(sentinel.text_id)
        expected_calls = [
            call.execute(tacl.constants.DELETE_TEXT_NGRAMS_SQL,
                         [sentinel.text_id]),
            call.execute(tacl.constants.DELETE_TEXT_HAS_NGRAMS_SQL,
                         [sentinel.text_id]),
            call.commit()]
        self.assertEqual(store._conn.mock_calls, expected_calls)

    def test_diff(self):
        labels = {sentinel.label: 2, sentinel.label2: 1}
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = labels
        get_placeholders = self._create_patch(
            'tacl.DataStore._get_placeholders', False)
        get_placeholders.return_value = sentinel.placeholders
        log_query_plan = self._create_patch('tacl.DataStore._log_query_plan',
                                            False)
        input_fh = MagicMock(name='fh')
        catalogue = MagicMock(name='catalogue')
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        _diff = self._create_patch('tacl.DataStore._diff', False)
        _diff.return_value = input_fh
        output_fh = store.diff(catalogue, tokenizer, input_fh)
        set_labels.assert_called_once_with(store, catalogue)
        get_placeholders.assert_called_once_with(
            [sentinel.label, sentinel.label2])
        self.assertTrue(log_query_plan.called)
        sql = tacl.constants.SELECT_DIFF_SQL.format(sentinel.placeholders,
                                                    sentinel.placeholders)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(sql, [sentinel.label, sentinel.label2,
                                             sentinel.label, sentinel.label2])])
        self.assertTrue(_diff.called)
        self.assertEqual(input_fh, output_fh)

    def test_diff_asymmetric(self):
        labels = {sentinel.label: 1, sentinel.prime_label: 1}
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = labels
        get_placeholders = self._create_patch(
            'tacl.DataStore._get_placeholders', False)
        get_placeholders.return_value = sentinel.placeholders
        log_query_plan = self._create_patch('tacl.DataStore._log_query_plan',
                                            False)
        input_fh = MagicMock(name='fh')
        catalogue = MagicMock(name='catalogue')
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        tokenizer = MagicMock(name='tokenizer')
        _diff = self._create_patch('tacl.DataStore._diff', False)
        _diff.return_value = input_fh
        output_fh = store.diff_asymmetric(catalogue, sentinel.prime_label,
                                          tokenizer, input_fh)
        set_labels.assert_called_once_with(store, catalogue)
        get_placeholders.assert_called_once_with([sentinel.label])
        self.assertTrue(log_query_plan.called)
        sql = tacl.constants.SELECT_DIFF_ASYMMETRIC_SQL.format(
            sentinel.placeholders)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(sql, [sentinel.prime_label,
                                             sentinel.prime_label,
                                             sentinel.label])])
        self.assertTrue(_diff.called)
        self.assertEqual(input_fh, output_fh)

    def test_diff_asymmetric_invalid_label(self):
        # Tests that the right error is raised when the supplied label
        # is not present in the catalogue.
        catalogue = {'T1': 'A', 'T2': 'B'}
        prime_label = 'C'
        input_fh = MagicMock(name='fh')
        store = tacl.DataStore(':memory:')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = {'A': 1, 'B': 1}
        self.assertRaises(MalformedQueryError, store.diff_asymmetric,
                          catalogue, prime_label, tokenizer, input_fh)

    def test_diff_asymmetric_one_label(self):
        catalogue = {'T1': 'A', 'T2': 'A'}
        store = tacl.DataStore(':memory:')
        input_fh = MagicMock(name='fh')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = {'A': 2}
        self.assertRaises(MalformedQueryError, store.diff_asymmetric,
                          catalogue, 'A', tokenizer, input_fh)

    def test_diff_one_label(self):
        catalogue = {'T1': 'A', 'T2': 'A'}
        store = tacl.DataStore(':memory:')
        output_fh = MagicMock(name='fh')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = {'A': 2}
        self.assertRaises(MalformedQueryError, store.diff, catalogue,
                          tokenizer, output_fh)

    def test_diff_supplied_one_label(self):
        filenames = ['a.csv']
        labels = ['A']
        store = tacl.DataStore(':memory:')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        output_fh = MagicMock(name='fh')
        self.assertRaises(MalformedQueryError, store.diff_supplied, filenames,
                          labels, tokenizer, output_fh)

    def test_drop_indices(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        store._drop_indices()
        store._conn.execute.assert_called_once_with(
            tacl.constants.DROP_TEXTNGRAM_INDEX_SQL)

    def test_get_placeholders(self):
        store = tacl.DataStore(':memory:')
        data = [(['A'], '?'), (['A', 'B'], '?,?'), (['A', 'B', 'C'], '?,?,?')]
        for labels, expected_placeholders in data:
            actual_placeholders = store._get_placeholders(labels)
            self.assertEqual(actual_placeholders, expected_placeholders)

    def test_get_text_id(self):
        add_text = self._create_patch('tacl.DataStore._add_text_record')
        add_text.return_value = sentinel.new_text_id
        update_text = self._create_patch('tacl.DataStore._update_text_record')
        delete_ngrams = self._create_patch('tacl.DataStore._delete_text_ngrams')
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_checksum.return_value = sentinel.checksum
        text.get_filename.return_value = sentinel.filename
        text.get_names.return_value = (sentinel.name, sentinel.siglum)
        # There are three paths this method can take, depending on
        # whether a record already exists for the supplied text and,
        # if it does, whether the checksums match.
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        # Path one: there is no existing record.
        store._conn.execute.return_value = cursor
        cursor.fetchone.return_value = None
        actual_text_id = store._get_text_id(text)
        self.assertEqual(text.mock_calls, [call.get_names()])
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone()])
        add_text.assert_called_once_with(store, text)
        self.assertEqual(update_text.mock_calls, [])
        self.assertEqual(delete_ngrams.mock_calls, [])
        self.assertEqual(actual_text_id, sentinel.new_text_id)
        # Path two: there is an existing record, with a matching checksum.
        store._conn.reset_mock()
        text.reset_mock()
        add_text.reset_mock()
        update_text.reset_mock()
        cursor.fetchone.return_value = {'checksum': sentinel.checksum,
                                        'id': sentinel.old_text_id}
        actual_text_id = store._get_text_id(text)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone()])
        self.assertEqual(text.mock_calls,
                         [call.get_names(), call.get_checksum()])
        self.assertEqual(add_text.mock_calls, [])
        self.assertEqual(update_text.mock_calls, [])
        self.assertEqual(delete_ngrams.mock_calls, [])
        self.assertEqual(actual_text_id, sentinel.old_text_id)
        # Path three: there is an existing record, with a different
        # checksum.
        store._conn.reset_mock()
        text.reset_mock()
        add_text.reset_mock()
        update_text.reset_mock()
        cursor.fetchone.return_value = {'checksum': sentinel.new_checksum,
                                        'id': sentinel.old_text_id}
        actual_text_id = store._get_text_id(text)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone()])
        self.assertEqual(text.mock_calls,
                         [call.get_names(), call.get_checksum(),
                          call.get_filename()])
        update_text.assert_called_once_with(store, text, sentinel.old_text_id)
        delete_ngrams.assert_called_once_with(store, sentinel.old_text_id)
        self.assertEqual(add_text.mock_calls, [])
        self.assertEqual(actual_text_id, sentinel.old_text_id)

    def test_has_ngrams(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        store._conn.execute.return_value = cursor
        # Path one: there are n-grams.
        cursor.fetchone.return_value = True
        actual_result = store._has_ngrams(sentinel.text_id, sentinel.size)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_HAS_NGRAMS_SQL,
                                       [sentinel.text_id, sentinel.size]),
                          call.execute().fetchone()])
        self.assertEqual(actual_result, True)
        # Path two: there are no n-grams.
        store._conn.reset_mock()
        cursor.reset_mock()
        cursor.fetchone.return_value = None
        actual_result = store._has_ngrams(sentinel.text_id, sentinel.size)
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_HAS_NGRAMS_SQL,
                                       [sentinel.text_id, sentinel.size]),
                          call.execute().fetchone()])
        self.assertEqual(actual_result, False)

    def test_initialise_database(self):
        pass

    def test_intersection(self):
        labels = [sentinel.label1, sentinel.label2]
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = {}
        sort_labels = self._create_patch('tacl.DataStore._sort_labels', False)
        sort_labels.return_value = labels
        get_placeholders = self._create_patch(
            'tacl.DataStore._get_placeholders', False)
        get_placeholders.return_value = sentinel.placeholders
        log_query_plan = self._create_patch('tacl.DataStore._log_query_plan',
                                            False)
        input_fh = MagicMock(name='fh')
        csv = self._create_patch('tacl.DataStore._csv', False)
        csv.return_value = input_fh
        catalogue = MagicMock(name='catalogue')
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        output_fh = store.intersection(catalogue, input_fh)
        set_labels.assert_called_once_with(store, catalogue)
        get_placeholders.assert_called_once_with(labels)
        self.assertTrue(log_query_plan.called)
        sql = 'SELECT TextNGram.ngram, TextNGram.size, Text.work, Text.siglum, TextNGram.count, Text.label FROM Text, TextNGram WHERE Text.label IN (sentinel.placeholders) AND Text.id = TextNGram.text AND TextNGram.ngram IN (SELECT TextNGram.ngram FROM Text, TextNGram WHERE Text.label = ? AND Text.id = TextNGram.text AND TextNGram.ngram IN (SELECT TextNGram.ngram FROM Text, TextNGram WHERE Text.label = ? AND Text.id = TextNGram.text))'
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(sql, labels * 2)])
        csv.assert_called_once_with(cursor, tacl.constants.QUERY_FIELDNAMES,
                                    input_fh)
        self.assertEqual(input_fh, output_fh)

    def test_intersection_one_label(self):
        labels = [sentinel.label1]
        set_labels = self._create_patch('tacl.DataStore._set_labels')
        set_labels.return_value = {}
        sort_labels = self._create_patch('tacl.DataStore._sort_labels', False)
        sort_labels.return_value = labels
        output_fh = MagicMock(name='fh')
        catalogue = MagicMock(name='catalogue')
        store = tacl.DataStore(':memory:')
        self.assertRaises(MalformedQueryError, store.intersection, catalogue,
                          output_fh)

    def test_intersection_supplied_one_label(self):
        filenames = ['a.csv']
        labels = ['A']
        store = tacl.DataStore(':memory:')
        output_fh = MagicMock(name='fh')
        self.assertRaises(MalformedQueryError, store.intersection_supplied,
                          filenames, labels, output_fh)

    def test_check_diff_result(self):
        # Test the various possibilities that
        # DataStore._reduce_diff_results must handle.
        store = tacl.DataStore(':memory:')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        tokenize = tokenizer.tokenize
        join = tokenizer.joiner.join
        row = pd.Series(['ABC', 3, 'a', 'base', 1, 'A'],
                        index=tacl.constants.QUERY_FIELDNAMES)
        # N-gram is not composed of any existing (n-1)-gram.
        matches = {'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 1)
        # N-gram is composed entirely of existing (n-1)-grams.
        matches = {'AB': 1, 'BC': 1, 'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 1)
        # N-gram is composed partly by existing (n-1)-grams.
        matches = {'AB': 1, 'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 0)
        matches = {'BC': 1, 'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 0)
        # N-gram is composed of one or more n-grams with count 0.
        matches = {'AB': 0, 'BC': 1, 'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 0)
        matches = {'AB': 1, 'BC': 0, 'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 0)
        matches = {'AB': 0, 'BC': 0, 'CD': 1}
        actual_row = store._check_diff_result(row, matches, tokenize, join)
        self.assertEqual(actual_row['count'], 0)

    def test_reduce_diff_results_composed(self):
        # Consider the diff between a text "abcdefg" and
        # "abcABCDEFdGHIefg". Only fully composed n-grams (those made
        # up of two (n-1)-grams that are in the results) should be
        # kept.
        store = tacl.DataStore(':memory:')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        input_data = (
            ['cA', '2', 'a', 'base', '1', 'A'],
            ['AB', '2', 'a', 'base', '1', 'A'],
            ['B[C]', '2', 'a', 'base', '1', 'A'],
            ['[C]D', '2', 'a', 'base', '1', 'A'],
            ['DE', '2', 'a', 'base', '1', 'A'],
            ['EF', '2', 'a', 'base', '1', 'A'],
            ['Fd', '2', 'a', 'base', '1', 'A'],
            ['dG', '2', 'a', 'base', '1', 'A'],
            ['GH', '2', 'a', 'base', '1', 'A'],
            ['HI', '2', 'a', 'base', '1', 'A'],
            ['Ie', '2', 'a', 'base', '1', 'A'],
            ['cd', '2', 'b', 'base', '1', 'B'],
            ['de', '2', 'b', 'base', '1', 'B'],
            ['bcA', '3', 'a', 'base', '1', 'A'],
            ['cAB', '3', 'a', 'base', '1', 'A'],
            ['AB[C]', '3', 'a', 'base', '1', 'A'],
            ['B[C]D', '3', 'a', 'base', '1', 'A'],
            ['[C]DE', '3', 'a', 'base', '1', 'A'],
            ['DEF', '3', 'a', 'base', '1', 'A'],
            ['EFd', '3', 'a', 'base', '1', 'A'],
            ['FdG', '3', 'a', 'base', '1', 'A'],
            ['dGH', '3', 'a', 'base', '1', 'A'],
            ['GHI', '3', 'a', 'base', '1', 'A'],
            ['HIe', '3', 'a', 'base', '1', 'A'],
            ['Ief', '3', 'a', 'base', '1', 'A'],
            ['bcd', '3', 'b', 'base', '1', 'B'],
            ['cde', '3', 'b', 'base', '1', 'B'],
            ['def', '3', 'b', 'base', '1', 'B'],
            ['abcA', '4', 'a', 'base', '1', 'A'],
            ['bcAB', '4', 'a', 'base', '1', 'A'],
            ['cAB[C]', '4', 'a', 'base', '1', 'A'],
            ['AB[C]D', '4', 'a', 'base', '1', 'A'],
            ['B[C]DE', '4', 'a', 'base', '1', 'A'],
            ['[C]DEF', '4', 'a', 'base', '1', 'A'],
            ['DEFd', '4', 'a', 'base', '1', 'A'],
            ['EFdG', '4', 'a', 'base', '1', 'A'],
            ['FdGH', '4', 'a', 'base', '1', 'A'],
            ['dGHI', '4', 'a', 'base', '1', 'A'],
            ['GHIe', '4', 'a', 'base', '1', 'A'],
            ['HIef', '4', 'a', 'base', '1', 'A'],
            ['Iefg', '4', 'a', 'base', '1', 'A'],
            ['abcd', '4', 'b', 'base', '1', 'B'],
            ['bcde', '4', 'b', 'base', '1', 'B'],
            ['cdef', '4', 'b', 'base', '1', 'B'],
            ['defg', '4', 'b', 'base', '1', 'B'],
            ['abcde', '5', 'b', 'base', '1', 'B'],
            ['bcdef', '5', 'b', 'base', '1', 'B'],
            ['cdefg', '5', 'b', 'base', '1', 'B'])
        expected_rows = set(
            (('cA', '2', 'a', 'base', '1', 'A'),
             ('AB', '2', 'a', 'base', '1', 'A'),
             ('B[C]', '2', 'a', 'base', '1', 'A'),
             ('[C]D', '2', 'a', 'base', '1', 'A'),
             ('DE', '2', 'a', 'base', '1', 'A'),
             ('EF', '2', 'a', 'base', '1', 'A'),
             ('Fd', '2', 'a', 'base', '1', 'A'),
             ('dG', '2', 'a', 'base', '1', 'A'),
             ('GH', '2', 'a', 'base', '1', 'A'),
             ('HI', '2', 'a', 'base', '1', 'A'),
             ('Ie', '2', 'a', 'base', '1', 'A'),
             ('cd', '2', 'b', 'base', '1', 'B'),
             ('de', '2', 'b', 'base', '1', 'B'),
             ('cAB', '3', 'a', 'base', '1', 'A'),
             ('AB[C]', '3', 'a', 'base', '1', 'A'),
             ('B[C]D', '3', 'a', 'base', '1', 'A'),
             ('[C]DE', '3', 'a', 'base', '1', 'A'),
             ('DEF', '3', 'a', 'base', '1', 'A'),
             ('EFd', '3', 'a', 'base', '1', 'A'),
             ('FdG', '3', 'a', 'base', '1', 'A'),
             ('dGH', '3', 'a', 'base', '1', 'A'),
             ('GHI', '3', 'a', 'base', '1', 'A'),
             ('HIe', '3', 'a', 'base', '1', 'A'),
             ('cde', '3', 'b', 'base', '1', 'B'),
             ('cAB[C]', '4', 'a', 'base', '1', 'A'),
             ('AB[C]D', '4', 'a', 'base', '1', 'A'),
             ('B[C]DE', '4', 'a', 'base', '1', 'A'),
             ('[C]DEF', '4', 'a', 'base', '1', 'A'),
             ('DEFd', '4', 'a', 'base', '1', 'A'),
             ('EFdG', '4', 'a', 'base', '1', 'A'),
             ('FdGH', '4', 'a', 'base', '1', 'A'),
             ('dGHI', '4', 'a', 'base', '1', 'A'),
             ('GHIe', '4', 'a', 'base', '1', 'A')))
        actual_rows = self._reduce_diff(store, input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)

    def test_reduce_diff_no_overlap(self):
        # An n-gram that does not overlap at all with any (n-1)-gram
        # should be kept:
        #   abdef vs abcbde
        store = tacl.DataStore(':memory:')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        input_data = (
            ['ef', '2', 'a', 'base', '1', 'A'],
            ['abd', '3', 'a', 'base', '1', 'A'],
            ['def', '3', 'a', 'base', '1', 'A'],
            ['abde', '4', 'a', 'base', '1', 'A'],
            ['bdef', '4', 'a', 'base', '1', 'A'],
            ['abdef', '5', 'a', 'base', '1', 'A'],
            ['bc', '2', 'b', 'base', '1', 'B'],
            ['cb', '2', 'b', 'base', '1', 'B'],
            ['abc', '3', 'b', 'base', '1', 'B'],
            ['bcb', '3', 'b', 'base', '1', 'B'],
            ['cbd', '3', 'b', 'base', '1', 'B'],
            ['abcb', '4', 'b', 'base', '1', 'B'],
            ['bcbd', '4', 'b', 'base', '1', 'B'],
            ['cbde', '4', 'b', 'base', '1', 'B'],
            ['abcbd', '5', 'b', 'base', '1', 'B'],
            ['bcbde', '5', 'b', 'base', '1', 'B'],
            ['cbdef', '5', 'b', 'base', '1', 'B'],
            ['abcbde', '6', 'b', 'base', '1', 'B'],
            ['bcbdef', '6', 'b', 'base', '1', 'B'],
            ['abcbdef', '7', 'b', 'base', '1', 'B'])
        expected_rows = set(
            (('ef', '2', 'a', 'base', '1', 'A'),
             ('abd', '3', 'a', 'base', '1', 'A'),
             ('bc', '2', 'b', 'base', '1', 'B'),
             ('cb', '2', 'b', 'base', '1', 'B'),
             ('bcb', '3', 'b', 'base', '1', 'B')))
        actual_rows = self._reduce_diff(store, input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)

    def test_reduce_diff_size(self):
        # Consider a diff where the smallest gram for a witness is
        # larger than the smallest gram across all witnesses:
        #   abdef vs abcbdef
        store = tacl.DataStore(':memory:')
        tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS['cbeta'])
        input_data = (
            ['abd', '3', 'a', 'base', '1', 'A'],
            ['abde', '4', 'a', 'base', '1', 'A'],
            ['abdef', '5', 'a', 'base', '1', 'A'],
            ['bc', '2', 'b', 'base', '1', 'B'],
            ['cb', '2', 'b', 'base', '1', 'B'],
            ['abc', '3', 'b', 'base', '1', 'B'],
            ['bcb', '3', 'b', 'base', '1', 'B'],
            ['cbd', '3', 'b', 'base', '1', 'B'],
            ['abcb', '4', 'b', 'base', '1', 'B'],
            ['bcbd', '4', 'b', 'base', '1', 'B'],
            ['cbde', '4', 'b', 'base', '1', 'B'],
            ['abcbd', '5', 'b', 'base', '1', 'B'],
            ['bcbde', '5', 'b', 'base', '1', 'B'],
            ['cbdef', '5', 'b', 'base', '1', 'B'],
            ['abcbde', '6', 'b', 'base', '1', 'B'],
            ['bcbdef', '6', 'b', 'base', '1', 'B'],
            ['abcbdef', '7', 'b', 'base', '1', 'B'])
        expected_rows = set(
            (('abd', '3', 'a', 'base', '1', 'A'),
             ('bc', '2', 'b', 'base', '1', 'B'),
             ('cb', '2', 'b', 'base', '1', 'B'),
             ('bcb', '3', 'b', 'base', '1', 'B')))
        actual_rows = self._reduce_diff(store, input_data, tokenizer)
        self.assertEqual(set(actual_rows), expected_rows)

    def _reduce_diff(self, store, input_data, tokenizer):
        in_fh = self._create_csv(input_data)
        out_fh = io.StringIO(newline='')
        return self._get_rows_from_csv(store._reduce_diff_results(
            in_fh, tokenizer, out_fh))

    def test_set_labels(self):
        catalogue = collections.OrderedDict(
            [(sentinel.text1, sentinel.label1),
             (sentinel.text2, sentinel.label2),
             (sentinel.text3, sentinel.label1)])
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        store._conn.execute.return_value = cursor
        cursor.fetchone.return_value = {'token_count': 10}
        actual_labels = store._set_labels(catalogue)
        expected_labels = {sentinel.label1: 20, sentinel.label2: 10}
        connection_calls = [
            call.execute(tacl.constants.UPDATE_LABELS_SQL, ['']),
            call.execute(tacl.constants.UPDATE_LABEL_SQL,
                         [sentinel.label1, sentinel.text1]),
            call.execute(tacl.constants.SELECT_TEXT_TOKEN_COUNT_SQL,
                         [sentinel.text1]),
            call.execute(tacl.constants.UPDATE_LABEL_SQL,
                         [sentinel.label2, sentinel.text2]),
            call.execute(tacl.constants.SELECT_TEXT_TOKEN_COUNT_SQL,
                         [sentinel.text2]),
            call.execute(tacl.constants.UPDATE_LABEL_SQL,
                         [sentinel.label1, sentinel.text3]),
            call.execute(tacl.constants.SELECT_TEXT_TOKEN_COUNT_SQL,
                         [sentinel.text3]),
            call.commit()]
        for connection_call in connection_calls:
            self.assertIn(connection_call, store._conn.mock_calls)
        self.assertEqual(actual_labels, expected_labels)

    def test_sort_labels(self):
        store = tacl.DataStore(':memory:')
        label_data = {sentinel.label1: 2, sentinel.label2: 3,
                      sentinel.label3: 1}
        actual_labels = store._sort_labels(label_data)
        expected_labels = [sentinel.label2, sentinel.label1, sentinel.label3]
        self.assertEqual(actual_labels, expected_labels)

    def test_update_text_record(self):
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_checksum.return_value = sentinel.checksum
        tokens = [sentinel.token]
        text.get_tokens.return_value = tokens
        store._update_text_record(text, sentinel.text_id)
        self.assertEqual(text.mock_calls,
                         [call.get_checksum(), call.get_tokens()])
        store._conn.execute.assert_called_once_with(
            tacl.constants.UPDATE_TEXT_SQL,
            [sentinel.checksum, len(tokens), sentinel.text_id])
        store._conn.commit.assert_called_once_with()

    def test_validate_true(self):
        corpus = MagicMock(spec_set=tacl.Corpus)
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_checksum.return_value = sentinel.checksum
        text.get_names.return_value = (sentinel.name, sentinel.siglum)
        corpus.get_witnesses.return_value = (text,)
        catalogue = collections.OrderedDict(
            [(sentinel.text1, sentinel.label1),
             (sentinel.text2, sentinel.label2),
             (sentinel.text3, sentinel.label1)])
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        cursor.fetchone.return_value = {'checksum': sentinel.checksum}
        actual_result = store.validate(corpus, catalogue)
        corpus.get_witnesses.assert_has_calls([
            call(sentinel.text1), call(sentinel.text2), call(sentinel.text3)])
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone(),
                          call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone(),
                          call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone()])
        self.assertEqual(actual_result, True)

    def test_validate_missing_record(self):
        corpus = MagicMock(spec_set=tacl.Corpus)
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_checksum.return_value = sentinel.checksum
        text.get_names.return_value = (sentinel.name, sentinel.siglum)
        corpus.get_witnesses.return_value = (text,)
        catalogue = {sentinel.text1: sentinel.label1}
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        cursor.fetchone.return_value = None
        actual_result = store.validate(corpus, catalogue)
        corpus.get_witnesses.assert_has_calls([call(sentinel.text1)])
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone()])
        self.assertEqual(actual_result, False)

    def test_validate_mismatched_checksums(self):
        corpus = MagicMock(spec_set=tacl.Corpus)
        text = MagicMock(spec_set=tacl.WitnessText)
        text.get_checksum.return_value = sentinel.checksum
        text.get_names.return_value = (sentinel.name, sentinel.siglum)
        corpus.get_witnesses.return_value = (text,)
        catalogue = {sentinel.text1: sentinel.label1}
        store = tacl.DataStore(':memory:')
        store._conn = MagicMock(spec_set=sqlite3.Connection)
        cursor = store._conn.execute.return_value
        cursor.fetchone.return_value = {'checksum': sentinel.checksum2}
        actual_result = store.validate(corpus, catalogue)
        corpus.get_witnesses.assert_has_calls([call(sentinel.text1)])
        self.assertEqual(store._conn.mock_calls,
                         [call.execute(tacl.constants.SELECT_TEXT_SQL,
                                       [sentinel.name, sentinel.siglum]),
                          call.execute().fetchone()])
        self.assertEqual(actual_result, False)


if __name__ == '__main__':
    unittest.main()
