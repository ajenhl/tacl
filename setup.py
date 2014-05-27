#!/usr/bin/env python

from distutils.core import setup


with open('README.rst') as fh:
    long_description = fh.read()

setup(name='tacl',
      version='1.1.0',
      description='Text analyser for corpus linguistics',
      long_description=long_description,
      author='Jamie Norrish',
      author_email='jamie@artefact.org.nz',
      url='https://github.com/ajenhl/tacl',
      packages=['tacl'],
      scripts=['bin/tacl', 'bin/tacl-helper'],
      requires=['biopython', 'lxml', 'pandas'],
      install_requires=['biopython', 'lxml', 'pandas'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3',
          'Topic :: Text Processing :: Linguistic',
        ]
      )
