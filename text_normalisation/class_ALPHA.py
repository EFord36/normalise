# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 10:12:48 2016

@author: Elliot
"""
import re
import pickle

import numpy as np
from sklearn.semi_supervised import LabelPropagation as lp

from tag1 import tag1, is_digbased, acr_pattern
from class_NUMB import gen_frame
from splitter import split, retag1
from measurements import meas_dict, meas_dict_pl
from element_dict import element_dict

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

with open('NSW_dict.pickle', mode='rb') as file:
    NSWs = pickle.load(file)

with open('word_tokenized.pickle', mode='rb') as file:
    word_tokenized = pickle.load(file)

with open('word_tokenized_lowered.pickle', mode='rb') as file:
    word_tokenized_lowered = pickle.load(file)

with open('clf_ALPHA.pickle', mode='rb') as file:
    clf_ALPHA = pickle.load(file)

# Store all ALPHA tags from training data in ALPHA_list, including SPLT-ALPHA
tagged = tag1(NSWs)

ALPHA_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tagged.items()
              if tag == 'ALPHA'}

SPLT_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tagged.items()
             if tag == 'SPLT'}

splitted = split(SPLT_dict)
retagged = retag1(splitted)
retagged_ALPHA_dict = {ind: (nsw, tag) for ind, (nsw, tag) in retagged.items()
                       if tag == 'SPLT-ALPHA'}
ALPHA_dict.update(retagged_ALPHA_dict)

ampm = ['am', 'pm', 'AM', 'PM', 'a.m.', 'p.m.', 'A.M.', 'P.M.', 'pm.', 'am.']
adbc = ['AD', 'A.D.', 'ad', 'a.d.', 'BC', 'B.C.', 'bc', 'B.C.']

def run_clfALPHA(dic, text):
    """Train classifier on training data, return dictionary with added tag.

    dic: dictionary entry where key is index of word in orig text, value
         is a tuple with the nsw and the tag (ALPHA, NUMB, SPLT-, MISC).
    The dictionary returned has the same entries with the tuple extended with
    a more specific number tag assigned to it by the classifier.
    """

    clf = clf_ALPHA
    int_tag_dict = {
                    1: 'EXPN',
                    2: 'LSEQ',
                    3: 'WDLK',
                    }
    out = {}
    for (ind, (nsw, tag)) in dic.items():
        pred_int = int(clf.predict(gen_featuresetsALPHA({ind: (nsw, tag)}, text)))
        ntag = int_tag_dict[pred_int]
        out.update({ind: (nsw, tag, ntag)})
    return out


def gen_featuresetsALPHA(tagged_dict, text):
    """Return an array for features for each item in the input dict."""
    return np.array([give_featuresALPHA(item, text)
                    for item in tagged_dict.items()],
                    dtype=float)


def give_featuresALPHA(item, text):
    """Return a list of features for a dictionary item."""
    ind, nsw, tag = item[0], item[1][0], item[1][1]
    context = gen_frame(item, text)
    out = [

           ]
    out.extend(seed_features(item, context))
    """out.extend(in_features(nsw))"""
    return out


def seed_features(item, context):
    """Return a list of features equivalent to those used in the seedset."""
    ind, nsw, tag = item[0], item[1][0], item[1][1]
    out = [
           nsw in ['Mr.', 'Mrs.', 'Mr', 'Mrs'],
           nsw in ['i.e.', 'ie.', 'e.g.', 'eg.'],
           nsw.endswith('.') and nsw.istitle() and not acr_pattern.match(nsw),
           (nsw.isupper() and is_cons(nsw) and not (nsw in meas_dict and
           is_digbased(context[1])) and not acr_pattern.match(nsw)),
           (nsw in meas_dict or nsw in meas_dict_pl) and is_digbased(context[1]),
           (nsw in ampm or nsw in adbc) and is_digbased(context[1]),
           (nsw.istitle() and nsw.isalpha() and len(nsw) > 3 and not is_cons(nsw)),
           (not (nsw.isupper() or nsw.endswith('s') and nsw[:-1].isupper()) and
           (nsw.lower() in wordlist or
           (nsw[:-1].lower() in wordlist and nsw.endswith('s')))
           and nsw not in ampm),
           triple_rep(nsw) and len(nsw) > 3,
           bool(acr_pattern.match(nsw) and nsw not in meas_dict),
           nsw.islower() and len(nsw) > 3,
           nsw.endswith('s') and nsw[:-1].isupper(),
           nsw in element_dict
           ]
    return out


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
        featset.append(give_featuresALPHA((ind, (nsw, tag)), text))
    return (np.array(featset, dtype=int), np.array(seedset))


def fit_clf(dic, text):
    """Fit a Label Propogation classifier to the input dictionary."""
    model = lp(tol=0.01)
    X, y = gen_feats_and_seed(dic, text)
    model.fit(X, y)
    return model


def fit_and_store_clf(dic, text):
    """fit a Label Propogation classifier, and store in clf_ALPHA.pickle"""
    clf = fit_clf(dic, text)
    with open('clf_ALPHA.pickle', 'wb') as file:
        pickle.dump(clf, file)


def seed(dict_tup, text):
    """Assign a seedset label to the input tuple.

    Generate seeds for the seedset by assigning integer labels to obvious
    cases. Where there is no obvious case, '-1' is returned.
    """
    ind, nsw, tag = dict_tup[0], dict_tup[1][0], dict_tup[1][1]
    context = gen_frame((ind, (nsw, tag)), text)
    if nsw in ['Mr.', 'Mrs.', 'Mr', 'Mrs']:
        return 3
    elif nsw in ['i.e.', 'ie.', 'e.g.', 'eg.']:
        return 2
    elif nsw.endswith('.') and nsw.istitle() and not acr_pattern.match(nsw):
        return 1
    elif (nsw.isupper() and is_cons(nsw) and not (nsw in meas_dict and
         is_digbased(context[1]))):
             return 2
    elif nsw.endswith('s') and nsw[:-1].isupper():
        return 2
    elif (nsw in meas_dict or nsw in meas_dict_pl) and is_digbased(context[1]):
        return 1
    elif (nsw in ampm or nsw in adbc) and is_digbased(context[1]):
        return 2
    elif nsw.istitle() and nsw.isalpha() and len(nsw) > 3 and not is_cons(nsw):
        return 3
    elif nsw in element_dict:
        return 1
    elif (not (nsw.isupper() or nsw.endswith('s') and nsw[:-1].isupper()) and
         (nsw.lower() in wordlist or
         (nsw[:-1].lower() in wordlist and nsw.endswith('s')))
         and nsw not in ampm):
             return 3
    elif triple_rep(nsw) and len(nsw) > 3:
        return 3
    elif nsw.islower() and len(nsw) > 3:
        return 3
    elif acr_pattern.match(nsw) and not nsw in meas_dict:
        return 2
    elif len(nsw) == 1:
        return 2
    else:
        return -1


def is_cons(w):
    """Return True if no vowels in w."""
    for lt in w:
        if lt in ['A', 'E', 'I', 'O', 'U', 'a', 'e', 'i', 'o', 'u']:
            return False
    return True


def triple_rep(w):
    """Return 'True' if w has a letter repeated 3 times consecutively."""
    for i in range(len(w)-2):
        if w[i] == w[i+1] and w[i] == w[i+2] and w[i].isalpha():
            return True
    return False

ALPHAs_context = []
for item in ALPHA_dict.items():
    if item[0] < 1206200:
        for word in gen_frame(item, word_tokenized):
            ALPHAs_context.append(' {} '.format(word))

third_ALPHA_dict = {}
count = 0
for item in ALPHA_dict.items():
    count += 1
    if count % 3 == 0:
        third_ALPHA_dict.update((item,))
