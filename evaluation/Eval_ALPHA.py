# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import (accuracy_score, confusion_matrix, precision_score,
                             recall_score)

from normalise.class_ALPHA import run_clfALPHA, gen_frame
from normalise.tagger import tagify
from gs_ALPHA_dict import gs_ALPHA_dict, gs_ALPHA_tagged
from gold_standard_full import gold_standard

text = gold_standard


def create_ALPHA_ex():
    ALPHA_ex = []
    for ind, (word, tag) in gs_ALPHA_dict.items():
        ALPHA_ex.append(gen_frame((ind, (word, tag)), text))
    with open('gs_alphas', mode='w', encoding='utf-8') as file:
        file.write(str(ALPHA_ex))

gold_standard_predicted = run_clfALPHA(gs_ALPHA_dict, text, verbose=False)


def gold_vs_pred_tuple():
    """ Return list of predicted tags and list of gold standard tags"""
    predicted = []
    gold = []
    for ind, (value1, value2, value3) in gold_standard_predicted.items():
        predicted.append(value3)
        gold.append(gs_ALPHA_tagged[ind][2])
    return predicted, gold

accuracy = accuracy_score(gold_vs_pred_tuple()[0], gold_vs_pred_tuple()[1])

labels = ['LSEQ', 'EXPN', 'WDLK']

# Return a confusion matrix.
confusion = confusion_matrix(gold_vs_pred_tuple()[0], gold_vs_pred_tuple()[1],
                             labels)

# Return a normalised confusion matrix.
confusion_normalised = (confusion.astype('float') / confusion.sum(axis=1)
                        [:, np.newaxis])


def plot_confusion_matrix(r):
    """ Plot a graphical confusion matrix with predicted tags on the x axis
    and correct tags on the y axis. Allows us to see which pairs of tags are
    confused most frequently.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(r)
    plt.title('Confusion Matrix')
    fig.colorbar(cax)
    ax.set_xticklabels([''] + labels)
    ax.set_yticklabels([''] + labels)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.show()


def list_errors():
    for ind, (txt, tag, ntag) in gold_standard_predicted.items():
        if ntag != gs_ALPHA_tagged[ind][2]:
            print("Ind: {0}, Item: {1}, ".format(ind, txt)
                  + "Predicted Tag: {}, ".format(ntag)
                  + "True Tag: {}, ".format(gs_ALPHA_tagged[ind][2])
                  + "/n, {}".format(gen_frame((ind, (txt, tag)), text))
                  )
