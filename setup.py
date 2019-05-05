# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='normalise',
    platforms=['any'],
    packages=find_packages(exclude=['tests', 'evaluation']),
    include_package_data=True,
    version='0.1.9',
    summary='A module to normalise non-standard words in text',
    description=long_description,
    description_content_type='text/markdown',
    author='Elliot Ford, Emma Flint',
    author_email='elliot.ford@hotmail.co.uk',
    license="GPL",
    url='https://github.com/EFord36/normalise',
    download_url='https://github.com/EFord36/normalise/tarball/0.1.9',
    keywords=['normalisation', 'text', 'pre-processing'],
    classifiers=[
        "Natural Language :: English",
        "Topic :: Text Processing",
        ("License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)")
    ],
    install_requires=['nltk', 'scikit-learn', 'numpy', 'roman', 'scipy'],
    entry_points={'console_scripts': ['normalise=normalise.command_line:main']}
)
