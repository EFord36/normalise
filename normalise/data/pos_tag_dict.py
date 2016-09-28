# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import pickle
from collections import defaultdict

from nltk.corpus import treebank, brown
from nltk.tag.mapping import map_tag

from normalise.data.abbrev_dict import states


def store_pos_tag_dicts():
    pos_tag_dict = defaultdict(tuple)
    tagged = treebank.tagged_sents()
    for sent in tagged:
        for tup in sent:
            if not tup[1] in pos_tag_dict[tup[0].lower()]:
                pos_tag_dict[tup[0].lower()] += (tup[1],)

    pos_tag_dict_univ = defaultdict(tuple)
    penn_tagged_univ = treebank.tagged_sents(tagset='universal')
    brown_tagged_univ = brown.tagged_sents(tagset='universal')
    for text in [penn_tagged_univ, brown_tagged_univ]:
        for sent in text:
            for tup in sent:
                if not tup[1] in pos_tag_dict_univ[tup[0].lower()]:
                    pos_tag_dict_univ[tup[0].lower()] += (tup[1],)
    for word in states.values():
        pos_tag_dict[word.lower()] += ('NNP',)
        pos_tag_dict_univ[word.lower()] += ('NOUN',)
    dicts = (pos_tag_dict, pos_tag_dict_univ)
    with open('{}/data/pos_dicts.pickle'.format(mod_path), 'wb') as file:
        pickle.dump(dicts, file, protocol=2)


def add_to_pos_dicts(pos_dict_new, pos_dict_new_univ):
    with open('{}/data/pos_dicts.pickle'.format(mod_path), mode='rb') as f:
        pos_dict, pos_dict_univ = pickle.load(f)

    for key in pos_dict_new:
        if type(pos_dict_new[key]) == tuple:
            for tag in pos_dict_new[key]:
                if tag not in pos_dict[key]:
                    pos_dict[key] = pos_dict[key] + (tag,)
        elif type(pos_dict_new[key]) == str:
            if pos_dict_new[key] not in pos_dict[key]:
                pos_dict[key] = pos_dict[key] + (pos_dict_new[key],)

    for key in pos_dict_new_univ:
        if type(pos_dict_new_univ[key]) == tuple:
            for tag in pos_dict_new_univ[key]:
                if tag not in pos_dict_univ[key]:
                    pos_dict_univ[key] = pos_dict_univ[key] + (tag,)
        elif type(pos_dict_new_univ[key]) == str:
            if pos_dict_new[key] not in pos_dict[key]:
                pos_dict_univ[key] = (pos_dict_univ[key]
                                     + (pos_dict_new_univ[key],))
    dicts = (pos_dict, pos_dict_univ)
    with open('{}/data/pos_dicts.pickle'.format(mod_path), mode='wb') as f:
        pickle.dump(dicts, f, protocol=2)
    print(dicts)


def create_pos_dict(dictionary):
    pos = defaultdict(tuple)
    pos_univ = defaultdict(tuple)
    for key in dictionary:
        if type(dictionary[key]) == tuple:
            pos[key] = dictionary[key]
            pos_univ[key] = map_tag('en-ptb', 'universal', dictionary[key])
        elif type(dictionary[key]) == str:
            pos[key] = (dictionary[key],)
            pos_univ[key] = (map_tag('en-ptb', 'universal', dictionary[key]),)
    return pos, pos_univ

title_dict = {
              'honourable': 'NNP',
              'general': 'NNP',
              'colonel': 'NNP',
              'lieutenant': 'NNP',
              'superintendent': 'NNP',
              'senior': 'NNP',
              'junior': 'NNP',
              'sir': 'NNP',
              'senator': 'NNP',
              'doctor': 'NNP',
              'duke': 'NNP',
              'captain': 'NNP'
              }
