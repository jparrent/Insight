#!/usr/bin/python3

import sys
import os
import logging
import pycurl
import json
import re
import urllib
import pandas as pd
from io import BytesIO
from tqdm import tqdm
import csv
import pickle

_RESTAURANTS_DIR = '../data/restaurants/'
_NUTRITION_DIR = '../data/nutrition/'
_WORD_DIR = '../data/words/'


PY3 = sys.version_info[0] > 2

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

EDAMAM_APP_ID = os.environ['EDAMAM_APP_ID']
EDAMAM_API_KEY = os.environ['EDAMAM_API_KEY']
# EDAMAM_APP_ID = '4292fd2d'
# EDAMAM_API_KEY = '3cc10693855e91977eeb5b0caa7b7b5b'
edamam_url = 'https://api.edamam.com/api/nutrition-data'

allergenLabels = [
    'DAIRY_FREE', 'GLUTEN_FREE', 'WHEAT_FREE', 'EGG_FREE', 'MILK_FREE',
    'PEANUT_FREE', 'TREE_NUT_FREE', 'SOY_FREE', 'FISH_FREE', 'SHELLFISH_FREE',
    'MUSTARD_FREE', 'SESAME_FREE', 'LUPINE_FREE', 'MOLLUSK_FREE'
]

# healthPreference = [
#     'VEGAN', 'VEGETARIAN', 'PESCATARIAN', 'PALEO', 'NO_OIL_ADDED', 'KOSHER'
# ]

antihealthPreference = ['VEGAN', 'VEGETARIAN']


class Test:

    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf


def get_nutrition(item):

    params = {
        'app_id': EDAMAM_APP_ID,
        'app_key': EDAMAM_API_KEY,
        'ingr': '1 large ' + item
    }

    t = Test()
    c = pycurl.Curl()
    c.setopt(c.URL, edamam_url + '?' + urllib.parse.urlencode(params))
    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
    e = BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, e.write)
    c.perform()
    c.close()

    data = e.getvalue()
    data = json.loads(data.decode('utf-8', 'ignore'))
    return data

completed = []
nutrition_data = {}


def completedList(item):
    completed.append(item)
    with open(_RESTAURANTS_DIR + 'menu-item-words-completed.txt', 'w') as wfile:
        for word in completed:
            wfile.write("%s\n" % word)


def completedJSON(dict):
    json.dump(dict, open(_NUTRITION_DIR + 'nutrition_data.json', 'w'),
              sort_keys=True, indent=4)


if os.path.exists(_RESTAURANTS_DIR + 'menu-item-words-completed.txt'):
    with open(_RESTAURANTS_DIR + 'menu-item-words-completed.txt') as rfile:
        completed = rfile.read().splitlines()

if os.path.exists(_NUTRITION_DIR + 'nutrition_data.json'):
    with open(_NUTRITION_DIR + 'nutrition_data.json') as jfile:
        nutrition_data = json.load(jfile)


def build_nutrition_dict_from_menu_items():

    # sentences = []

    # print('Collecting words from menus')
    # with open(_RESTAURANTS_DIR + 'restaurants-w-ids-items.csv') as csvfile:
    #     readcsv = csv.reader(csvfile, delimiter=',')
    #     for row in tqdm(readcsv):
    #         item = row[4].strip()
    #         description = row[5].strip()
    #         sentence = ' '.join([item, description])
    #         sentence = sentence.strip().split()
    #         sentence = list(set(sentence))
    #         sentences.extend(sentence)
    #
    # llist = list(set(sentences))
    # with open(_RESTAURANTS_DIR + 'menu-item-words.txt', 'w') as wfile:
    #     for word in llist:
    #         wfile.write("%s\n" % word)

    with open(_RESTAURANTS_DIR + 'menu-item-words.txt', 'r') as rfile:
        llist = rfile.read().splitlines()

    with open(_WORD_DIR + 'food-search-list.csv') as f:
        fllist = f.readlines()
        fllist = [x.lower().strip('\n') for x in llist]
        fllist = set(llist)
        fllist = list(llist)
        fllist.sort()
        llist.extend(fllist)

    print('Building nutrition dicitonary from menu items')
    for item in tqdm(llist):
        if item not in nutrition_data.keys() and item not in completed:
            print(item)
            try:
                data = get_nutrition(item)
            except JSONDecodeError:
                completedList(item)
                continue
            if len(data["healthLabels"]) == 28 and data["calories"] == 0:
                completedList(item)
                continue
            h_labels = data['healthLabels']
            allergens = [i.lower()
                         for i in allergenLabels if i not in h_labels]
            allergens = [re.sub('_free$', '', i) for i in allergens]
            allergens = [i.replace('tree_nut', 'tree nut') for i in allergens]
            allergens.extend([i.lower() for i in antihealthPreference if i not in h_labels])

            if len(allergens) != 0:
                nutrition_data[item] = allergens
                completedList(item)

        completedJSON(nutrition_data)


build_nutrition_dict_from_menu_items()

pickle.dump(nutrition_data, open(_NUTRITION_DIR + 'nutrition_data.p', 'wb'))
json.dump(nutrition_data, open(_NUTRITION_DIR +
                               'nutrition_data.json', 'w'), sort_keys=True, indent=4)
