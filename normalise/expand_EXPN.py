# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

from math import log
from collections import defaultdict
import re
import pickle
from io import open

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.corpus import names
from nltk.tokenize import word_tokenize as wt
from nltk import FreqDist as fd
from nltk import pos_tag

from normalise.detect import mod_path
from normalise.data.abbrev_dict import states, create_user_abbrevs
from normalise.splitter import split
from normalise.tagger import is_digbased
from normalise.data.measurements import meas_dict, meas_dict_pl

with open('{}/data/word_tokenized_lowered.pickle'.format(mod_path), mode='rb') as f:
    word_tokenized_lowered = pickle.load(f)

with open('{}/data/pos_dicts.pickle'.format(mod_path), mode='rb') as file:
    pos_tag_dict, pos_tag_dict_univ = pickle.load(file)

with open('{}/data/abbrev_dict.pickle'.format(mod_path), mode='rb') as file:
    abbrevs_orig = pickle.load(file)

with open('{}/data/sig_dict.pickle'.format(mod_path), mode='rb') as file:
    sig_dict = pickle.load(file)

brown = word_tokenized_lowered[:1161192]
brown_common = {word: log(1161192 / freq) for
                word, freq in fd(brown).most_common(5000)[100:]}
words = [w for w, freq in fd(brown).most_common()]
names_lower = {w.lower() for w in names.words()}


def expand_EXPN(nsw, i, text, user_abbrevs={}):
    """Expand abbreviations to best possible match. If no close matches,
       return nsw."""
    try:
        if user_abbrevs:
            abbrevs = create_user_abbrevs(user_abbrevs)
        else:
            abbrevs = abbrevs_orig
        if nsw in ['St.', 'st.', 'St']:
            if i < len(text):
                if text[i + 1].lower() in names_lower:
                    return 'Saint'
                elif text[i + 1].endswith("'s"):
                    if text[i + 1][:-2].lower() in names_lower:
                           return 'Saint'
                elif text[i - 1].istitle():
                    return 'street'
                elif text[i + 1].istitle():
                    return 'Saint'
        elif nsw in meas_dict:
            if isinstance(i, int):
                if is_digbased(text[i - 1]):
                    if text[i - 1] == '1':
                        return meas_dict[nsw]
                    else:
                        return meas_dict_pl[nsw]
            else:
                full = text[int(i)]
                index = full.find(nsw)
                if index == 0:
                    if is_digbased(text[int(i) - 1]):
                        if text[int(i) - 1] == '1':
                            return meas_dict[nsw]
                        else:
                            return meas_dict_pl[nsw]
                else:
                    if is_digbased(full[:index]):
                        if text[int(i) - 1] == '1':
                            return meas_dict[nsw]
                        else:
                            return meas_dict_pl[nsw]
        elif (nsw.endswith('.') and nsw[:-1] in meas_dict
              and is_digbased(text[i - 1])):
            if text[i - 1] == '1':
                return meas_dict[nsw[:-1]]
            else:
                return meas_dict_pl[nsw[:-1]]
        if nsw.endswith('.') and nsw[:-1].lower() in abbrevs:
            w = nsw[:-1]
        else:
            w = nsw
        if w.lower() in abbrevs:
            cands = abbrevs[w.lower()]
            true_tag = abbrev_tag(i, text)
            true_tag_univ = abbrev_tag_univ(i, text)
            if len(cands) == 1:
                cand = cands[0]
                if pos_tag_dict_univ[cand.lower()] in [true_tag_univ, tuple()]:
                    return cand
            matches = []
            for cand in cands:
                if true_tag in pos_tag_dict[cand.lower()]:
                    matches += [cand]
            if not matches:
                for cand in cands:
                    if true_tag_univ in pos_tag_dict_univ[cand.lower()]:
                        matches += [cand]
            if matches:
                best = 0
                current = []
                if len(matches) == 1:
                    return matches[0]
                for cand in matches:
                    olap = overlap(i, cand, text)
                    if olap > best and cand in brown_common:
                        best = olap
                        current = [cand]
                    elif olap == best and best != 0:
                        current.append(cand)
                    elif cand in states.values() and not current:
                        current.append(cand)
                best = 0
                exp = ''
                for c in current:
                    if c in states.values():
                        return c
                    elif c in brown_common:
                        freq = brown_common[c]
                    else:
                        freq = 0
                    if freq < best:
                        best = freq
                        exp = c
            else:
                exp = maximum_overlap(w, i, text)
        elif w.lower().endswith('s.') and w.lower()[:-2] in abbrevs:
            return expand_EXPN(w.lower()[:-2], i, text) + 's'
        elif w.lower().endswith('s') and w.lower()[:-1] in abbrevs:
            return expand_EXPN(w.lower()[:-1], i, text) + 's'
        else:
            exp = maximum_overlap(w, i, text)
        if exp == '':
            return nsw
        else:
            return exp
    except(KeyboardInterrupt, SystemExit):
        raise
    except LookupError:
        raise
    except:
        return nsw


def maximum_overlap(w, i, text):
    """Return the candidate expansion with the highest overlap."""
    best = 0
    current = []
    curr = ''
    t_matches = tag_matches(i, text)
    if t_matches:
        if len(t_matches) == 1:
            if t_matches[0] in brown_common:
                return t_matches[0]
            else:
                return w
        for cand in t_matches:
            olap = overlap(i, cand, text)
            if olap > best and cand in words:
                best = olap
                current = [cand]
            elif olap == best and best != 0:
                current.append(cand)
        best = 0
        for c in current:
            if c in brown_common:
                freq = brown_common[c]
            else:
                freq = 0
            if freq < best:
                best = freq
                curr = c
            elif freq == best and len(tag_matches(i, text)) == 1:
                best = freq
                curr = c
            return curr
    if curr == '':
        return w
    else:
        return curr


def overlap(i, word, text):
    """Return overlap between words in the context of the abbreviation and
       words in the signatures generated for each candidate expansion."""
    overlap = 0
    sig = gen_signature(word)
    context = gen_context(i, text)
    for w in context:
        if w in sig:
            if w in brown_common:
                overlap += brown_common[w]
            else:
                overlap += log(1161192 / 1)
    return overlap


def find_matches(word):
    """Find examples of the candidate word in the Brown corpus."""
    lst1 = []
    for i in range(len(brown)):
        if brown[i] == word:
            lst1.append(i)
    return lst1


def gen_signature(word):
    """Generate a signature for each candidate expansion, using contextual
       information from the Brown corpus, as well as WordNet definitions and
       examples (if applicable)."""
    if word in gen_signature.dict:
        return gen_signature.dict[word]
    inds = find_matches(word)
    if len(inds) > 50:
        f = len(inds) / 50
        inds = [inds[int(i * f)] for i in range(50)]
    signature = defaultdict(int)
    for i in inds:
        for w in gen_context(i, brown):
            signature[w] += 1
    sig = {w for w in signature
           if signature[w] > 1
           and w not in stopwords.words('english') and w != ','}
    if word in wn.words():
        if wn.synsets(word) and str(wn.synsets(word)[0]).count("'") == 2:
            define = (eval("wn.{}.definition()".format(
                      str(wn.synsets(word)[0]).lower())))
            examples = (eval("wn.{}.examples()".format(
                        str(wn.synsets(word)[0]).lower())))
            if examples:
                for ex in examples:
                        sig.update([w for w in wt(ex)
                                   if w not in stopwords.words('english')])
            if define:
                        sig.update([w for w in wt(define)
                                   if w not in stopwords.words('english')])
    gen_signature.dict[word] = sig
    return sig

gen_signature.dict = sig_dict

def gen_context(i, text):
    """Generate context for the abbreviation - 4 words either side unless
       sentence is too short."""
    ind = i
    context = []
    text = text[:]
    if not isinstance(i, int):
        ind = int(i)
        split_token = text[ind]
        del text[ind]
        parts = split({ind: (split_token, 'SPLT')}, verbose=False)
        for it in sorted(parts, reverse=True):
            text.insert(ind, parts[it][0])
    start = ind
    end = ind + 1
    sloop = True
    while sloop and start > 0:
        if text[start - 1] not in ['.', '!', '?']:
            start -= 1
        else:
            sloop = False
    eloop = True
    while eloop and end <= len(text) - 1:
        if text[end] in ['.', '!', '?']:
            eloop = False
        else:
            end += 1
    if ind - start < 4:
        if end - start >= 9:
            context += text[start: start + 9]
        else:
            context += text[start: end]
    elif end - ind < 5:
        if end - start >= 9:
            context += text[end - 9: end]
        else:
            context += text[start: end]
    else:
        context += text[ind - 4: ind + 5]
    return context


def tag_sent(i, text):
    """POS tag sentence (or context) containing abbreviation."""
    sent = gen_context(i, text)
    return pos_tag(sent)


def tag_cands(abbrv):
    """Tags candidate expansions of the abbreviaiton with POS."""
    tagged_cands = []
    for (cand, freq) in gen_best(abbrv):
        tagged_cands += [(cand, pos_tag_dict[cand])]
    return tagged_cands


def abbrev_tag(i, text):
    """Return POS tag for the abbreviation."""
    for (cand, tag) in tag_sent(i, text):
        if isinstance(i, int):
            if text[i] == cand:
                return tag
        else:
            if split({int(i): (text[int(i)], 'SPLT')},
                     verbose=False)[i][0] == cand:
                return tag


def tag_sent_univ(i, text):
    """POS tag sentence using universal tagset."""
    sent = gen_context(i, text)
    return pos_tag(sent, tagset='universal')


def tag_cands_univ(abbrv):
    """Tags candidate expansions using universal tagset."""
    tagged_cands = []
    for (cand, freq) in gen_best(abbrv):
        tagged_cands += [(cand, pos_tag_dict_univ[cand])]
    return tagged_cands


def abbrev_tag_univ(i, text):
    """Return POS tag for the abbreviation using universal tagset."""
    for (cand, tag) in tag_sent_univ(i, text):
        if isinstance(i, int):
            if text[i] == cand:
                return tag
        else:
            if split({int(i): (text[int(i)], 'SPLT')},
                     verbose=False)[i][0] == cand:
                return tag


def tag_matches(i, text):
    """Return candidate expansions whose POS tag matches the POS tag of the
       abbreviation."""
    matches = []
    if isinstance(i, int):
        abbrev = text[i]
    else:
        abbrev = split({int(i): (text[int(i)], 'SPLT')}, verbose=False)[i][0]
    true_tag = abbrev_tag(i, text)
    for (cand, tags) in tag_cands(abbrev):
        if true_tag in tags:
            matches += [cand]
    if not matches:
        true_tag_univ = abbrev_tag_univ(i, text)
        for (cand, tags) in tag_cands_univ(abbrev):
            if true_tag_univ in tags:
                matches += [cand]
    if not matches and len(tag_cands_univ(abbrev)) == 1:
        if tag_cands_univ(abbrev)[0][1] == tuple():
            return [tag_cands_univ(abbrev)[0][0]]
    if len(matches) <= 10:
        return matches
    else:
        return matches[:10]


def find_last_letter(w):
    """Find last alphabetic character in a word."""
    if w[-1].isalpha():
        return w[-1]
    else:
        return find_last_letter(w[:-1])


def gen_candidates(word):
    """Generate a list of candidate expansions given an abbreviation."""
    vowel_cands = []
    start_cands = []
    start_and_end_cands = []
    reg_cons = ''
    reg_start = ''
    reg_start_and_end = ''
    for lt in word.lower():
        if lt.isalpha():
            reg_cons += lt
            reg_cons += '[aeiou]*'
    reg_cons += '$'
    regex_cons = re.compile(reg_cons)
    for lt in word.lower():
        if lt.isalpha():
            reg_start += lt
    regex_start = re.compile(reg_start)
    last = find_last_letter(word)
    if last == 's':
        last = find_last_letter(word[:word.rfind(last)]) + last
    for lt in word[:word.rfind(last)].lower():
        if lt.isalpha():
            reg_start_and_end += lt
    reg_start_and_end += '.*{}$'.format(last)
    regex_start_and_end = re.compile(reg_start_and_end)
    for w in words:
        if regex_cons.match(w):
            vowel_cands.append(w)
        elif regex_start_and_end.match(w):
            start_and_end_cands.append(w)
        elif regex_start.match(w):
            start_cands.append(w)
    return vowel_cands, start_and_end_cands, start_cands


def distance(abbrv, word):
    """Calculate distance between abbreviation and potential expansion."""
    extras = [lt for lt in word if abbrv.count(lt) != word.count(lt)]
    count = 0
    for lt in extras:
        if lt not in ['a', 'e', 'i', 'o', 'u']:
            count += 1
        else:
            count += 0.2
    return count


def gen_best(abbrv):
    """Generate best expansions given abbreviation (up to 50)."""
    vowel_cands, start_and_end_cands, start_cands = gen_candidates(abbrv)
    vowel_freqs = sorted([(it, brown_common[it])
                         for it in vowel_cands
                         if it in brown_common],
                         key=lambda cand: cand[1])
    start_and_end_freqs = sorted([(it, brown_common[it])
                                 for it in start_and_end_cands
                                 if it in brown_common],
                                 key=lambda cand: cand[1])
    start_freqs = sorted([(it, brown_common[it])
                         for it in start_cands
                         if it in brown_common],
                         key=lambda cand: cand[1])
    ordered_cands = [(word, freq) for word, freq in vowel_freqs]
    start_and_end_ind = 0
    start_ind = 0
    while (start_and_end_ind < len(start_and_end_freqs) - 1
           and start_ind < len(start_freqs)):
        ordered_cands += [start_and_end_freqs[start_and_end_ind]]
        start_and_end_ind += 1
        ordered_cands += [start_and_end_freqs[start_and_end_ind]]
        start_and_end_ind += 1
        ordered_cands += [start_freqs[start_ind]]
        start_ind += 1
    if start_and_end_ind < len(start_and_end_freqs):
        ordered_cands.extend([(word, freq) for word, freq
                             in start_and_end_freqs[start_and_end_ind:]])
    if start_ind < len(start_freqs):
        ordered_cands.extend([(word, freq) for word, freq
                             in start_freqs[start_ind:]])
    for word in start_and_end_cands + start_cands:
        if word not in [w for w, f in ordered_cands]:
            ordered_cands += [(word, 0)]
    if len(ordered_cands) <= 50:
        return ordered_cands
    else:
        return ordered_cands[:50]
