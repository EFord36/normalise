# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import os
import sys
import pickle
from io import open

from nltk import WordNetLemmatizer
from nltk.corpus import words
from nltk.corpus import nps_chat
from nltk.corpus import brown
from nltk.corpus import names
from normalise.data.contraction_list import contractions
from normalise.data.tech_words import tech_words

mod_path = os.path.dirname(__file__)

with open('{}/data/wordlist.pickle'.format(mod_path), mode='rb') as file:
    wordlist = pickle.load(file)

with open('{}/data/fake_data.pickle'.format(mod_path), mode='rb') as file:
    fake_data = pickle.load(file)

if __name__ == '__main__':
    word_tokenized = brown.words() + nps_chat.words() + fake_data
    brown_lower = {w.lower() for w in brown.words()
                   if len(w) > 4 and w.isalpha()}
    names_lower = {w.lower() for w in names.words()}
    words_lower = {w.lower() for w in words.words('en') if len(w) > 1}
    wordlist = brown_lower | names_lower | words_lower | set(tech_words) | {'I', 'i', 'a', 'A'}
    word_tokenized_lowered = [w.lower() if w.lower() in wordlist
                              else w for w in word_tokenized]
    word_tokenized = list(word_tokenized)


# Conditions for identification of NSWs.
def cond1(w):
    """ Return word if its lower-cased form is not in the wordlist."""
    return w.lower() not in wordlist or w == 'US'


def cond2(w):
    """ Return word if its lemmatised form is not in the wordlist."""
    wnl = WordNetLemmatizer()
    return wnl.lemmatize(w.lower()) not in wordlist


def cond3(w):
    """ Return word if it is not single punctuation."""
    if len(w) > 2:
        return True
    bools = [l.isalnum() for l in w]
    if True in bools:
        return True
    else:
        return False


def cond4(w):
    """ Return word if its non-possessive form (with 's/s' removed) is not in
    the wordlist.
    """
    return (not ((w.endswith("'s") or w.endswith("s'")) and
            w.lower()[:-2] in wordlist))


def ident_NSW(w):
    """ Identify NSWs.

    Return word if it satisfies all four above conditions.
    """
    return (cond1(w) and cond2(w) and cond3(w) and cond4(w)
            and not (w.lower() in contractions))


def create_NSW_dict(text, verbose=True):
    "Create dictionary of NSWs in text: keys are indices, values NSWs"
    return {i: text[i] for i in range(len(text)) if ident_NSW(text[i])}
