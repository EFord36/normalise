# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 09:45:45 2016

@author: emmaflint
"""
import pickle 

import nltk
from nltk.tokenize import word_tokenize as wt
from nltk import FreqDist as fd

with open('word_tokenized_lowered.pickle', mode='rb') as file:
    word_tokenized_lowered = pickle.load(file)

brown = word_tokenized_lowered[:1161192]
wordlist = [w for w, freq in fd(brown).most_common()]

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
    
def tag_sent(i, text):
    sent = gen_context(i, text)
    return nltk.pos_tag(sent)
    
def tag_cands(abbrv):
    tagged_cands = []
    for (cand, freq) in gen_best(abbrv):
        tagged_cands += nltk.pos_tag(wt(cand))
    return tagged_cands

def abbrev_tag(i, text):
    for (cand, tag) in tag_sent(i, text):
        if text[i] == cand:
            return tag
            
def tag_matches(i, text):
    matches = []
    for (cand, tag) in tag_cands(text[i]):
        if tag == abbrev_tag(i, text):
            matches += (cand, tag)
    return matches
    
    
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
    if len(sorted_cands) > 30:
        return sorted_cands[:30]
    else:
        return sorted_cands
    

   

    


            
            
