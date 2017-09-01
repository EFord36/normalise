# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import sys
import re
import pickle
from io import open

from normalise.detect import mod_path
from normalise.tagger import tagify, NSWs, is_digbased, only_alpha
from normalise.data.measurements import meas_dict

with open('{}/data/wordlist.pickle'.format(mod_path), mode='rb') as file:
    wordlist = pickle.load(file)

digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

if __name__ == "__main__":
    SPLT_dict = {ind: (nsw, tag) for ind, (nsw, tag)
                 in tagify(NSWs, verbose=False).items()
                 if tag == 'SPLT'}


def tag_SPLT(lst):
    """ Assign new index and tag 'SPLT-' to every part of a split token."""
    if len(lst) > 9:
        inc = round((1 / (len(lst))), 2)
    else:
        inc = 0.1
    ind = lst[0]
    out = {}
    for i in range(1, len(lst)):
        out.update({ind + inc * i: (lst[i], 'SPLT-')})
    return out


def split(dic, verbose=True):
    """ Form dictionary of SPLT tokens."""
    split_dict = {}
    done = 0
    for ind, (nsw, tag) in dic.items():
        if verbose:
            sys.stdout.write("\r{} of {} split".format(done, len(dic)))
            sys.stdout.flush()
        out = [ind]
        emph_list = []
        emph_match = emph_pattern.match(nsw)
        if emph_match:
            emph_list += emph_match.groups()
        else:
            emph_list += [nsw]
        hyph_list = []
        for nsw in emph_list:
            hyph_list.extend([item for item in nsw.split('-') if item])
        slash_list = []
        for nsw in hyph_list:
            slash_list.extend([item for item in nsw.split('/') if item])
        space_list = []
        for nsw in slash_list:
            space_list.extend([item for item in nsw.split(' ') if item])
        underscore_list = []
        for nsw in space_list:
            underscore_list.extend([item for item in nsw.split('_') if item])
        mixedalnum_list = []
        for nsw in underscore_list:
            mixedalnum_list.extend([item for item in mixedalnum_split(nsw)
                                    if item])
        updown_list = []
        for nsw in mixedalnum_list:
            updown_list.extend([item for item in split_updown(nsw) if item])
        mixedcase_list = []
        for nsw in updown_list:
            mixedcase_list.extend([item for item in mixedcase_split(nsw)
                                   if item])
        out.extend(mixedcase_list)
        split_dict.update(tag_SPLT(out))
        done += 1
    if verbose:
        sys.stdout.write("\r{} of {} split".format(done, len(dic)))
        sys.stdout.flush()
        print("\n")
    return split_dict


def retagify(dic, verbose=True):
    """ Retag each part of a SPLT token as 'SPLT-ALPHA', 'SPLT-NUMB' or
    'SPLT-MISC'.
    """
    out = {}
    for ind, (it, tag) in dic.items():
        if verbose:
            sys.stdout.write("\r{} of {} retagged".format(len(out), len(dic)))
            sys.stdout.flush()
        if len(it) > 100:
            out.update({ind: (it, tag + 'MISC')})
        if is_digbased(it):
            out.update({ind: (it, tag + 'NUMB')})
        elif (only_alpha(it) and
              (not mixedcase_pattern.match(it) or
               len(it) <= 3 or (it[-1] == 's' and not
               mixedcase_pattern.match(it[:-1])))):
                    out.update({ind: (it, tag + 'ALPHA')})
        elif it in meas_dict:
            out.update({ind: (it, tag + 'ALPHA')})
        else:
            out.update({ind: (it, tag + 'MISC')})
    if verbose:
        sys.stdout.write("\r{} of {} retagged".format(len(out), len(dic)))
        sys.stdout.flush()
        print("\n")
    return out


def split_updown(nsw):
    """ For tokens matching updown_pattern; split before or after penultimate
    upper-case character depending on whether resulting word is in wordlist.
    If neither group in wordlist, split before penultimate upper-case letter
    as default.
    """
    try:
        m = updown_pattern.match(nsw)
        if m:
            if (m.group(2) + m.group(3)).lower() in wordlist:
                return [m.group(1), m.group(2) + m.group(3)]
            elif m.group(3) in wordlist:
                return [m.group(1) + m.group(2), m.group(3)]
            else:
                return [m.group(1), m.group(2) + m.group(3)]
        else:
            return [nsw]
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        return nsw


def mixedalnum_split(nsw):
    """ Split tokens on transitions from letters to numbers or numbers to
    letters.
    """
    try:
        out = []
        ind = 0
        if nsw[0] in digits:
            cat = 'num'
        elif nsw[0].isalpha:
            cat = 'let'
        else:
            cat = 'punc'
        for i in range(1, len(nsw)):
            if nsw[i] in digits:
                if cat == 'num' or cat == 'punc':
                    pass
                else:
                    out.append(nsw[ind:i])
                    cat = 'num'
                    ind = i
            elif nsw[i].isalpha():
                if cat == 'let' or cat == 'punc':
                    pass
                else:
                    out.append(nsw[ind:i])
                    cat = 'let'
                    ind = i
            elif nsw[i]=='°' and cat=='num' and nsw[i+1:] in ['C', 'F', 'K', 'Re']:
                out.append(nsw[ind:i])
                ind = i
                break
            else:
                pass
        out.append(nsw[ind:])
        if len(out)==3 and is_digbased(out[0]) and out[2].isdigit() and out[1] + out[2] in meas_dict:
            out = [out[0], out[1] + out[2]]
        return out
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        return nsw


def mixedcase_split(nsw):
    """ Split tokens on transitions from upper- to lower- or lower- to
    upper-case.
    """
    try:
        if nsw.isalpha():
            if nsw.istitle():
                return [nsw]
            else:
                out = []
                ind = 0
                if nsw[0].isupper():
                    cat = 'up'
                else:
                    cat = 'low'
                for i in range(1, len(nsw)):
                    if nsw[i].isupper():
                        if cat == 'up':
                            pass
                        else:
                            out.append(nsw[ind:i])
                            cat = 'up'
                            ind = i
                    else:
                        if cat == 'low':
                            pass
                        elif nsw[i - 1].isupper():
                            cat = 'low'
                            pass
                        else:
                            out.append(nsw[ind:i])
                            cat = 'low'
                            ind = i
                out.append(nsw[ind:])
                return out
        else:
            return [nsw]
    except(KeyboardInterrupt, SystemExit):
        raise
    except:
        return nsw


hyphen_pattern = re.compile('''
(([\'\.]?                       # optional "'" or "."
[A-Za-z]                        # letter
[\'\.]?)                        # optional "'" or "."
+                               # lines 1-3 repeated one or more times
(-|/|\s|(-&-))                  # followed by '-', '/', or '-&-'
)+                              # all of the above repeated 1+ times
([\'\.]?[A-Za-z][\.\']?)*       # optional final 'word' (same as lines 1-3)
$                               # end of string
''', re.VERBOSE)

mixedcase_pattern = re.compile('''
([A-Z]{2,}[a-z]) |    # 2 or more capitals, a lowercase OR
(.*[a-z][A-Z])        # any number of chars, a lowercase, an uppercase
''', re.VERBOSE)

emph_pattern = re.compile('''
([\*~<:]+)                      # '*' or '~' repeated one or more times
((?:[A-Za-z]+[-/\']?)+[A-Za-z]+)# optionally hyphenated 'word'
([\*~>:]+)                      # '*' or '~' repeated one or more times
$                               # end of string
''', re.VERBOSE)

updown_pattern = re.compile('''
([A-Z]+?)                       # 1 or more capitals (non-greedy) (capturing)
([A-Z])                         # a capital (capturing)
([a-z]+)                        # 1 or more lowercase (capturing)
$
''', re.VERBOSE)
