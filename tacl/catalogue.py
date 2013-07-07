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

    def load (self, path):
        """Loads the data from `path` into the catalogue.

        :param path: path to catalogue file
        :type path: `str`

        """
        reader = csv.reader(open(path, 'r', encoding='utf-8', newline=''),
                            delimiter=' ', skipinitialspace=True)
        for row in reader:
            if len(row) > 1 and row[1]:
                self[row[0]] = row[1]

    def save (self, path):
        """Saves this catalogue's data to `path`.

        :param path: file path to save catalogue data to
        :type path: `str`

        """
        writer = csv.writer(open(path, 'w', newline=''), delimiter=' ')
        rows = list(self.items())
        rows.sort(key=lambda x: x[0])
        writer.writerows(rows)
