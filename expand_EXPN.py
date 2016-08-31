import re
import pickle

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize as wt

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

with open('word_tokenized_lowered.pickle', mode='rb') as file:
    word_tokenized_lowered = pickle.load(file)

brown = word_tokenized_lowered[:1161192]


def find_matches(word):
    lst1 = []
    for i in range(len(brown)):
        if brown[i] == word:
            lst1.append(i)
    return lst1


def gen_signature(word):
    inds = find_matches(word)
    signature = []
    if word in wn.words():
        define = (eval("wn.{}.definition()".format(
                  str(wn.synsets(word)[0]).lower())))
        examples = (eval("wn.{}.examples()".format(
                    str(wn.synsets(word)[0]).lower())))
        if define:
            signature += wt(define)
        if examples:
            signature += wt(examples)
    for i in inds:
        signature += gen_context(i, brown)
    return signature


def gen_context(i, text):
    context = []
    start = i
    end = i + 1
    sloop = True
    while sloop:
        if text[start - 1] not in ['.', '!', '?']:
            start -= 1
        else:
            sloop = False
    eloop = True
    while eloop:
        if text[end] in ['.', '!', '?']:
            eloop = False
        else:
            end += 1
    if i - start < 4:
        if end - start >= 9:
            context += text[start: start + 9]
        else:
            context += text[start: end]
    elif end - i < 5:
        if end - start >= 9:
            context += text[end - 9: end]
        else:
            context += text[start: end]
    else:
        context += text[i - 4: i + 5]
    return context


def gen_candidates(word):
    cands = []
    reg = ''
    for lt in word:
        reg += lt
        reg += '[aeiou]*'
    regex = re.compile(reg)
    for w in wordlist:
        if regex.match(w):
            cands.append(w)
    return cands


def distance(abbrv, word):
    extras = [lt for lt in word if abbrv.count(lt) != word.count(lt)]
    count = 0
    for lt in extras:
        if lt not in ['a', 'e', 'i', 'o', 'u']:
            count += 1
        else:
            count += 0.2
    return count


def gen_best(abbrv):
    cands = [(it, distance(abbrv, it)) for it in gen_candidates(abbrv)]
    sorted_cands = sorted(cands, key=lambda cand: cand[1])
    final = []
    if len(sorted_cands) > 50:
        return sorted_cands[:50]
    else:
        return sorted_cands
