# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 13:54:25 2016

@author: Elliot
"""

from __future__ import division, print_function, unicode_literals

import pickle
import nltk
from nltk.corpus import words
from nltk.corpus import nps_chat
from nltk.corpus import brown
from nltk.corpus import names
from contraction_list import contractions

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

if __name__ == '__main__':
    word_tokenized = brown.words() + nps_chat.words()
    brown_lower = {w.lower() for w in brown.words() if len(w) > 4 and w.isalpha()}
    names_lower = {w.lower() for w in names.words()}
    words_lower = {w.lower() for w in words.words('en') if len(w) > 1}
    wordlist = brown_lower | names_lower | words_lower | {'I', 'i', 'a', 'A'}
    word_tokenized_lowered = [w.lower() if w.lower() in wordlist
                              else w for w in word_tokenized]


# Conditions for identification of NSWs.
def cond1(w):
    """ Return word if its lower-cased form is not in the wordlist."""
    return w.lower() not in wordlist


def cond2(w):
    """ Return word if its lemmatised form is not in the wordlist."""
    wnl = nltk.WordNetLemmatizer()
    return wnl.lemmatize(w.lower()) not in wordlist


def cond3(w):
    """ Return word if it is not single punctuation."""
    return not(len(w) <= 2 and not w.isalnum())


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


def create_NSW_dict(text):
    "Create dictionary of NSWs in text: keys are indices, values NSWs"
    out = {}
    for i in range(len(text)):
        w = text[i]
        if ident_NSW(w):
            out[i] = w
    return out
