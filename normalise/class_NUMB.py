# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 09:14:19 2016

@author: Elliot
"""
import re
import pickle

import numpy as np
from sklearn.semi_supervised import LabelPropagation as lp

from normalise.tag1 import tag1
from normalise.expand_NUMB import ecurr_dict
from normalise.timezones import timezone_dict
from normalise.splitter import split, retag1
from normalise.measurements import meas_dict, meas_dict_pl

with open('data/NSW_dict.pickle', mode='rb') as file:
    NSWs = pickle.load(file)

with open('data/word_tokenized.pickle', mode='rb') as file:
    word_tokenized = pickle.load(file)

with open('data/word_tokenized_lowered.pickle', mode='rb') as file:
    word_tokenized_lowered = pickle.load(file)

with open('data/wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

with open('data/clf_NUMB.pickle', mode='rb') as file:
    clf_NUMB = pickle.load(file)

# Store all NUMB tags from training data in NUMB_list, including SPLT-NUMB.
tagged = tag1(NSWs)

NUMB_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tagged.items()
             if tag == 'NUMB'}

SPLT_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tagged.items()
             if tag == 'SPLT'}

splitted = split(SPLT_dict)
retagged = retag1(splitted)
retagged_NUMB_dict = {ind: (nsw, tag) for ind, (nsw, tag) in retagged.items()
                      if tag == 'SPLT-NUMB'}
NUMB_dict.update(retagged_NUMB_dict)

curr_list = ['£', '$', '€', 'Y']
ampm = ['am', 'pm', 'AM', 'PM', 'a.m.', 'p.m.', 'A.M.', 'P.M.', 'pm.', 'am.']
months = ["January", "Jan", "Jan.", "February", "Feb", "Feb.",
          "March", "Mar", "Mar.", "April", "Apr", "Apr.", "May",
          "June", "Jun", "Jun.", "July", "Jul", "Jul.", "August",
          "Aug", "Aug.", "September", "Sept", "Sept.", "October",
          "Oct", "Oct.", "November", "Nov", "Nov.", "December",
          "Dec", "Dec."]
addr_words = ['Road', 'Rd.', 'Street', 'Avenue', 'Ave.']


def run_clfNUMB(dic, text):
    """Train classifier on training data, return dictionary with added tag.

    dic: dictionary entry where key is index of word in orig text, value
         is a tuple with the nsw and the tag (ALPHA, NUMB, SPLT-, MISC).
    The dictionary returned has the same entries with the tuple extended with
    a more specific number tag assigned to it by the classifier.
    """
    clf = clf_NUMB
    int_tag_dict = {
                    1: 'PRCT',
                    2: 'MONEY',
                    3: 'NTIME',
                    4: 'NYER',
                    5: 'NDIG',
                    6: 'NORD',
                    7: 'NUM',
                    8: 'NRANGE',
                    9: 'NTEL',
                    10: 'NDATE',
                    11: 'NADDR'
                    }
    out = {}
    for (ind, (nsw, tag)) in dic.items():
        pred_int = int(clf.predict(gen_featuresetsNUM({ind: (nsw, tag)}, text)))
        ntag = int_tag_dict[pred_int]
        out.update({ind: (nsw, tag, ntag)})
    return out


def gen_featuresetsNUM(tagged_dict, text):
    """Return an array for features for each item in the input dict."""
    return np.array([give_featuresNUM(item, text)
                    for item in tagged_dict.items()],
                    dtype=float)


def give_featuresNUM(item, text):
    """Return a list of features for a dictionary item."""
    ind, nsw, tag = item[0], item[1][0], item[1][1]
    context = gen_frame(item, text)
    out = [
           adj_month(context),
           year_size(nsw) or year_context(context),
           context[1] == 'in',
           range_vs_date_slash(nsw),
           range_vs_date_hyph(nsw),
           date_vs_num(nsw),
           time_context(nsw, context),
           looks_rangey(nsw),
           nsw.isdigit() and 'SPLT' not in tag,
           nsw.isdigit() and 'SPLT' in tag,
           context[1] in ['around', 'about', 'approximately'],
           context[1] in ['over', 'under'],
           context[1] == 'on',
           context[1] == 'at',
           context[1] == 'in',
           context[1] == 'of'
           ]
    out.extend(seed_features(item, context))
    out.extend(in_features(nsw))
    return out


def adj_month(context):
    """Return 'True' if word is adjacent to nsw."""
    if context[3] in months or context[1] in months:
        return True
    else:
        return False


def looks_rangey(nsw):
    """Return True if number fits range pattern, not date."""
    m = range_pattern.match(nsw)
    n = seed_range_pattern.match(nsw)
    if (m or n) and not range_vs_date_hyph(nsw):
        return True
    else:
        return False


def year_size(nsw):
    """Return '1' if nsw is greater than 1800."""
    if not nsw.isdigit():
        return False
    elif 1800 < int(nsw) < 2050:
        return 1
    else:
        return 0


def year_context(context):
    adbc = ['AD', 'A.D.', 'ad', 'a.d.', 'BC', 'B.C.', 'bc', 'B.C.']
    """Return 'True' if nsw is followed by variant on 'ad' or 'bc'."""
    if context[3] in adbc or context[1] in adbc:
        return True
    else:
        return False


def range_vs_date_slash(nsw):
    """Return 'True'1' if nsw looks like a date with a slash in."""
    if '/' not in nsw:
        return False
    elif nsw.count('/') == 2:
        return 1
    elif nsw[0] == '0':
        return 1
    else:
        slash = nsw.find('/')
        first = nsw[:slash]
        second = nsw[slash:]
        if not (first.isdigit() and second.isdigit()):
            return False
        elif len(first) != len(second):
            return 0
        elif (int(first) > 12 and int(second) > 12 or
              int(first) > 31 or int(second) > 31):
            return 0
        elif len(first) == 1:
            return False
        elif int(second) > int(first[-len(second):]):
            return 0
        else:
            return 1


def range_vs_date_hyph(nsw):
    """Return 'True'1' if nsw looks like a date with a hyphen in."""
    if '-' not in nsw:
        return False
    elif nsw.count('-') == 2:
        return 1
    elif nsw[0] == '0':
        return 1
    else:
        hyph = nsw.find('-')
        first = nsw[:hyph]
        second = nsw[hyph:]
        if not (first.isdigit() and second.isdigit()):
            return False
        elif len(first) != len(second):
            return 0
        elif (int(first) > 12 and int(second) > 12 or
              int(first) > 31 or int(second) > 31):
            return 0
        elif len(first) == 1:
            return False
        elif int(second) > int(first[-len(second):]):
            return 0
        else:
            return 1


def date_vs_num(nsw):
    """Return '1' if nsw looks like a date with a '.' in."""
    if '.' not in nsw:
        return False
    elif nsw.count('.') > 1:
        return 1
    else:
        dot = nsw.find('.')
        first = nsw[:dot]
        second = nsw[dot:]
        if not (first.isdigit() and second.isdigit()):
            return False
        elif not (first.isdigit() and second.isdigit()):
            return False
        elif len(first) > 1 and first[0] == '0':
            return 1
        elif second[-1] == '0':
            return 1
        else:
            return 0


def time_context(nsw, context):
    """Return 'True' if followed by some variant of 'am' or 'pm'."""
    if '.' in nsw or ':' in nsw:
        if context[3] in ampm:
            return True
        else:
            return False
    else:
        return False

def looks_datey(nsw, context):
    m = date_pattern.match(nsw)
    if date_pattern.match(nsw):
        if (int(m.group(1)) <= 12 and 12 < int(m.group(3)) < 32 or
            12 < int(m.group(1)) < 32 and int(m.group(3)) <= 12):
                return True
        elif context[1] == 'on':
            return True
        else:
            return False
    else:
        return False


def in_features(nsw):
    """Return list of bools if specific punctuation is in nsw."""
    out = []
    for c in [':']:
        out.append(c in nsw)
    return out


def seed_features(item, context):
    """Return a list of features equivalent to those used in the seedset."""
    ind, nsw, tag = item[0], item[1][0], item[1][1]
    out = [
           nsw.endswith('%'),
           (nsw[0] in curr_list or nsw[-3:] in ecurr_dict or
            nsw[:3] in ecurr_dict),
           ('.' in nsw and
            (context[3] in timezone_dict or
             context[3] in ampm) or
            bool(time_pattern.match(nsw))),
           ((context[1] == 'in' and len(nsw) == 4 and nsw.isdigit()) or
            (nsw.endswith('s') and len(nsw) == 5 and
            nsw[:2] in ['19', '20']) or
            context[1] in months and len(nsw) == 4 and nsw.isdigit()),
           (nsw.isdigit() and context[1].isalpha() and context[1].isupper() and
          len(context[1]) > 1 and context[1].lower() not in wordlist and
          len(nsw) > 1) or nsw.count('.') > 2,
           (nsw[-2:] in ['st', 'nd', 'rd', 'th'] or
            ((context[1] in months or context[3] in months) and
            nsw.isdigit() and
            int(nsw) < 31)),
           ((float_pattern.match(nsw) and float(nsw) > 31) or
          ((context[3] in ['million', 'billion', 'thousand'] or
          (context[3] in meas_dict or context[3] in meas_dict_pl) and
          nsw.isdigit()))),
          looks_datey(nsw, context),
          (len(nsw) == 11 and nsw.startswith('0')) or nsw.startswith('+44'),
          looks_rangey(nsw),
          (nsw.isdigit() and 1950 < int(nsw) < 2100
            and not (context[3] in meas_dict or context[3] in meas_dict_pl)),
          len(nsw) < 5 and context[4] in addr_words,
           ]
    return out


def create_NUMB_ex():
    """Create text file 'NUMB_examples.txt' containing NUMB nsws in context"""
    NUMB_ex = []
    for ind, (word, tag) in NUMB_dict.items():
        NUMB_ex.append(gen_frame((ind, (word, tag)), text))
    with open('NUMB_examples.txt', mode='w', encoding='utf-8') as file:
        file.write(str(NUMB_ex))


def gen_frame(dict_tup, text):
    """Return tuple containing nsw and two words either side in orig text.

    If nsw has been split, count previous parts of original 'word' as part
    of the left-context.
    If a context word is '.' and the following word is capitalised,
    replace following words in that half of the context with <END>.
    """
    ind, word, tag = dict_tup[0], dict_tup[1][0], dict_tup[1][1]
    tup = ()
    end = 0
    if isinstance(ind, int):
        for i in range(ind - 2, ind + 3):
            if i < 0:
                tup += ('<END>',)
            elif i + 2 > len(text):
                tup += (text[i],)
                rem = 5 - len(tup)
                tup += rem * ('<END>',)
                break
            elif (text[i] == '.' and
                    text[i + 1].istitle()):
                if len(tup) > 2:
                    end = 1
                    tup += ('<END>',)
                elif len(tup) == 0:
                    tup = ('<END>',)
                else:
                    leng = len(tup)
                    tup = leng * ('<END>',)
            elif end:
                tup += ('<END>',)
            else:
                tup += (text[i],)
    else:
        rind = round(ind)
        full = text[rind]
        start = ''
        end = ''
        index = full.find(word)
        start = full[:index]
        end = full[index + len(word):]
        potential_context = gen_frame((rind, (word, tag)), text)
        if start and end:
            tup = (potential_context[1],
                   start, word, end, potential_context[-2])
        elif start:
            tup = (potential_context[1],
                   start, word,
                   potential_context[-2], potential_context[-1])
        elif end:
            tup = (potential_context[0],
                   potential_context[1], word,
                   end, potential_context[-2])
        else:
            tup = (potential_context[0],
                   potential_context[1], word,
                   potential_context[-2],
                   potential_context[-1])
    return tup


def gen_seed(dic, text):
    """Return a list of the (integer) labels assigned to the seedset."""
    seedset = []
    for ind, (nsw, tag) in dic.items():
        seedset.append(seed((ind, (nsw, tag)), text))
    return seedset


def gen_feats_and_seed(dic, text):
    """Return a tuple of arrays - the first of features, the second, labels."""
    seedset = []
    featset = []
    for ind, (nsw, tag) in dic.items():
        seedset.append(seed((ind, (nsw, tag)), text))
        featset.append(give_featuresNUM((ind, (nsw, tag)), text))
    return (np.array(featset, dtype=int), np.array(seedset))


def fit_clf(dic, text):
    """Fit a Label Propogation classifier to the input dictionary."""
    model = lp()
    X, y = gen_feats_and_seed(dic, text)
    model.fit(X, y)
    return model


def fit_and_store_clf(dic, text):
    """fit a Label Propogation classifier, and store in clf_NUMB.pickle"""
    clf = fit_clf(dic, text)
    with open('data/clf_NUMB.pickle', 'wb') as file:
        pickle.dump(clf, file)


def seed(dict_tup, text):
    """Assign a seedset label to the input tuple.

    Generate seeds for the seedset by assigning integer labels to obvious
    cases. Where there is no obvious case, '-1' is returned.
    """
    ind, nsw, tag = dict_tup[0], dict_tup[1][0], dict_tup[1][1]
    context = gen_frame((ind, (nsw, tag)), text)
    if nsw.endswith('%'):
        return 1
    elif (nsw[0] in curr_list or nsw[-3:] in ecurr_dict or
            nsw[:3] in ecurr_dict):
        return 2
    elif ('.' in nsw and
          (context[3] in timezone_dict or
           context[3] in ampm) or
          time_pattern.match(nsw)):
                return 3
    elif ((context[1] == 'in' and len(nsw) == 4 and nsw.isdigit()) or
          (nsw.endswith('s') and len(nsw) == 5 and nsw[:2] in ['19', '20']) or
          context[1] in months and len(nsw) == 4 and nsw.isdigit()):
                return 4
    elif (nsw.isdigit() and context[1].isalpha() and context[1].isupper() and
          len(context[1]) > 1 and context[1].lower() not in wordlist and
          len(nsw) > 1) or nsw.count('.') > 2:
        return 5
    elif (nsw[-2:] in ['st', 'nd', 'rd', 'th'] or
          ((context[1] in months or context[3] in months) and
          nsw.isdigit() and
          int(nsw) <= 31)):
            return 6
    elif ((float_pattern.match(nsw) and float(nsw) > 31) or
          ((context[3] in ['million', 'billion', 'thousand']) or
          (context[3] in meas_dict or context[3] in meas_dict_pl) and
          nsw.isdigit())):
        return 7
    elif looks_datey(nsw, context):
        return 10
    elif looks_rangey(nsw):
        return 8
    elif (len(nsw) == 11 and nsw.startswith('0')) or nsw.startswith('+44'):
        return 9
    elif '.' in nsw or ',' in nsw:
        return 7
    elif (nsw.isdigit() and 1950 < int(nsw) < 2100
            and not (context[3] in meas_dict or context[3] in meas_dict_pl)):
        return 4
    elif len(nsw) < 5 and context[4] in addr_words:
        return 11
    else:
        return - 1

time_pattern = re.compile('''
([0-9]{1,2})            # one or two numbers
\:                      # ':'
([0-9]{2})              # two numbers
$
''', re.VERBOSE)

float_pattern = re.compile('''
[0-9]+                  # any number of digits
\.                      # '.'
[0-9]+                  # any number of digits
$                       # end
''', re.VERBOSE)

seed_range_pattern = re.compile('''
(([0-9]{4}              # (4 digits
-                       # a hyphen
[0-9]{2}                # 2 digits
$)                      # end)
|                       # OR
([0-9]{4}               # (4 digits
/                       # a slash
[0-9]{,2}               # 1 or 2 digits
$))                     # end)
''', re.VERBOSE)

range_pattern = re.compile('''
([0-9]+                 # 1 or more digits
\.?                     # optional '.'
[0-9]*)                 # 0 or more digits
(/|-|–)                   # hyphen or slash
([0-9]+                 # same pattern as lines 1-3
\.?
[0-9]*)
$
''', re.VERBOSE)

date_pattern = re.compile('''
([0-9]{1,2})
(/)
([0-9]{1,2})
(/)?
([0-9]{2,4})?
$
''', re.VERBOSE)
