# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 15:18:06 2016

@author: emmaflint
"""

from __future__ import division, print_function, unicode_literals

from NSW_new import create_NSW_dict
from tag1 import tag1
from splitter import split, retag1
from class_ALPHA import run_clfALPHA
from class_NUMB import run_clfNUMB
from tag_MISC import tag_MISC
from expand_all import expand_all

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
    out = text
    for item in (expanded_ALPHA, expanded_NUMB, expanded_MISC):
        for nsw in item.items():
            if isinstance(nsw[0], int):
                out[nsw[0]] = nsw[1][3]
            elif out[int(nsw[0])] == text[int(nsw[0])]:
                out[int(nsw[0])] = nsw[1][3]
            elif text[int(nsw[0])].find(out[int(nsw[0])]) < text[int(nsw[0])].find(nsw[1][0]):
                out[int(nsw[0])] = out[int(nsw[0])] + " " + nsw[1][3]
            elif text[int(nsw[0])].find(out[int(nsw[0])]) > text[int(nsw[0])].find(nsw[1][0]):
                out[int(nsw[0])] = nsw[1][3] + " " + out[int(nsw[0])]
    return out
