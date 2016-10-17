#!/usr/bin/python3

import os
import sys
import logging
import re
import pycurl
import json
from tqdm import tqdm
import pandas as pd

_RESTAURANTS_DIR = '../data/restaurants/'
_WORD_DIR = '../data/words/'

PY3 = sys.version_info[0] > 2

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

LOCU_KEY = os.environ['LOCU_KEY']
locu_url = 'https://api.locu.com/v2/venue/search'

dfRestwID = pd.DataFrame(columns=('RestID', 'Name', 'Address',
                                  'City', 'ItemName', 'ItemDescription'))


exclude_menus = [
    '', ' ', 'Wine', 'Reserve', 'Specialty Cocktails', 'Beer', 'Beverages',
    'Drink Specialties', 'After Thoughts', 'Featured Wine', 'Bicchieri',
    'Birre', 'Bianchi Italiani', 'Bianchi Americani', 'Rose', 'Vino Spumante',
    'Cordials', 'Rossi Italiani', 'Rossi Americani', 'Bottled Beer',
    'Stouts & Porters', 'Brown Ales', 'Ales', 'Pale Ales', 'Lights',
    'India Pale Ales', 'Weizens', 'Pilsner', 'Lagers',
    'Belgians & Belgian Styles', 'Belgian White Ales', 'Fruit Beers', 'Ciders',
    'Malt', 'Current Draft List', 'Whites', 'Red', 'Sparkling',
    "Morton's Coffee", 'Italian Coffee', 'Irish Coffee', 'Spanish Coffee',
    'Antioxidant Me', 'Lean and Green', 'Skynny Blood Orange Cosmo',
    'The Red Velvet', 'Skinny Rita', 'Select Beverages', 'Vintage', 'Classic',
    'Sizzle', 'Swizzle, Swirl', 'Rosso', 'Bianco',
    'Champagne & Sparkling Wine​', 'Additional Drinks', 'White Wines',
    'Red Wines', 'Ordering Info', 'Corner cocktails', 'Bottled Beer',
    'Select Origin', 'Origin', 'Artisanal Blends', 'Espresso', 'Certified',
    'Dark Roast', 'Water Process Decaf', 'Samplers', 'Red Wine', 'White Wine',
    'Announcing two new Bar Bites, including: Mini Crab Cake BLTs and Smoked Salmon Pizza!​',
    'Reds', 'Sparklings', 'Beer List', 'House Wines',
]


class Test:

    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf


RestID = 0


def get_exclude_words_list():

    with open(_WORD_DIR + '6K_adverbs.txt') as f:
        excluded_words = f.readlines()
        excluded_words = [x.strip('\n') for x in excluded_words]

    with open(_WORD_DIR + 'food-adjectives-list.txt') as f:
        adjectives = f.readlines()
        adjectives = [x.lower().strip('\n') for x in adjectives]

    with open(_WORD_DIR + 'stop-word-list.txt') as f:
        stopwords = f.readlines()
        stopwords = [x.strip('\n') for x in stopwords]

    excluded_words.extend(adjectives)
    excluded_words.extend(stopwords)
    excluded_words.sort()
    excluded_words = set(excluded_words)
    excluded_words = list(excluded_words)

    return excluded_words


def get_RestID(count):
    count += 1
    return count


def get_restaurants(city):

    locu_query_data = json.dumps({
        "api_key": LOCU_KEY,
        "fields": ["name", "menus", "categories", "location"],
        "venue_queries": [
            {
                "location": {
                    "locality": city
                },
                "menus": {"$present": "true"},
                "categories": {"name": "restaurants"}
            }
        ]
    })

    t = Test()
    c = pycurl.Curl()
    c.setopt(c.URL, locu_url)
    c.setopt(pycurl.HTTPHEADER, [
             'X-Postmark-Server-Token: LOCU_KEY', 'Accept: application/json'])
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.POSTFIELDS, locu_query_data)
    c.setopt(c.WRITEFUNCTION, t.body_callback)
    c.perform()
    c.close()

    data = json.loads(t.contents.decode('utf-8'))
    return data


def stripped(s):
    return "".join(i for i in s if 31 < ord(i) < 127)


def get_cities():

    cities = pd.read_html(
        'https://simple.wikipedia.org/wiki/List_of_United_States_cities_by_population')

    cities_list = [city for city in cities[0][1][1:]]
    return cities_list


def collect_menus_data(RestID, city):

    excluded_words = get_exclude_words_list()
    data = get_restaurants(city)

    venues = data['venues']

    for ven in venues:

        RestID = get_RestID(RestID)
        RestID = int(RestID)
        RestCity = city
        RestName = ven['name'].split('-')[0]
        RestName = re.sub(r'\([^)]*\)*', '', RestName)
        RestName = RestName.replace("`", "'")
        RestName = RestName.strip()
        RestAddress = ven['location']

        try:
            RestStreet = RestAddress['address1'].replace(',', '')
            RestStreet = RestStreet.replace('Locu_none', '')
            RestStreet = re.sub('<[^>]*>', '', RestStreet)
        except KeyError:
            RestStreet = ''

        try:
            RestState = RestAddress['region']
        except KeyError:
            RestState = ''

        try:
            RestZip = RestAddress['postal_code']
        except KeyError:
            RestZip = ''

        try:
            RestAddress = ' '.join([RestStreet, RestCity, RestState, RestZip])
            RestAddress = RestAddress.replace('.', '')
            RestAddress = re.sub(r'\([^)]*\)*', '', RestAddress)
            RestAddress = RestAddress.replace(';', '')
            RestAddress = RestAddress.strip()

        except KeyError:
            RestAddress = ''

        menus = ven['menus']
        num_of_menus = len(menus)

        if num_of_menus == 0:

            continue

        for men in menus:

            for section in men['sections']:

                section_name = stripped(section['section_name'])

                if section_name not in exclude_menus:

                    for subsection in section['subsections']:

                        menu = subsection['contents']

                        for item in menu:

                            try:

                                name = item['name']
                                name = re.sub('\s*[^a-zA-Z\'*\.]\s*', ' ', name)
                                name = name.replace('.', '')
                                name = name.replace('*', '')
                                name = name.lower().strip()
                                name = [w for w in name.split() if w not in excluded_words]
                                name = ' '.join(name)

                            except KeyError:

                                continue

                            try:

                                description = item['description']
                                description = re.sub(
                                    '\s*[^a-zA-Z\'*\.]\s*', ' ', description)
                                description = description.replace('.', '')
                                description = description.lower().strip()
                                description = [w for w in description.split()
                                               if w not in excluded_words]
                                description = ' '.join(description)
                                ItemName, ItemDescription = name, description

                            except KeyError:
                                ItemName = name
                                ItemDescription = ''

                            dfRestwID.loc[len(dfRestwID)] = [RestID, RestName,
                                                             RestAddress, RestCity, ItemName, ItemDescription]

    return RestID


cities_list = get_cities()

for city in tqdm(cities_list):

    collect_menus_data(RestID, city)

    dfRestwID["RestID"] = dfRestwID["RestID"].astype(int)
dfRestwID.to_csv(_RESTAURANTS_DIR + 'restaurants-w-ids-items.csv', index=False)
