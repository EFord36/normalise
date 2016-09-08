# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 13:19:09 2016

@author: emmaflint
"""
import re
import pickle

from math import log
from nltk import FreqDist as fd
from NSW_new import wordlist
from expand_NUMB import expand_NUM

with open('word_tokenized_lowered.pickle', mode='rb') as file:
    word_tokenized_lowered = pickle.load(file)


def expand_HTAG(word):
    m = hashtag_pattern.match(word)
    string = m.group(2)
    exp = 'hashtag'
    if string in wordlist:
        exp = exp + " " + string
    else:
        exp = exp + " " + infer_spaces(m.group(2))
    if m.group(3):
        exp = exp + " " + expand_NUM(m.group(3))
    return exp
   

# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
brown = word_tokenized_lowered[:1161192]
words = [w for w, freq in fd(brown).most_common()]
wordcost = dict((k, log((i+1)*log(len(words)))) for i,k in enumerate(words))
maxword = max(len(x) for x in words)

def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))
                
hashtag_pattern = re.compile('''
(\#)
([A-Za-z]+
[_-]?
[A-Za-z]*)
([0-9]*)
''', re.VERBOSE) 
