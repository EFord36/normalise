# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 13:19:09 2016

@author: emmaflint
"""
import re
import pickle

from math import log
from nltk import FreqDist as fd
from normalise.NSW_new import wordlist
from normalise.expand_NUMB import expand_NUM

with open('../normalise/data/word_tokenized_lowered.pickle', mode='rb') as file:
    word_tokenized_lowered = pickle.load(file)


def expand_HTAG(word):
    try:
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
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        return word

def expand_URL(word):
    try:
        starts = ["http://", "https://", "www."]
        starts_exp = ['', '', 'W W W dot']
        ends = [".com", ".org", ".org.uk", ".co.uk"]
        ends_exp = ["dot com", "dot org", "dot org dot U K", "dot co dot U K"]
        m = urlstart_pattern.match(word)
        n = urlend_pattern.match(word)
        exp = ''
        if m.group(1) and n:
            start = m.group(1)
            middle = urlend_pattern.match(m.group(2))
            end = middle.group(2)
            exp += (starts_exp[starts.index(start)] + " " + infer_spaces(middle.group(1))
                   + " " + ends_exp[ends.index(end)])
        elif n:
            middle = n.group(1)
            end = n.group(2)
            exp += infer_spaces(middle) + " " + ends_exp[ends.index(end)]
        else:
            return word
        return exp
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        return word


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

urlstart_pattern = re.compile('''
(https?://|            #'http' followed by optional 's', then '://' OR
www\.|)
(.*)              #'www.'
''', re.VERBOSE | re.IGNORECASE)

urlend_pattern = re.compile('''
(.*)                      #any number of characters                      # '.'
(\.com|                 # 'com' OR
\.org|
\.org\.uk|          # 'org' followed optionally by '.uk' OR
\.co\.uk)               # 'co.uk'
$                       #end of string
''', re.VERBOSE | re.IGNORECASE)
