#!/usr/bin/python3

import sys
import logging
import pycurl
import json
import re
import urllib
# import html5lib
import pandas as pd
# from io import StringIO
from io import BytesIO
from tqdm import tqdm
import csv

_WORD_DIR = '../data/words/'
_NUTRITION_DIR = '../data/nutrition/'

PY3 = sys.version_info[0] > 2

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

EDAMAM_APP_ID = '4292fd2d'
EDAMAM_API_KEY = '3cc10693855e91977eeb5b0caa7b7b5b'
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

# FOODFACTS_API_TOKE = ''
# foodfacts_url = ''


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


def get_food_items_list():

    food_items = []
    remove_from_list = []

    with open(_WORD_DIR + 'food-search-list.csv') as f:
        food_items = f.readlines()
        food_items = [x.lower().strip('\n') for x in food_items]
        food_items = set(food_items)
        food_items = list(food_items)
        food_items.sort()

    print('Cleaning food items list')
    for item in tqdm(food_items):
        data = get_nutrition(item)
        if len(data["healthLabels"]) == 28 and data["calories"] == 0:
            remove_from_list.append(item)

    food_items = [i for i in food_items if i not in remove_from_list]
    food_items = set(food_items)
    food_items = list(food_items)
    food_items.sort()

    df = pd.DataFrame(food_items)
    df.to_csv(_WORD_DIR + 'food-search-list.txt', index=False, header=False)

    return food_items


def build_bag_of_words_from_nutrition(sentences, item):

    data = get_nutrition(item)
    h_labels = data['healthLabels']

    allergens = [i.lower() for i in allergenLabels if i not in h_labels]
    allergens = [re.sub('_free$', '', i) for i in allergens]
    allergens = [i.replace('tree_nut', 'nut') for i in allergens]
    allergens.extend([i.lower() for i in antihealthPreference if i not in h_labels])

    # unfavored = [i.lower() for i in healthPreference if i not in h_labels]

    # creates ['dairy', 'milk']
    if len(allergens) != 0:
        allergens.insert(0, item)
        sentences.append(allergens)

    return sentences


def build_bag_of_words():

    sentences = []

    food_items = get_food_items_list()

    print('Creating sentences for food items')
    for item in tqdm(food_items):

        sentences = build_bag_of_words_from_nutrition(sentences, item)

    csvfile = open(_NUTRITION_DIR + 'nutrition-sentences.csv', 'w')
    writer = csv.writer(csvfile)
    for sentence in sentences:
        writer.writerow(sentence)
    csvfile.close()

build_bag_of_words()
