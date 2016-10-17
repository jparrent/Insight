#!/usr/bin/python3

import sys
import logging
import pycurl
import json
import re
import urllib
# import html5lib
# from gensim.models import word2vec
import pandas as pd
# from io import StringIO
from io import BytesIO
from tqdm import tqdm


YUMMLY_APP_ID = '0f3a50a4'
YUMMLY_API_KEY = '9e0617c119a0168cf90d8f3729b31620'
yummly_url = 'http://api.yummly.com/v1/api/recipe/'

# http://api.yummly.com/v1/api/recipe/Avocado-cream-pasta-sauce-recipe-306039?_app_id=ID&_app_key=KEY

# item = 'Avocado-cream-pasta-sauce-recipe-306039'

PY3 = sys.version_info[0] > 2

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class Test:

    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf


def get_recipe(item):

    params = {
        '_app_id': YUMMLY_APP_ID,
        '_app_key': YUMMLY_API_KEY,
    }

# The base url for the Search Recipes GET is
# http://api.yummly.com/v1/api/recipes?_app_id=app-id&_app_key=app-key&your
# _search_parameters

    t = Test()
    c = pycurl.Curl()
    c.setopt(c.URL, yummly_url + '?' + urllib.parse.urlencode(params) + urllib.parse.urlencode(item))
    c.setopt(pycurl.HTTPHEADER, ['Accept: application/json'])
    e = BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, e.write)
    c.perform()
    c.close()

    data = e.getvalue()
    data = json.loads(data.decode('utf-8', 'ignore'))
    return data


data = get_recipe(item)

ingr_list = data['ingrdientLines']
