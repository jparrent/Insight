#!/usr/bin/python3

from flask import render_template
from flask import request, redirect
from app import app
from app.RankRest import RankIt
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import numpy as np
import csv
from gensim.models import word2vec
import os
import sys
import inspect
import pickle

# postgres -D /usr/local/var/postgres
# \.run.py
# psql --username=jparrent
# \connect menus


def get_cities():

    cities = pd.read_html(
        'https://simple.wikipedia.org/wiki/List_of_United_States_cities_by_population')

    cities_list = [city for city in cities[0][1][1:]]
    states_list = [state for state in cities[0][2][1:]]
    cities_states_list = [(city, state) for city, state in zip(cities_list, states_list)]
    cities_states_list.sort()
    return cities_states_list

current_dir = os.path.join(os.getcwd(), 'app')

model_fp = os.path.join(
    current_dir, 'model/wordmodel_allmenus_sept25_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod')
model_hs1_fp = os.path.join(
    current_dir, 'model/wordmodel_allmenus_hs1_sept25_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod')
model_hs1_neg0_fp = os.path.join(
    current_dir, 'model/wordmodel_allmenus_hs1_neg0_sept25_size300_window10_mincount20_workers4_batchwords40_sample1em3.mod')

model = word2vec.Word2Vec.load(model_fp)
model_hs1 = word2vec.Word2Vec.load(model_hs1_fp)
model_hs1_neg0 = word2vec.Word2Vec.load(model_hs1_neg0_fp)

nutrition_data_file_name = 'data/nutrition/nutrition_data.p'
nutrition_file = os.path.join(current_dir, nutrition_data_file_name)
nutrition_data = pickle.load(open(nutrition_file, 'rb'))

user = 'jparrent'
host = 'localhost'
dbname = 'menus'
db = create_engine('postgres://%s@%s/%s' % (user, host, dbname))
con = None
con = psycopg2.connect(database=dbname, user=user)


@app.route('/')
@app.route('/index')
@app.route('/home')
def lettuceEats():
    cities_states_list = get_cities()
    return render_template("index.html", cities_states_list=cities_states_list)


@app.route('/results')
def results():

    cities_states_list = get_cities()

    allergens = []
    big8 = []

    formData = request.values if request.method == "POST" else request.values
    formData = [item for item in formData.items(multi=True)]

    for item in formData:
        if item[0] == 'city':
            city = item[1]
        elif item[0] == 'allergens':
            allergens.extend(item[1].replace(',', '').split())
        else:
            big8.append(item[1])

    sql_query = "select restid, restname, address, sentence from restaurantswids where city='" + city + "';"
    query_results = pd.read_sql_query(sql_query, con)
    # query_results = query_results[query_results.sentence.notnull()]

    scores, all_allergens = RankIt(query_results, model, model_hs1,
                                   model_hs1_neg0, allergens, nutrition_data, big8)

    return render_template('index.html', scores=scores, all_allergens=all_allergens, scroll='results', cities_states_list=cities_states_list)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")
