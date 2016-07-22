# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 13:06:35 2016

@author: Elliot
"""
from __future__ import division, print_function, unicode_literals

from NSW_new import create_NSW_dict
from tag1 import tag1
from splitter import split, retag1
from class_ALPHA import run_clfALPHA
from class_NUMB import run_clfNUMB
from tag_MISC import tag_MISC

def detect_and_tag(text):
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
    return tagged_ALPHA, tagged_NUMB, tagged_MISC
