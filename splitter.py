# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 10:54:54 2016

@author: Elliot
"""

from __future__ import division, print_function, unicode_literals

import re
import pickle

from tag1 import tag1, NSWs, is_digbased, only_alpha

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

SPLT_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tag1(NSWs).items()
             if tag == 'SPLT'}





def tag_SPLT(lst):
    """ Assign new index and tag 'SPLT-' to every part of a split token."""
    if len(lst) > 9:
        inc = round((1 / (len(lst))), 2)
    else:
        inc = 0.1
    ind = lst[0]
    out = {}
    for i in range(1, len(lst)):
        out.update({ind+inc*i: (lst[i], 'SPLT-')})
    return out


def split(dic):
    """ Form dictionary of SPLT tokens."""
    split_dict = {}
    for ind, (nsw, tag) in dic.items():
        out = [ind]
        emph_list = []
        emph_match = emph_pattern.match(nsw)
        if emph_match:
            emph_list += emph_match.groups()
        else:
            emph_list += [nsw]
        hyph_list = []
        for nsw in emph_list:
            hyph_list.extend(nsw.split('-'))
        mixedalnum_list = []
        for nsw in hyph_list:
            mixedalnum_list.extend(mixedalnum_split(nsw))
        updown_list = []
        for nsw in mixedalnum_list:
            updown_list.extend(split_updown(nsw))
        mixedcase_list = []
        for nsw in updown_list:
            mixedcase_list.extend(mixedcase_split(nsw))
        out.extend(mixedcase_list)
        split_dict.update(tag_SPLT(out))
    return split_dict


def retag1(dic):
    """ Retag each part of a SPLT token as 'SPLT-ALPHA', 'SPLT-NUMB' or
    'SPLT-MISC'.
    """
    out = {}
    for ind, (it, tag) in dic.items():
        if len(it) > 100:
            out.update({ind: (it, tag + 'MISC')})
        if is_digbased(it):
            out.update({ind: (it, tag + 'NUMB')})
        elif (only_alpha(it) and
              (not mixedcase_pattern.match(it) or
               len(it) <= 3 or (it[-1] == 's' and not
               mixedcase_pattern.match(it[:-1])))):
                    out.update({ind: (it, tag + 'ALPHA')})
        else:
            out.update({ind: (it, tag + 'MISC')})
    return out


def split_updown(nsw):
    """ For tokens matching updown_pattern; split before or after penultimate
    upper-case character depending on whether resulting word is in wordlist.
    If neither group in wordlist, split before penultimate upper-case letter
    as default.
    """
    m = updown_pattern.match(nsw)
    if m:
        if (m.group(2) + m.group(3)).lower() in wordlist:
            return [m.group(1), m.group(2) + m.group(3)]
        elif m.group(3) in wordlist:
            return [m.group(1) + m.group(2), m.group(3)]
        else:
            return [m.group(1), m.group(2) + m.group(3)]
    else:
        return [nsw]


def mixedalnum_split(nsw):
    """ Split tokens on transitions from letters to numbers or numbers to
    letters.
    """
    if nsw.isalnum():
        out = []
        ind = 0
        if nsw[0] in digits:
            cat = 'num'
        else:
            cat = 'let'
        for i in range(1, len(nsw)):
            if nsw[i] in digits:
                if cat == 'num':
                    pass
                else:
                    out.append(nsw[ind:i])
                    cat = 'num'
                    ind = i
            else:
                if cat == 'let':
                    pass
                else:
                    out.append(nsw[ind:i])
                    cat = 'let'
                    ind = i
        out.append(nsw[ind:])
        return out
    else:
        return [nsw]


def mixedcase_split(nsw):
    """ Split tokens on transitions from upper- to lower- or lower- to
    upper-case.
    """
    if nsw.isalpha():
        if nsw.istitle():
            return [nsw]
        else:
            out = []
            ind = 0
            if nsw[0].isupper():
                cat = 'up'
            else:
                cat = 'low'
            for i in range(1, len(nsw)):
                if nsw[i].isupper():
                    if cat == 'up':
                        pass
                    else:
                        out.append(nsw[ind:i])
                        cat = 'up'
                        ind = i
                else:
                    if cat == 'low':
                        pass
                    else:
                        out.append(nsw[ind:i])
                        cat = 'low'
                        ind = i
            out.append(nsw[ind:])
            return out
    else:
        return [nsw]


hyphen_pattern = re.compile('''
(([\'\.]?                       # optional "'" or "."
[A-Za-z]                        # letter
[\'\.]?)                        # optional "'" or "."
+                               # lines 1-3 repeated one or more times
(-|/|\s|(-&-))                  # followed by '-', '/', or '-&-'
)+                              # all of the above repeated 1+ times
([\'\.]?[A-Za-z][\.\']?)*       # optional final 'word' (same as lines 1-3)
$                               # end of string
''', re.VERBOSE)

mixedcase_pattern = re.compile('''
([A-Z]{2,}[a-z]) |    # 2 or more capitals, a lowercase OR
(.*[a-z][A-Z])        # any number of chars, a lowercase, an uppercase
''', re.VERBOSE)

emph_pattern = re.compile('''
([\*~<:]+)                      # '*' or '~' repeated one or more times
((?:[A-Za-z]+[-/\']?)+[A-Za-z]+)# optionally hyphenated 'word'
([\*~>:]+)                      # '*' or '~' repeated one or more times
$                               # end of string
''', re.VERBOSE)

updown_pattern = re.compile('''
([A-Z]+?)                       # 1 or more capitals (non-greedy) (capturing)
([A-Z])                         # a capital (capturing)
([a-z]+)                        # 1 or more lowercase (capturing)
$
''', re.VERBOSE)
