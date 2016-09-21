import pickle
from collections import defaultdict

from nltk.corpus import brown
from nltk.tag.mapping import map_tag

from normalise.data.abbrev_dict import states


def store_pos_tag_dicts():
    pos_tag_dict = defaultdict(tuple)
    tagged = brown.tagged_sents()
    for sent in tagged:
        for tup in sent:
            if not tup[1] in pos_tag_dict[tup[0].lower()]:
                pos_tag_dict[tup[0].lower()] += (tup[1],)

    pos_tag_dict_univ = defaultdict(tuple)
    tagged_univ = brown.tagged_sents(tagset='universal')
    for sent in tagged_univ:
        for tup in sent:
            if not tup[1] in pos_tag_dict_univ[tup[0].lower()]:
                pos_tag_dict_univ[tup[0].lower()] += (tup[1],)
    for word in states.values():
        pos_tag_dict[word.lower()] += ('NNP',)
        pos_tag_dict_univ[word.lower()] += ('NOUN',)
    dicts = (pos_tag_dict, pos_tag_dict_univ)
    with open('../normalise/data/pos_dicts.pickle', 'wb') as file:
        pickle.dump(dicts, file)


def add_to_pos_dicts(pos_dict_new, pos_dict_new_univ):
    with open('pos_dicts.pickle', mode='rb') as f:
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
    with open('pos_dicts.pickle', mode='wb') as f:
        pickle.dump(dicts, f)
    print(dicts)


def create_pos_dict(dictionary):
    pos = defaultdict(tuple)
    pos_univ = defaultdict(tuple)
    for key in dictionary:
        if type(dictionary[key]) == tuple:
            pos[key] = dictionary[key]
            pos_univ[key] = map_tag('brown', 'universal', dictionary[key])
        elif type(dictionary[key]) == str:
            pos[key] = (dictionary[key],)
            pos_univ[key] = (map_tag('brown', 'universal', dictionary[key]),)
    return pos, pos_univ

title_dict = {
              'honourable': 'NP',
              'general': 'NP',
              'colonel': 'NP',
              'lieutenant': 'NP',
              'superintendent': 'NP',
              'senior': 'NP',
              'junior': 'NP',
              'sir': 'NP',
              'senator': 'NP',
              'doctor': 'NP',
              'duke': 'NP',
              'captain': 'NP'
              }
