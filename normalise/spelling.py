# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import re
from collections import defaultdict
from io import open

import nltk

from normalise.detect import mod_path
from normalise.expand_EXPN import brown_common

with open('{}/data/wordlist.pickle'.format(mod_path), mode='rb') as file:
    wordlist = pickle.load(file)
