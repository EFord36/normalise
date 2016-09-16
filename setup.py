from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

setup(
    name='Text-Normalisation',
    packages=['Text-Normalisation'],
    version='1.0',
    description='A module to normalise non-standard words in text',
    author='Elliot Ford, Emma Flint',
    author_email='ef355@cam.ac.uk',
    license="GPL"
    url='https://github.com/EFord36/Text-Normalisation',
    download_url='https://github.com/EFord36/Text-Normalisation/tarball/1.0',
    keywords=['normalisation', 'text', 'pre-processing'],
    classifiers=[
        "Natural Language :: English",
        "Topic :: Text Processing",
        "License :: OSI Approved :: "
        + "GNU General Public License v3 or later (GPLv3+)"
    ],
    install_requires=['nltk', 'scikit-learn', 'numpy']
)