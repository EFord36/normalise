from __future__ import division, print_function, unicode_literals

import pickle
from nltk.corpus import names

from normalise.detect import create_NSW_dict
from normalise.tagger import tagify, is_digbased
from normalise.splitter import split, retagify
from normalise.class_ALPHA import run_clfALPHA
from normalise.class_NUMB import run_clfNUMB, gen_frame
from normalise.tag_MISC import tag_MISC
from normalise.expand_all import expand_all
from normalise.expand_NUMB import bmoney

with open('../normalise/data/wordlist.pickle', mode='rb') as file:
    wordlist = pickle.load(file)

names_lower = {w.lower() for w in names.words()}


def normalise(text, verbose=True):
    if verbose:
        print("\nCREATING NSW DICTIONARY")
        print("-----------------------\n")

    NSWs = create_NSW_dict(text, verbose=verbose)
    if verbose:
        print("{} NSWs found\n".format(len(NSWs)))
        print("TAGGING NSWs")
        print("------------\n")
    tagged = tagify(NSWs, verbose=verbose)
    ALPHA_dict = {}
    NUMB_dict = {}
    MISC_dict = {}
    SPLT_dict = {}
    for item in tagged.items():
        tag = item[1][1]
        if tag == 'ALPHA':
            ALPHA_dict.update((item,))
        elif tag == 'NUMB':
            NUMB_dict.update((item,))
        elif tag == 'MISC':
            MISC_dict.update((item,))
        elif tag == 'SPLT':
            SPLT_dict.update((item,))
    if verbose:
        print("SPLITTING NSWs")
        print("--------------\n")
    splitted = split(SPLT_dict, verbose=verbose)
    if verbose:
        print("RETAGGING SPLIT NSWs")
        print("--------------------\n")
    retagged = retagify(splitted, verbose=verbose)
    for item in retagged.items():
        tag = item[1][1]
        if tag == 'SPLT-ALPHA':
            ALPHA_dict.update((item,))
        elif tag == 'SPLT-NUMB':
            NUMB_dict.update((item,))
        elif tag == 'SPLT-MISC':
            MISC_dict.update((item,))
    if verbose:
        print("CLASSIFYING ALPHABETIC NSWs")
        print("---------------------------\n")
    tagged_ALPHA = run_clfALPHA(ALPHA_dict, text, verbose=verbose)
    if verbose:
        print("CLASSIFYING NUMERIC NSWs")
        print("------------------------\n")
    tagged_NUMB = run_clfNUMB(NUMB_dict, text, verbose=verbose)
    if verbose:
        print("CLASSIFYING MISCELLANEOUS NSWs")
        print("------------------------------\n")
    tagged_MISC = tag_MISC(MISC_dict, verbose=verbose)
    if verbose:
        print("EXPANDING ALPHABETIC NSWs")
        print("-------------------------\n")
    expanded_ALPHA = expand_all(tagged_ALPHA, text, verbose=verbose)
    if verbose:
        print("EXPANDING NUMERIC NSWs")
        print("----------------------\n")
    expanded_NUMB = expand_all(tagged_NUMB, text, verbose=verbose)
    if verbose:
        print("EXPANDING MISCELLANEOUS NSWs")
        print("----------------------------\n")
    expanded_MISC = expand_all(tagged_MISC, text, verbose=verbose)
    return expanded_ALPHA, expanded_NUMB, expanded_MISC


def tokenize_basic(text):
    guess = text.split(' ')
    out = []
    for i in range(len(guess) - 1):
        if not guess[i]:
            pass
        elif guess[i].isalpha():
            out.append(guess[i])
        elif guess[i][0] in ['(', '[', '{']:
            if guess[i][1] in [')', ']', '}']:
                out.extend([guess[i][0], guess[i][1:-1], guess[i][-1]])
            else:
                out.extend([guess[i][0], guess[i][1:]])
        elif guess[i][-1] in [')', ']', '}']:
                out.extend([guess[i][:-1], guess[i][-1]])
        elif guess[i][-1] == '.' and guess[i][:-1].isalpha():
            following = guess[i + 1]
            if following.istitle() and following.lower() in wordlist:
                if following.lower() in names_lower:
                    if guess[i][:-1] in wordlist:
                        out.extend([guess[i][:-1], '.'])
                    else:
                        out.append(guess[i])
                else:
                    out.extend([guess[i][:-1], '.'])
            elif guess[-1][-1] == '.' and is_digbased(guess[-1][:-1]):
                out.extend([guess[-1][:-1], '.'])
            else:
                out.append(guess[i])
        elif guess[i].endswith((',', ':', ';')):
            out.extend([guess[i][:-1], guess[i][-1]])
        else:
            out.append(guess[i])
    if guess[-1].isalpha():
        out.append(guess[-1])
    elif guess[-1][-1] == '.' and guess[-1][:-1] in wordlist:
        out.extend([guess[-1][:-1], '.'])
    elif guess[-1][-1] == '.' and is_digbased(guess[-1][:-1]):
        out.extend([guess[-1][:-1], '.'])
    elif guess[-1].endswith((',', ':', ';')):
        out.extend([guess[-1][:-1], guess[-1][-1]])
    else:
        out.append(guess[-1])
    return out


def standardise(text, tokenizer=tokenize_basic, verbose=True):
    if type(text) == str:
        if tokenizer == tokenize_basic and verbose:
            print("NOTE: using basic tokenizer.\n"
                  "For better results, input tokenized text,"
                  " or use a custom tokenizer")
            return insert(tokenizer(text), verbose=verbose)
        else:
            return insert(tokenizer(text), verbose=verbose)
    else:
        return insert(text, verbose=verbose)


def insert(text, verbose=True):
    (expanded_ALPHA,
    expanded_NUMB,
    expanded_MISC) = normalise(text, verbose=verbose)
    out = text[:]
    split_dict = {}
    for item in (expanded_ALPHA, expanded_NUMB, expanded_MISC):
        for nsw in item.items():
            if isinstance(nsw[0], int):
                out[nsw[0]] = nsw[1][3]
                if nsw[1][2] == 'MONEY' and gen_frame(nsw, text)[3] in bmoney:
                    out[nsw[0] + 1] = ''
            else:
                rind = int(nsw[0])
                if rind in split_dict:
                    split_dict[rind][100 * (nsw[0] - rind)] = nsw[1][3]
                else:
                    split_dict[rind] = {(100 * (nsw[0] - rind)): nsw[1][3]}
                if out[rind] == text[rind]:
                    out[rind] = nsw[1][3]
                else:
                    final = ''
                    for it in sorted(split_dict[rind]):
                        final += ' '
                        final += split_dict[rind][it]
                    final = final[1:]
                    out[rind] = final
    return out


def rejoin(tokenized_text):
    out = ''
    for word in tokenized_text:
        out += word
        out += ' '
    return out
