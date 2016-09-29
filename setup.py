# -*- coding: utf-8 -*-

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='normalise',
    platforms=['any'],
    packages=find_packages(exclude=['tests', 'evaluation']),
    package_data={'normalise': ['data/*.pickle']},
    include_package_data=True,
    version='0.1.0',
    description='A module to normalise non-standard words in text',
    author='Elliot Ford, Emma Flint',
    author_email='ef355@cam.ac.uk',
    license="GPL",
    url='https://github.com/EFord36/normalise',
    download_url='https://github.com/EFord36/normalise/tarball/1.0',
    keywords=['normalisation', 'text', 'pre-processing'],
    classifiers=[
        "Natural Language :: English",
        "Topic :: Text Processing",
        ("License :: OSI Approved :: "
        "GNU General Public License v3 or later (GPLv3+)")
    ],
    install_requires=['nltk', 'scikit-learn', 'numpy', 'roman'],
    entry_points={'console_scripts': ['normalise=normalise.command_line:main']}
)
