#!/usr/bin/python3

import sys
import json
import re
import pandas as pd
import numpy as np
import csv
from gensim.models import word2vec

_RESTAURANTS_DIR = '../data/restaurants/'
_NUTRITION_DIR = '../data/nutrition/'

sentences = []

with open(_RESTAURANTS_DIR + 'restaurants-w-ids-items.csv') as csvfile:
    readcsv = csv.reader(csvfile, delimiter=',')
    for row in readcsv:
        item = row[4].strip()
        description = row[5].strip()
        sentence = ' '.join([item, description])
        sentence = sentence.strip().split()
        sentences.append(sentence)

# hs = if 1, hierarchical softmax will be used for model training. If set to 0 (default),
# and negative is non-zero, negative sampling will be used.
#
# negative = if > 0, negative sampling will be used, the int for negative specifies
# how many “noise words” should be drawn (usually between 5-20). Default is 5.
# If set to 0, no negative samping is used.

# # sentences = word2vec.Text8Corpus('text8')
model = word2vec.Word2Vec(sentences, size=300, window=10, min_count=20,
                          workers=4, sample=1e-3, batch_words=40)
model_hs1 = word2vec.Word2Vec(sentences, hs=1, negative=5, size=300, window=10, min_count=20,
                              workers=4, sample=1e-3, batch_words=40)
model_hs1_neg0 = word2vec.Word2Vec(sentences, hs=1, negative=0, size=300, window=10, min_count=20,
                                   workers=4, sample=1e-3, batch_words=40)


# nutrition_model = word2vec.Word2Vec(nutrition_sentences, size=5,
#                                     window=10, min_count=20, workers=4, sample=1e-3, batch_words=40)
#
model.doesnt_match("spicy walnut glaze orange".split())
# # >> 'orange'
#
model.similar_by_word('walnuts')
# # >> returns similar words, but not walnuts
#
model.save('wordmodel_allmenus_sept25_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod')
model_hs1.save(
    'wordmodel_allmenus_hs1_sept25_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod')
model_hs1_neg0.save(
    'wordmodel_allmenus_hs1_neg0_sept25_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod')

model.init_sims(replace=True)
model_hs1.init_sims(replace=True)
model_hs1_neg0.init_sims(replace=True)
