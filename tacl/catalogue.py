import csv
import os

from .constants import CATALOGUE_TEXT_RELABELLED_ERROR
from .exceptions import MalformedCatalogueError


class Catalogue (dict):

    def generate (self, path, label):
        """Creates default data from the corpus at `path`, marking all
        texts with `label`.

        :param path: path to a corpus directory
        :type path: `str`
        :param label: label to categorise each text as
        :type label: `str`

        """
        for filename in os.listdir(path):
            self[filename] = label

    def load (self, path):
        """Loads the data from `path` into the catalogue.

        :param path: path to catalogue file
        :type path: `str`

        """
        fieldnames = ['text', 'label']
        with open(path, 'r', encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh, delimiter=' ', fieldnames=fieldnames,
                                    skipinitialspace=True)
            for row in reader:
                text, label = row['text'], row['label']
                if label:
                    if text in self:
                        raise MalformedCatalogueError(
                            CATALOGUE_TEXT_RELABELLED_ERROR.format(text))
                    self[text] = label

    def save (self, path):
        """Saves this catalogue's data to `path`.

        :param path: file path to save catalogue data to
        :type path: `str`

        """
        writer = csv.writer(open(path, 'w', newline=''), delimiter=' ')
        rows = list(self.items())
        rows.sort(key=lambda x: x[0])
        writer.writerows(rows)
