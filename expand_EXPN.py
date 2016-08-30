import re
import pickle

with open('wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)


def gen_candidates(word):
    cands = []
    reg = '[aeiou]*'
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
    count = 0.0
    for lt in extras:
        if lt in ['a', 'e', 'i', 'o', 'u']:
            count += 0.1
        else:
            count += 1.0
    return count


def gen_best(abbrv):
    cands = [(it, distance(abbrv, it)) for it in gen_candidates(abbrv)]
    sorted_cands = sorted(cands, key=lambda cand: cand[1])
    final = []
    i = 0
    while len(final) < 5 and i < 10:
        for it in sorted_cands:
            if it[1] == i:
                final.append(it)
        i += 1
    return final
