# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 16:15:15 2016

@author: emmaflint
"""
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (accuracy_score, confusion_matrix, precision_score,
recall_score)

from gold_standard_dict import gold_standard_dict, gold_standard_tagged
from tag1 import tag1

# Tag gold standard NSW tokens, return dictionary of predicted tags.
gold_standard_predicted = tag1(gold_standard_dict)

def predicted_tags():
    """Return list of predicted tags"""
    out = []
    for ind, (value1, value2) in gold_standard_predicted.items():
        out.append(value2)
    return out

def goldstandard_tags():
    """Return list of gold standard tags"""
    out = []
    for ind, (value1, value2) in gold_standard_tagged.items():
        out.append(value2)
    return out

# Compute % accuracy by comparing gold standard tags to predicted tags.
accuracy = accuracy_score(goldstandard_tags(),predicted_tags())

labels = ['ALPHA', 'NUMB', 'SPLT', 'MISC']

# Return a confusion matrix.
confusion = confusion_matrix(goldstandard_tags(),predicted_tags(), labels)

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
    """ List instances where the predicted tag differs from the correct tag,
    ie. errors made by the tagger.
    """
    for ind, (txt, tag) in gold_standard_predicted.items():
        if tag != gold_standard_tagged[ind][1]:
            print("Item: {0}, Predicted Tag: {1}, True Tag: {2}"
            .format(txt, tag, gold_standard_tagged[ind][1]))

precision = precision_score(goldstandard_tags(),predicted_tags(),
                            labels, average = 'weighted')

recall = recall_score(goldstandard_tags(),predicted_tags(),
                            labels, average = 'weighted')
