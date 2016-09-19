# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 15:18:06 2016

@author: emmaflint
"""

from __future__ import division, print_function, unicode_literals

from normalise.NSW_new import create_NSW_dict
from normalise.tag1 import tag1
from normalise.splitter import split, retag1
from normalise.class_ALPHA import run_clfALPHA
from normalise.class_NUMB import run_clfNUMB
from normalise.tag_MISC import tag_MISC
from normalise.expand_all import expand_all


def normalise(text):
    NSWs = create_NSW_dict(text)
    tagged = tag1(NSWs)
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
    splitted = split(SPLT_dict)
    retagged = retag1(splitted)
    for item in retagged.items():
        tag = item[1][1]
        if tag == 'SPLT-ALPHA':
            ALPHA_dict.update((item,))
        elif tag == 'SPLT-NUMB':
            NUMB_dict.update((item,))
        elif tag == 'SPLT-MISC':
            MISC_dict.update((item,))
    tagged_ALPHA = run_clfALPHA(ALPHA_dict, text)
    tagged_NUMB = run_clfNUMB(NUMB_dict, text)
    tagged_MISC = tag_MISC(MISC_dict)
    expanded_ALPHA = expand_all(tagged_ALPHA, text)
    expanded_NUMB = expand_all(tagged_NUMB, text)
    expanded_MISC = expand_all(tagged_MISC, text)
    return expanded_ALPHA, expanded_NUMB, expanded_MISC


def insert(text):
    expanded_ALPHA, expanded_NUMB, expanded_MISC = normalise(text)
    out = text[:]
    split_dict = {}
    for item in (expanded_ALPHA, expanded_NUMB, expanded_MISC):
        for nsw in item.items():
            if isinstance(nsw[0], int):
                out[nsw[0]] = nsw[1][3]
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
