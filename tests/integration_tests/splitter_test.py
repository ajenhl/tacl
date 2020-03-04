import os
import shutil
import tempfile
import unittest

import tacl
from tacl.exceptions import MalformedSplitConfigurationError
from ..tacl_test_case import TaclTestCase


class SplitterIntegrationTestCase(TaclTestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        self._data_dir = os.path.join(base_dir, 'data', 'splitter')
        self._corpus_dir = os.path.join(self._data_dir, 'corpus')
        self._tokenizer = tacl.Tokenizer(*tacl.constants.TOKENIZERS[
            tacl.constants.TOKENIZER_CHOICE_CBETA])
        self._conf_dir = os.path.join(self._data_dir, 'conf')
        self._expected_dir = os.path.join(self._data_dir, 'expected')

    def _setup(self, actual_dir):
        corpus_dir = os.path.join(actual_dir, 'corpus')
        shutil.copytree(self._corpus_dir, corpus_dir)
        corpus = tacl.Corpus(corpus_dir, self._tokenizer)
        splitter = tacl.Splitter(corpus)
        return splitter, corpus_dir

    def _test_error_raised(self, conf_name):
        with tempfile.TemporaryDirectory() as actual_dir:
            splitter, corpus_conf = self._setup(actual_dir)
            conf_path = os.path.join(self._conf_dir, conf_name)
            self.assertRaises(MalformedSplitConfigurationError, splitter.split,
                              conf_path)

    def test_splitter_correct(self):
        with tempfile.TemporaryDirectory() as actual_dir:
            splitter, corpus_dir = self._setup(actual_dir)
            expected_dir = os.path.join(self._data_dir, 'expected', 'A-conf')
            conf_path = os.path.join(self._conf_dir, 'A.xml')
            splitter.split(conf_path)
            self._compare_dirs(corpus_dir, expected_dir)

    def test_splitter_delete(self):
        with tempfile.TemporaryDirectory() as actual_dir:
            splitter, corpus_dir = self._setup(actual_dir)
            expected_dir = os.path.join(self._data_dir, 'expected', 'I-conf')
            conf_path = os.path.join(self._conf_dir, 'I.xml')
            splitter.split(conf_path)
            self._compare_dirs(corpus_dir, expected_dir)

    def test_splitter_existing_directory(self):
        """Tests that an error is raised if a split will create output in a
        pre-existing directory."""
        with tempfile.TemporaryDirectory() as actual_dir:
            splitter, corpus_dir = self._setup(actual_dir)
            os.mkdir(os.path.join(corpus_dir, 'existing'))
            conf_path = os.path.join(self._conf_dir, 'H.xml')
            self.assertRaises(MalformedSplitConfigurationError, splitter.split,
                              conf_path)

    def test_splitter_invalid_witness(self):
        """Tests that an error is raised if a split part specifies a witness
        that does not exist for the source work."""
        self._test_error_raised('G.xml')

    def test_splitter_missing_end(self):
        """Tests that an error is raised if a split part specifies an end
        string that does not occur in the text."""
        self._test_error_raised('C.xml')

    def test_splitter_missing_start(self):
        self._test_error_raised('B.xml')

    def test_splitter_missing_whole(self):
        self._test_error_raised('D.xml')

    def test_splitter_missing_witnesses(self):
        """Tests that an error is raised if a split conf part has no
        witnesses."""
        self._test_error_raised('F.xml')

    def test_splitter_missing_work(self):
        """Tests that an error is raised if a split conf file references a
        work that does not exist in the corpus."""
        self._test_error_raised('missing.xml')

    def test_splitter_switched_start_end(self):
        """Tests that an error is raised if a split conf part has a start
        string that occurs after an end string."""
        self._test_error_raised('E.xml')


if __name__ == '__main__':
    unittest.main()
