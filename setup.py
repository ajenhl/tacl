#!/usr/bin/env python3

from setuptools import setup


with open('README.rst') as fh:
    long_description = fh.read()

setup(name='tacl',
      version='3.0.0',
      description='Text analyser for corpus linguistics',
      long_description=long_description,
      author='Jamie Norrish',
      author_email='jamie@artefact.org.nz',
      url='https://github.com/ajenhl/tacl',
      packages=['tacl', 'tacl.command'],
      entry_points={
          'console_scripts': [
              'tacl=tacl.command.tacl_script:main',
              'tacl-helper=tacl.command.tacl_helper_script:main',
              'tacl-jitc=tacl.command.jitc_script:main',
          ],
      },
      package_data={
          'tacl': ['assets/jitc/*.js', 'assets/jitc/*.css',
                   'assets/results_highlight/*.js', 'assets/templates/*.html',
                   'assets/xslt/*.xsl'],
      },
      install_requires=['biopython', 'colorlog', 'Jinja2', 'lxml',
                        'pandas>=0.17.0'],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3',
          'Topic :: Text Processing :: Linguistic',
      ],
      test_suite='tests',
      )
