# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 15:15:56 2016

@author: Elliot
"""
import nltk
import re
wordlist = nltk.corpus.words.words()


def create_regexp(w):
    """Return regular expression representing word with repeated cs 1+ times.
    """
    regexp = w[0]
    for i in range(1, len(w)):
        if w[i] == w[i-1]:
            if regexp[-1] != '+':
                regexp += '+'
        else:
            regexp += w[i]
    regexp += '$'
    return regexp


def expand_FNSP(w):
    """Return 'original' word from FNSP."""
    if '*' in w:
        return FNSP_ast(w)
    else:
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
                if w[i] != w[i-1]:
                    red_word += w[i]
            return red_word


def FNSP_ast(w):
    """Return 'original' rude word from asterisked FNSP."""
    rude = ['ass', 'asshole', 'balls', 'bitch', 'cunt', 'cock', 'crap',  'cum',
            'dick' 'fuck', 'pussy', 'shit', 'tits', 'twat']
    candidates = [r for r in rude if len(r) == len(w)]
    final = ''
    ind = 0
    while not final:
        r = candidates[ind]
        match = True
        for i in range(len(r)):
            if r[i] != w[i] and w[i] != '*':
                match = False
        if match:
            final += r
        ind += 1
    return final
