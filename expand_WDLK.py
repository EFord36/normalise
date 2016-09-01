import re
import pickle

from class_ALPHA import triple_rep
from spellcheck import correct

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)


def expand_WDLK(word):
    if triple_rep(word):
        return expand_FNSP(word)
    else:
        return correct(word)


def expand_FNSP(w):
    """Return 'original' word from FNSP."""
    reg = create_regexp(w)
    final = ''
    for e in wordlist:
        m = re.match(reg, e)
        if m:
            final = m.string
            break
    if final:
        return final
    else:
        red_word = w[0]
        for i in range(1, len(w)):
            if w[i] != w[i - 1]:
                red_word += w[i]
        return red_word


def create_regexp(w):
    """Return regular expression representing word with repeated cs 1+ times.
    """
    regexp = w[0]
    for i in range(1, len(w)):
        if w[i] == w[i - 1]:
            if regexp[-1] != '+':
                regexp += '+'
        else:
            regexp += w[i]
    regexp += '$'
    return regexp
