import csv
import os


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

    def labels (self):
        """Returns a list of the labels used in this catalogue.

        :rtype: `list`

        """
        labels = set(self.values())
        labels.discard('')
        return list(labels)

    def load (self, path):
        """Loads the data from `path` into the catalogue.

        :param path: path to catalogue file
        :type path: `str`

        """
        reader = csv.reader(open(path), delimiter=' ', skipinitialspace=True)
        for row in reader:
            if len(row) > 1:
                self[row[0]] = row[1]

    def save (self, path):
        """Saves this catalogue's data to `path`.

        :param path: file path to save catalogue data to
        :type path: `str`

        """
        writer = csv.writer(open(path, 'w'), delimiter=' ')
        rows = list(self.items())
        rows.sort(key=lambda x: x[0])
        writer.writerows(rows)
