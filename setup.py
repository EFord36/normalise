# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='normalise',
    platforms=['any'],
    packages=find_packages(exclude=['tests', 'evaluation']),
    package_data={'normalise': ['data/*.pickle']},
    include_package_data=True,
    version='0.1',
    description='A module to normalise non-standard words in text',
    long_description=long_description,
    author='Elliot Ford, Emma Flint',
    author_email='ef355@cam.ac.uk',
    license="GPL",
    url='https://github.com/EFord36/normalise',
    download_url='https://github.com/EFord36/normalise/tarball/0.1',
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
