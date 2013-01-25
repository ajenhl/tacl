#!/usr/bin/env python

from distutils.core import setup


setup(name='tacl',
      version='1.0',
      description='Text analyser for corpus linguistics',
      author='Jamie Norrish',
      author_email='jamie@artefact.org.nz',
      packages=['tacl'],
      scripts=['bin/tacl'],
      requires=['lxml'],
      )
