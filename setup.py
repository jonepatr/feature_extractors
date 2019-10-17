#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Feature Extractors',
    version='0.1',
    description='Feature Extractors',
    author='Patrik Jonell',
    author_email='pjjonell@kth.se',
    install_requires=['docker'],
    packages=['feature_extractors'],
    scripts=['bin/feature_extractor']
)