# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:44:25 2016

@author: Elliot
"""
from __future__ import division, print_function, unicode_literals

import re
import pickle

from normalise.expand_NUMB import end_dict, ecurr_dict

with open('data/NSW_dict.pickle', mode='rb') as file:
    NSWs = pickle.load(file)

curr_list = ['£', '$', '€']
AlPHA_dict, NUMB_dict, MISC_dict = {}, {}, {}


def tag1(dic):
    """Return dictionary with added tag.

    dic: dictionary entry where key is index of word in orig text, value
         is the nsw
    The dictionary returned has the same keys with the values being a tuple
    with nsw and its assigned tag.
    """
    out = {}
    for ind, it in dic.items():
        if len(it) > 100:
            out.update({ind: (it, 'MISC')})
        if is_digbased(it):
            out.update({ind: (it, 'NUMB')})
        elif (only_alpha(it) and
              (not mixedcase_pattern.match(it) or
               len(it) <= 3 or (it[-1] == 's' and not
               mixedcase_pattern.match(it[:-1])))):
                    out.update({ind: (it, 'ALPHA')})
        elif is_url(it) or hashtag_pattern.match(it):
            out.update({ind: (it, 'MISC')})
        elif looks_splitty(it):
            out.update({ind: (it, 'SPLT')})
        else:
            out.update({ind: (it, 'MISC')})
    return out


def looks_splitty(w):
    """Return 'True' if w looks like it should be split."""
    if has_digit(w) and has_alpha(w):
        return True
    elif hyphen_pattern.match(w):
        return True
    elif (only_alpha(w) and not w[:2] == 'Mc'and not w[:3] == 'Mac' and
          mixedcase_pattern.match(w)):
        return True
    elif emph_pattern.match(w):
        return True
    else:
        return False


def is_digbased(w):
    """Return 'True' if w is based around digits."""
    if len(w) == 0:
        return False
    if w[-2:] in ["'s", "s'"]:
        return is_digbased(w[:-2])
    elif w[-3:] in ecurr_dict:
        return is_digbased(w[:-3])
    elif w[-2:] in ['st', 'nd', 'rd', 'th']:
        return is_digbased(w[:-2])
    elif w[-1].lower() in end_dict or w[-1] == 's':
        return is_digbased(w[:-1])
    elif w[0] in curr_list:
        return is_digbased(w[1:])
    elif w[0] == "'" and w[1:].isdigit():
        return True
    for lt in w:
        if not lt.isdigit() and lt not in ['/', '.', ',',
                                           '-', '–', '%',
                                           ':', "'", '"',
                                           "°", "—", "′"]:
            return False
    else:
        return True and has_digit(w)


def only_alpha(w):
    """Return 'True' if w is based on alphabetic characters."""
    if len(w) == 0:
        return False
    if w[-2:] in ["'s", "s'"]:
        return only_alpha(w[:-2])
    if is_acr(w):
        return True
    if w[-1] == '.':
        return only_alpha(w[:-1])
    if w[0] == "'":
        return only_alpha(w[1:])
    if w[-1] == "'":
        return only_alpha(w[:-1])
    if w[0] == '"' and w[-1] == '"':
        return only_alpha(w[1:-1])
    return (has_alpha(w) and bool(alpha_pattern.match(w)))


def is_digit(lt):
    """Return 'True' if input letter is a digit."""
    return lt.isdigit()


def is_alpha(lt):
    """Return 'True' if input letter is a letter."""
    return lt.isalpha()


def has_digit(w):
    """Return 'True' if w contains a digit."""
    if list(filter(is_digit, w)):
        return True
    else:
        return False


def has_alpha(w):
    """Return 'True' if w contains a letter."""
    if is_digbased(w):
        return False
    else:
        if list(filter(is_alpha, w)):
            return True
        else:
            return False


def is_acr(w):
    """Return 'True' if w is an acronym (alternates letters and '.')."""
    return bool(acr_pattern.match(w))


def is_url(w):
    """Return 'True' if start or end of w looks like a url."""
    if urlstart_pattern.match(w) or urlend_pattern.match(w):
        return True
    else:
        return False

hyphen_pattern = re.compile('''
(([\'\.]?                       # optional "'" or "."
[A-Za-z]                        # letter
[\'\.]?)                        # optional "'" or "."
+                               # lines 1-3 repeated one or more times
(-|–|—|/|\s|(-&-))              # followed by '-', '–', '—', '/', or '-&-'
)+                              # all of the above repeated 1+ times
([\'\.]?[A-Za-z][\.\']?)*       # optional final 'word' (same as lines 1-3)
$                               # end of string
    ''', re.VERBOSE)

mixedcase_pattern = re.compile('''
([A-Z]{2,}[a-z]) |    # 2 or more capitals, a lowercase OR
(.*[a-z][A-Z])        # any number of chars, a lowercase, an uppercase
''', re.VERBOSE)

emph_pattern = re.compile('''
[\*~<:]+                          # '*' or '~' repeated one or more times
([A-Za-z]+[-/\']?)+[A-Za-z]+    # optionally hyphenated 'word'
[\*~>:]+                          # '*' or '~' repeated one or more times
$                               # end of string
''', re.VERBOSE)

acr_pattern = re.compile('''
([A-Za-z]\.)+           # letter followed by '.' 1 or more times
[A-Za-z]?               # optional final letter
$                       # end of string
''', re.VERBOSE)

alpha_pattern = re.compile('''
([A-Za-z]+\'?)*         # (1 or more letter, optional apostrophe) repeated
$                       # end of string
''', re.VERBOSE)

urlstart_pattern = re.compile('''
(https?://)|            #'http' followed by optional 's', then '://' OR
(www\.)                 #'www.'
''', re.VERBOSE | re.IGNORECASE)

urlend_pattern = re.compile('''
.*                      #any number of characters
\.                      # '.'
((com)|                 # 'com' OR
(org(\.uk)?)|           # 'org' followed optionally by '.uk' OR
(co\.uk))               # 'co.uk'
$                       #end of string
''', re.VERBOSE | re.IGNORECASE)

hashtag_pattern = re.compile('''
\#
[A-Za-z0-9]+
[_-]?
[A-Za-z0-9]*
''', re.VERBOSE)

print('tag1 imported')
