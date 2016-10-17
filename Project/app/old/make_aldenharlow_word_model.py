#!/usr/bin/python3

import sys
import logging
import pycurl
import json
import re
from gensim.models import word2vec
from io import BytesIO

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

LOCU_API_TOKEN = '814d9f0f42d99a626430d193089eec7808e64bfe'
locu_url = 'https://api.locu.com/v2/venue/search'

locu_query_data = json.dumps({
    "api_key": LOCU_API_TOKEN,
    "fields": ["name", "menus"],
    "venue_queries": [
        {
            "name": "alden & harlow"
            # "menus": {"$present": "false"}
        }
    ]
})

PY3 = sys.version_info[0] > 2


class Test:

    def __init__(self):
        self.contents = ''
        if PY3:
            self.contents = self.contents.encode('ascii')

    def body_callback(self, buf):
        self.contents = self.contents + buf


sys.stderr.write("Testing %s\n" % pycurl.version)

t = Test()
c = pycurl.Curl()
c.setopt(c.URL, locu_url)
c.setopt(pycurl.HTTPHEADER, [
         'X-Postmark-Server-Token: LOCU_API_TOKEN', 'Accept: application/json'])
c.setopt(pycurl.POST, 1)
c.setopt(pycurl.POSTFIELDS, locu_query_data)
c.setopt(c.WRITEFUNCTION, t.body_callback)
c.perform()
c.close()

body = json.loads(t.contents.decode('utf-8'))

menu_data = body["venues"][0]["menus"]

# data = [{'currency_symbol': '$',
#       'menu_name': 'Menu',
#       'sections': [{'section_name': 'dinner\u200f',
#         'subsections': [{'contents': [{'description': '60-degree egg, walnuts, hot colatura & garlic dip',
#             'name': 'crispy baby bok choy',
#             'price': '14',
#             'type': 'ITEM'},
#            {'description': 'grilled oregano, roasted sunchoke, squid ink',
#             'name': 'octopus panzanella',
#             'price': '16',
#             'type': 'ITEM'},

menu_items = menu_data[0]['sections'][0]['subsections'][0]['contents']

# menu_items = [{'description': '60-degree egg, walnuts, hot colatura & garlic dip',
#   'name': 'crispy baby bok choy',
#   'price': '14',
#   'type': 'ITEM'},
#  {'description': 'grilled oregano, roasted sunchoke, squid ink',
#   'name': 'octopus panzanella',
#   'price': '16',
#   'type': 'ITEM'},

sentences = []

for item in menu_items:

    name = item['name']
    name = re.sub('\s*[^a-zA-Z0-9\'\.]\s*', ' ', name)
    sentence_head = ' '.join(['the ingredients for', name, 'are'])

    description = item['description']
    description = re.sub('\s*[^a-zA-Z0-9\'\.\,]\s*', ' ', description)
    description = description.split(',')
    sentence_tail = ' and'.join(description)

    item_soup = ' '.join([sentence_head, sentence_tail])
    sentence = item_soup.split()
    sentences.append(sentence)

# sentences = [[...], ['the', 'ingredients', 'for', 'smoked', 'lamb', 'belly',
# 'ribs', 'are', 'carrot', 'cashew', 'tahini', 'and', 'sour',
# 'orange', 'glaze'], [...]]


# sentences = word2vec.Text8Corpus('text8')
model = word2vec.Word2Vec(sentences, size=200, window=5,
                          min_count=1, workers=1, negative=5, batch_words=40)

# model.doesnt_match("spicy walnut glaze orange".split())
# >> 'orange'

# model.similar_by_word('walnuts')
# >> returns similar words, but not walnuts

# model.save('/tmp/mymodel')
# new_model = gensim.models.Word2Vec.load('/tmp/mymodel')

model.save('word_models/alden_harlow_size20_mincount1_batchwords40_UniqueWords164')
