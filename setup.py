#!/usr/bin/env python

from distutils.core import setup


setup(name='tacl',
      version='1.0',
      description='Text analyser for corpus linguistics',
      author='Jamie Norrish',
      author_email='jamie@artefact.org.nz',
      url='https://github.com/ajenhl/tacl',
      packages=['tacl'],
      scripts=['bin/tacl', 'bin/tacl-helper'],
      requires=['lxml', 'pandas'],
      classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
        ]
      )
