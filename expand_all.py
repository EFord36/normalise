import re
import pickle

from class_ALPHA import triple_rep
from spellcheck import correct
from expand_EXPN import expand_EXPN
from expand_NUMB import (expand_NUM, expand_NDIG, expand_NORD, expand_NYER,
                         expand_PRCT, expand_MONEY, expand_NTIME,
                         expand_NRANGE)

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

func_dict = {
             'EXPN': 'expand_EXPN(nsw, ind, text)',
             'LSEQ': 'expand_LSEQ(nsw)',
             'WDLK': 'expand_WDLK(nsw)',
             'NUM': 'expand_NUM(nsw)',
             'NORD': 'expand_NORD(nsw)',
             'NRANGE': 'expand_NRANGE(nsw)',
             'NDIG': 'expand_NDIG(nsw)',
             'NTIME': 'expand_NTIME(nsw)',
             'NDATE': 'expand_NDATE(nsw)',
             'NYER': 'expand_NYER(nsw)',
             'MONEY': 'expand_MONEY(nsw)',
             'PRCT': 'expand_PRCT(nsw)',
             'PROF': 'expand_PROF(nsw)',
             'URL': 'expand_URL(nsw)',
             'HTAG': 'expand_HTAG(nsw)',
             'NONE': 'expand_NONE(nsw)'
             }


def expand_all(dic, text):
    out = {}
    for ind, (nsw, tag, ntag) in dic.items():
        out.update({ind: (nsw, tag, ntag, (eval(func_dict[ntag])))})
    return out


def expand_URL(word):
    return word


def expand_HTAG(word):
    return word


def expand_NDATE(word):
    return word


def expand_NONE(nsw):
    return ''


def expand_PROF(w):
    """Return 'original' rude word from asterisked FNSP."""
    rude = ['ass', 'asshole', 'balls', 'bitch', 'cunt', 'cock', 'crap', 'cum',
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


def expand_WDLK(word):
    if word in wordlist:
        return word
    elif triple_rep(word):
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


def expand_LSEQ(word):
    out = ''
    if word[0].isalpha():
        out += word[0].upper()
    for c in word[1:]:
        if c.isalpha():
            out += ' '
            out += c.upper()
    return out
