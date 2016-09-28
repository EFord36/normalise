# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import re
import pickle
from io import open

from math import log
from nltk import FreqDist as fd
from normalise.detect import wordlist, mod_path
from normalise.expand_NUMB import expand_NUM
from normalise.tagger import has_digit
with open('{}/data/word_tokenized_lowered.pickle'.format(mod_path), mode='rb') as f:
    word_tokenized_lowered = pickle.load(f)


def expand_HTAG(word):
    """Expand tokens tagged HTAG."""
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


def email_word(word):
    if not word:
        return ''
    elif word.isdigit():
        return ' '.join(word)
    elif word in wordlist:
        return word
    elif word in ['co', 'com', 'org']:
        return word
    else:
        if email_dig_pattern.match(word):
            m = email_dig_pattern.match(word)
            groups = [m.group(1), m.group(2), m.group(3)]
            return ' '.join([email_word(group) for group in groups if group])
        elif len(word) < 4:
            return ' '.join(word.upper())
        else:
            return expand_HTAG(word)


def expand_URL(word):
    """Expand tokens tagged URL."""
    try:
        if '@' in word:
            out = ''
            current = ''
            for c in word:
                if c == '.':
                    # out += ' ' + expand_HTAG(current) + ' dot'
                    out += ' {} dot'.format(current if current in wordlist else email_word(current))
                    current = ''
                elif c == '@':
                    # out += ' ' + expand_HTAG(current) + ' at'
                    out += ' {} at'.format(current if current in wordlist else email_word(current))
                    current = ''
                else:
                    current += c
            if current:
                out += ' ' + current
            return out
        starts = {"http://": "", "https://": "", "www.": "W W W dot"}
        ends = {".com": "dot com", ".org": "dot org",
                ".org.uk": "dot org dot U K", ".co.uk": "dot co dot U K"}
        m = urlstart_pattern.match(word)
        n = urlend_pattern.match(word)
        exp = ''
        if m.group(1) and n:
            start = m.group(1)
            middle = urlend_pattern.match(m.group(2))
            end = middle.group(2)
            exp += (starts[start] + " "
                    + infer_spaces(middle.group(1))
                    + " " + ends[end])
        elif n:
            middle = n.group(1)
            end = n.group(2)
            exp += infer_spaces(middle) + " " + ends[end]
        else:
            return word
        return exp
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        return word


# Build a cost dict, assuming Zipf's law and cost = -math.log(probability).
brown = word_tokenized_lowered[:1161192]
words = [w for w, freq in fd(brown).most_common()]
wordcost = dict((k, log((i + 1) * log(len(words))))
                for i, k in enumerate(words))
maxword = max(len(x) for x in words)


def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i - maxword):i]))
        return min((c + wordcost.get(s[i - k - 1:i], 9e999), k + 1)
                   for k, c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1, len(s) + 1):
        c, k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i > 0:
        c, k = best_match(i)
        assert c == cost[i]
        out.append(s[i - k: i])
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
(https?://|       # 'http' followed by optional 's', then '://' OR
www\.)            # 'www.'
(.*)              # followed by anything
''', re.VERBOSE | re.IGNORECASE)

urlend_pattern = re.compile('''
(.*)              # any number of characters
(\.com|           # '.com' OR
\.org|            # '.org' OR
\.org\.uk|        # '.org.uk' OR
\.co\.uk)         # '.co.uk'
$                 # end of string
''', re.VERBOSE | re.IGNORECASE)

email_dig_pattern = re.compile('''
([A-Za-z]*)       # 0 or more letters
([0-9]+)          # 1 or more digits
([A-Za-z]*)       # 0 or more letters
$                 # end of string
''', re.VERBOSE | re.IGNORECASE)
