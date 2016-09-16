# -*- coding: utf-8 -*-

from __future__ import print_function, division
import re

import numpy as np
from sklearn.cluster import MiniBatchKMeans as mb

from normalise.expand_MONEY import end_dict, ecurr_dict


with open('data/NSW_list.txt', encoding='utf-8') as a_file:
    data = a_file.read()
    data = data.split(' ')


curr_list = ['£', '$', '€']
punct = ['.', '-', '/', ':', '*']
months = ["January", "Jan", "Jan.",
          "February", "Feb", "Feb.",
          "March", "Mar", "Mar.",
          "April", "Apr", "Apr.", "May",
          "June", "Jun", "Jun.",
          "July", "Jul", "Jul.",
          "August", "Aug", "Aug.",
          "September", "Sept", "Sept.",
          "October", "Oct", "Oct.",
          "November", "Nov", "Nov.",
          "December", "Dec", "Dec."]
money = ['million', 'millions', 'billion', 'billions', 'trillion', 'trillions']
roman = ['I', 'V', 'X', 'L', 'C', 'D', 'M']


def run_clf1(lst):
    clf = mb(n_clusters=4)
    clf.fit(gen_featuresets1(data))
    tag_dict = {
                int(predict1(clf, 'hello')): 'ALPHA',
                int(predict1(clf, '123')): 'NUMB',
                int(predict1(clf, 'WS99')): 'SPLT',
                int(predict1(clf, '-./%$**.')): 'MISC'
                }
    return [(w, tag_dict[int(predict1(clf, w))]) for w in lst]


def predict1(clf, samples):
    if type(samples) == str:
        return clf.predict(gen_featuresets1([samples]))
    else:
        return clf.predict(gen_featuresets1(samples))


def gen_featuresets1(samples):
    return np.array([give_features1(nsw) for nsw in samples], dtype=float)


def give_features1(nsw):
    return [
            only_alpha(nsw),
            is_url(nsw),
            punct_based(nsw),
            is_digbased(nsw),
            sing_punct(nsw),
            looks_splitty(nsw)
            ]


def is_digit(lt):
    return lt.isdigit()


def is_alpha(lt):
    return lt.isalpha()


def is_punct(lt):
    return lt in punct


def is_curr(lt):
    return lt in curr_list


def has_digit(w):
    if list(filter(is_digit, w)):
        return True
    else:
        return False


def has_alpha(w):
    if is_digbased(w):
        return False
    else:
        if list(filter(is_alpha, w)):
            return True
        else:
            return False

alpha_pattern = re.compile('''
([A-Za-z]+\'?)*         #(1 or more letter, optional apostrophe) repeated
$                       # end of string
    ''', re.VERBOSE)
def only_alpha(w):
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


def has_punct(w):
    if list(filter(is_punct, w)):
        return True
    else:
        return False


def has_curr(w):
    if list(filter(is_curr, w)):
        return True
    else:
        return False

acr_pattern = re.compile('''
([A-Za-z]\.)+           #letter followed by '.' 1 or more times
[A-Za-z]?               #optional final letter
$                       # end of string
''', re.VERBOSE)


def is_acr(w):
    return bool(acr_pattern.match(w))

urlstart_pattern = re.compile('''
(https?://)|            #'http' followed by optional 's', then '://' OR
(www\.)                 #'www.'
''', re.VERBOSE)

urlend_pattern = re.compile('''
.*                      #any number of characters
\.                      # '.'
((com)|                 # 'com' OR
(org(\.uk)?)|           # 'org' followed optionally by '.uk' OR
(co\.uk))               # 'co.uk'
$                       #end of string
''', re.VERBOSE)


def is_url(w):
    if urlstart_pattern.match(w) or urlend_pattern.match(w):
        return True
    else:
        return False


def has_lrep(w):
    for i in range(len(w)-2):
        if w[i] == w[i+1] and w[i] == w[i+2] and w[i].isalpha():
            return True
            break
    return False


def has_prep(w):
    for i in range(len(w)-2):
        if w[i] == w[i+1] and w[i] in punct:
            return True
            break
    return False


def is_time(w):
    if (has_digit(w) and
       (':' or '.') in w and
       (w.endswith('pm') or w.endswith('am'))):
            return True
    elif has_digit(w) and ':' in w and not has_alpha(w):
        return True
    elif has_digit(w) and (w.endswith('pm') or w.endswith('am')):
        return True
    else:
        return False


def is_year(w):
    if len(w) == 5 and w[:4].isdigit() and w.endswith('s'):
        return True
    elif len(w) == 2 and w[:1].isdigit() and w.endswith('s'):
        return True
    elif w.isdigit() and len(w) == 4:
        return True
    else:
        return False


def is_digbased(w):
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
                                           '-', '%', ':',
                                           "'",  '"', "°"]:
            return False
    else:
        return True and has_digit(w)


def sing_punct(w):
    if len(w) == 1 and not w.isalnum():
        return True
    else:
        return False

hyphen_pattern = re.compile('''
(([A-Za-z][\'\.]?)      #a letter followed optionally by '.' or "'"
+                       #repeated one or more times
(-|/|\s|(-&-))          #followed by '-', '/', or '-&-'
)+                      #all of the above repeated 1+ times
([A-Za-z][\.\']?)*      #optional final 'word' (same pattern as line 1)
$                       #end of string
    ''', re.VERBOSE)
mixedcase_pattern = re.compile('''
.*                      #any number of characters
([a-z][A-Z]|            #lowercase letter followed by uppercase OR
[A-Z][A-Z][a-z][a-z])   #two uppercase followed by two lowercase
.*
''', re.VERBOSE)
emph_pattern = re.compile('''
[\*~]+                          #'*' or '~' repeated one or more times
([A-Za-z]+[-/\']?)+[A-Za-z]+    #optionally hyphenated 'word'
[\*~]+                          #'*' or '~' repeated one or more times
$                               #end of string
''', re.VERBOSE)


def looks_splitty(w):
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


def punct_based(w):
    if has_prep(w):
        return True
    else:
        for lt in w:
            if lt.isalnum():
                return False
        return True
