import pickle
from collections import defaultdict

from nltk import FreqDist as fd
from nltk.corpus import brown as brown
from nltk.util import ngrams

with open('../normalise/data/wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

words = {'^' + w.lower() + '$'
         for w
         in wordlist
         if w.isalpha()}

quadgram_count = defaultdict(int)

for w in words:
        for i in range(len(w) - 2):
            quadgram_count[w[i: i + 4]] += 1


def quadgram_word(word):
    if word.endswith('.') or word.endswith("'"):
        return quadgram_word(word[:-1])
    else:
        test = '^' + word.lower() + '$'
        for i in range(len(test) - 3):
            if quadgram_count[test[i: i + 4]] != 0:
                return True
        return False
