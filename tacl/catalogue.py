import csv
import os

from .constants import CATALOGUE_WORK_RELABELLED_ERROR
from .exceptions import MalformedCatalogueError


class Catalogue (dict):

    def __init__(self, *args, **kwargs):
        self._ordered_labels = []
        super().__init__(*args, **kwargs)

    def generate(self, path, label):
        """Creates default data from the corpus at `path`, marking all
        works with `label`.

        :param path: path to a corpus directory
        :type path: `str`
        :param label: label to categorise each work as
        :type label: `str`

        """
        for filename in os.listdir(path):
            self[filename] = label

    @property
    def ordered_labels(self):
        """Returns the labels in their order of first occurrence from loading.

        If the catalogue was populated in whole or part through means
        other than the load method, the string sorted labels are
        returned instead.

        :rtype: `list`

        """
        return self._ordered_labels or self.labels

    @property
    def labels(self):
        """Returns the distinct labels defined in the catalogue.

        :rtype: `list`

        """
        return sorted(set(self.values()))

    def load(self, path):
        """Loads the data from `path` into the catalogue.

        :param path: path to catalogue file
        :type path: `str`

        """
        fieldnames = ['work', 'label']
        with open(path, 'r', encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh, delimiter=' ', fieldnames=fieldnames,
                                    skipinitialspace=True)
            for row in reader:
                work, label = row['work'], row['label']
                if label:
                    if label not in self._ordered_labels:
                        self._ordered_labels.append(label)
                    if work in self:
                        raise MalformedCatalogueError(
                            CATALOGUE_WORK_RELABELLED_ERROR.format(work))
                    self[work] = label

    def save(self, path):
        """Saves this catalogue's data to `path`.

        :param path: file path to save catalogue data to
        :type path: `str`

        """
        writer = csv.writer(open(path, 'w', newline=''), delimiter=' ')
        rows = list(self.items())
        rows.sort(key=lambda x: x[0])
        writer.writerows(rows)
