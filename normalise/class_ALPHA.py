import sys
import re
import pickle

import numpy as np
from sklearn.semi_supervised import LabelPropagation as lp
from roman import romanNumeralPattern

from normalise.detect import mod_path
from normalise.tagger import tagify, is_digbased, acr_pattern
from normalise.class_NUMB import gen_frame
from normalise.splitter import split, retagify
from normalise.data.measurements import meas_dict, meas_dict_pl
from normalise.data.abbrev_dict import abbrev_dict
from normalise.data.element_dict import element_dict

with open('{}/data/wordlist.pickle'.format(mod_path), mode='rb') as file:
    wordlist = pickle.load(file)

with open('{}/data/NSW_dict.pickle'.format(mod_path), mode='rb') as file:
    NSWs = pickle.load(file)

with open('{}/data/word_tokenized.pickle'.format(mod_path), mode='rb') as file:
    word_tokenized = pickle.load(file)

with open('{}/data/word_tokenized_lowered.pickle'.format(mod_path), mode='rb') as f:
    word_tokenized_lowered = pickle.load(f)

with open('{}/data/clf_ALPHA.pickle'.format(mod_path), mode='rb') as file:
    clf_ALPHA = pickle.load(file)

with open('{}/data/names.pickle'.format(mod_path), mode='rb') as file:
    names_lower = pickle.load(file)

if __name__ == "__main__":
    tagged = tagify(NSWs, verbose=False)

    ALPHA_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tagged.items()
                  if tag == 'ALPHA'}

    SPLT_dict = {ind: (nsw, tag) for ind, (nsw, tag) in tagged.items()
                 if tag == 'SPLT'}

    splitted = split(SPLT_dict, verbose=False)
    retagged = retagify(splitted, verbose=False)
    retagged_ALPHA_dict = {ind: (nsw, tag)
                           for ind, (nsw, tag) in retagged.items()
                           if tag == 'SPLT-ALPHA'}
    ALPHA_dict.update(retagged_ALPHA_dict)

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

ampm = ['am', 'pm', 'AM', 'PM', 'a.m.', 'p.m.', 'A.M.', 'P.M.', 'pm.', 'am.']
adbc = ['AD', 'A.D.', 'ad', 'a.d.', 'BC', 'B.C.', 'bc', 'B.C.']


def run_clfALPHA(dic, text, verbose=True, user_abbrevs={}):
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
        if verbose:
            sys.stdout.write("\r{} of {} classified".format(len(out), len(dic)))
            sys.stdout.flush()
        if romanNumeralPattern.match(nsw) and gen_frame((ind, (nsw, tag)), text)[1].lower() in names_lower:
            out.update({ind: (nsw, 'NUMB', 'NORD')})
        if nsw in user_abbrevs:
            out.update({ind: (nsw, 'ALPHA', 'EXPN')})
        else:
            pred_int = int(clf.predict(gen_featuresetsALPHA({ind: (nsw, tag)}, text)))
            ntag = int_tag_dict[pred_int]
            out.update({ind: (nsw, tag, ntag)})
    if verbose:
        sys.stdout.write("\r{} of {} classified".format(len(out), len(dic)))
        sys.stdout.flush()
        print("\n")
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
           (nsw.isupper() and is_cons(nsw) and not (nsw in meas_dict
            and is_digbased(context[1])) and not acr_pattern.match(nsw)),
           (nsw in meas_dict or nsw in meas_dict_pl) and is_digbased(context[1]),
           (nsw in ampm or nsw in adbc) and is_digbased(context[1]),
           (nsw.istitle() and nsw.isalpha() and len(nsw) > 3 and not is_cons(nsw)),
           (((nsw.startswith("O'") or nsw.startswith("D'")) and nsw[2:].istitle())
           or (nsw.endswith("s'") and nsw[:-2].istitle())
           or (nsw.endswith("'s") and nsw[:-2].istitle())),
           (not (nsw.isupper() or nsw.endswith('s') and nsw[:-1].isupper())
            and (nsw.lower() in wordlist
            or (nsw[:-1].lower() in wordlist and nsw.endswith('s')))
            and nsw not in ampm),
           triple_rep(nsw) and len(nsw) > 3,
           bool(acr_pattern.match(nsw) and nsw not in meas_dict),
           nsw.isalpha() and nsw.islower() and len(nsw) > 3,
           nsw.endswith('s') and nsw[:-1].isupper(),
           nsw in element_dict,
           nsw.isalpha and nsw.islower() and len(nsw) > 2,
           nsw.lower() in abbrev_dict or nsw in ['St.', 'st.', 'St']
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
    with open('{}/data/clf_ALPHA.pickle'.format(mod_path), 'wb') as file:
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
    elif nsw.lower() in abbrev_dict or nsw in ['St.', 'st.', 'St']:
        return 1
    elif (nsw.isupper() and is_cons(nsw) and not (nsw in meas_dict
          and is_digbased(context[1]))):
            return 2
    elif nsw.endswith('s') and nsw[:-1].isupper():
        return 2
    elif (nsw in meas_dict or nsw in meas_dict_pl) and is_digbased(context[1]):
        return 1
    elif (nsw in ampm or nsw in adbc) and is_digbased(context[1]):
        return 2
    elif nsw.istitle() and nsw.isalpha() and len(nsw) > 3 and not is_cons(nsw):
        return 3
    elif (((nsw.startswith("O'") or nsw.startswith("D'")) and nsw[2:].istitle())
           or (nsw.endswith("s'") and nsw[:-2].istitle())):
               return 3
    elif nsw in element_dict:
        return 1
    elif (not (nsw.isupper() or nsw.endswith('s') and nsw[:-1].isupper())
          and (nsw.lower() in wordlist
          or (nsw[:-1].lower() in wordlist and nsw.endswith('s')))
         and nsw not in ampm):
            return 3
    elif triple_rep(nsw) and len(nsw) > 3:
        return 3
    elif nsw.isalpha() and nsw.islower() and len(nsw) > 3:
        return 3
    elif acr_pattern.match(nsw) and nsw not in meas_dict:
        return 2
    elif len(nsw) == 1:
        return 2
    elif nsw.isalpha and nsw.islower() and len(nsw) > 2:
        return 3
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
    for i in range(len(w) - 2):
        if w[i] == w[i + 1] and w[i] == w[i + 2] and w[i].isalpha():
            return True
    return False
