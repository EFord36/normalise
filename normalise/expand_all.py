import re
import pickle

from normalise.class_ALPHA import triple_rep
from normalise.spellcheck import correct
from normalise.expand_EXPN import expand_EXPN
from normalise.expand_HTAG import expand_HTAG, expand_URL
from normalise.expand_NUMB import (expand_NUM, expand_NDIG, expand_NORD,
                                   expand_NYER, expand_PRCT, expand_MONEY,
                                   expand_NTIME, expand_NRANGE, expand_NTEL,
                                   expand_NDATE, expand_NSCI)

with open('../normalise/data/wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

func_dict = {
             'EXPN': 'expand_EXPN(nsw, ind, text)',
             'LSEQ': 'expand_LSEQ(nsw)',
             'WDLK': 'expand_WDLK(nsw)',
             'NUM': 'expand_NUM(nsw)',
             'NORD': 'expand_NORD((ind, (nsw, tag, ntag)), text)',
             'NRANGE': 'expand_NRANGE(nsw)',
             'NDIG': 'expand_NDIG(nsw)',
             'NTIME': 'expand_NTIME(nsw)',
             'NDATE': 'expand_NDATE(nsw)',
             'NADDR': 'expand_NYER(nsw)',
             'NTEL': 'expand_NTEL(nsw)',
             'NSCI': 'expand_NSCI(nsw)',
             'NYER': 'expand_NYER(nsw)',
             'MONEY': 'expand_MONEY((ind, (nsw, tag, ntag)), text)',
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


def expand_NONE(nsw):
    return ''


def expand_PROF(w):
    try:
        """Return 'original' rude word from asterisked FNSP."""
        rude = ['ass', 'asshole', 'balls', 'bitch', 'cunt', 'cock', 'crap',
                'cum', 'dick', 'fuck', 'pussy', 'shit', 'tits', 'twat']
        candidates = [r for r in rude if len(r) == len(w)]
        final = ''
        ind = 0
        if not candidates:
            return w
        else:
            while not final and ind < len(candidates):
                r = candidates[ind]
                match = True
                for i in range(len(r)):
                    if r[i] != w[i] and w[i] != '*':
                        match = False
                if match:
                    final += r
                ind += 1
            if final:
                return final
            else:
                return w
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        return w


def expand_WDLK(word):
    try:
        if word.lower() in wordlist:
            return word
        elif word[0].isupper() and word[1:].islower():
            return word
        elif triple_rep(word):
            return expand_FNSP(word)
        else:
            return correct(word)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        return word


def expand_FNSP(w):
    """Return 'original' word from FNSP."""
    try:
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
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        return w


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
    try:
        out = ''
        if word[0].isalpha():
            out += word[0].upper()
        for c in word[1:]:
            if c.isalpha():
                out += ' '
                out += c.upper()
        return out
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        return word
