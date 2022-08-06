import copy
import csv
import os

from .constants import CATALOGUE_WORK_RELABELLED_ERROR
from .exceptions import MalformedCatalogueError


class Catalogue (dict):

    """Dictionary mapping works (keys) to labels (values). Each work may
    have only one label."""

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

    def get_works_by_label(self, label):
        """Returns a list of works associated with `label`.

        :param label: label of works to be returned
        :type label: `str`
        :rtype: `list` of `str`

        """
        return [work for work, c_label in self.items() if c_label == label]

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

    def relabel(self, label_map):
        """Returns a copy of the catalogue with the labels remapped according
        to `label_map`.

        `label_map` is a dictionary mapping existing labels to new
        labels. Any existing label that is not given a mapping is
        deleted from the resulting catalogue.

        :param label_map: mapping of labels to new labels
        :type label_map: `dict`
        :rtype: `tacl.Catalogue`

        """
        catalogue = copy.deepcopy(self)
        to_delete = set()
        for work, old_label in catalogue.items():
            if old_label in label_map:
                catalogue[work] = label_map[old_label]
            else:
                to_delete.add(catalogue[work])
        for label in to_delete:
            catalogue.remove_label(label)
        return catalogue

    def remove_label(self, label):
        """Removes `label` from the catalogue, by removing all works carrying
        it.

        :param label: label to remove
        :type label: `str`

        """
        works_to_delete = []
        for work, work_label in self.items():
            if work_label == label:
                works_to_delete.append(work)
        for work in works_to_delete:
            del self[work]
        if self._ordered_labels:
            self._ordered_labels.remove(label)

    def save(self, path, sort=True):
        """Saves this catalogue's data to `path`.

        :param path: file path to save catalogue data to
        :type path: `str`
        :param sort: whether to sort by work name or not
        :type sort: `bool`

        """
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            writer = csv.writer(fh, delimiter=' ')
            rows = list(self.items())
            if sort:
                rows.sort(key=lambda x: x[0])
            writer.writerows(rows)
