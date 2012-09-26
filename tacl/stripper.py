# -*- coding: utf-8 -*-

import os
import re


# Each textual line (and, sadly, some non-textual lines) begins with a
# string representing the details of the text and the
# line. Unfortunately the format of this line varies in the crucial
# ending character(s). In 2682, at least, || is used; this is not
# handled in the regular expression below.
line_prefix_re = re.compile(ur'^T[^║:∥]*[║:∥](.*)$')
char_removal_re = re.compile(ur'[\(\)\? 。]')
raw_code_removal_re = re.compile(r'&[^;]*;')


class Stripper (object):

    """Class used for preprocessing a corpus of texts by stripping out
    all material that is not the textual material proper."""

    def __init__ (self, input_dir, output_dir):
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)

    def strip_files (self):
        for filename in os.listdir(self._input_dir):
            self.strip_file(filename)

    def strip_file (self, filename):
        file_path = os.path.join(self._input_dir, filename)
        root, ext = os.path.splitext(filename)
        stripped_file_path = os.path.join(self._output_dir,
                                          root + '-stripped' + ext)
        with open(file_path, 'rU') as input_file:
            with open(stripped_file_path, 'w') as output_file:
                for line in input_file:
                    stripped_line = self.strip_line(line.decode('utf-8'))
                    if stripped_line:
                        output_file.write(stripped_line.encode('utf-8'))

    def strip_line (self, line):
        new_line = ''
        match = line_prefix_re.search(line)
        if match:
            new_line = match.group(1)
            new_line = char_removal_re.subn('', new_line)[0]
            new_line = raw_code_removal_re.subn('', new_line)[0]
        return new_line
