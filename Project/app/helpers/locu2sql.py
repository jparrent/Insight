#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import numpy as np
import pandas as pd

_RESTAURANTS_DIR = '../data/restaurants/'

password = os.environ['LETTUCEEATS_PSQL_PW']
dbname = 'menus'
username = 'jparrent'

engine = create_engine('postgres://%s@localhost/%s' % (username, dbname))
# engine = create_engine('postgres://%s:%s@localhost/%s' % (username, password, dbname))

if not database_exists(engine.url):
    create_database(engine.url)
if database_exists(engine.url):
    print('Database', dbname, 'up and running.')

dfRestwID = pd.read_csv(_RESTAURANTS_DIR + 'restaurants-w-ids-items.csv',
                        names=['restid', 'restname', 'address', 'city', 'itemname', 'description'])
dfRestwID['description'] = dfRestwID['description'].fillna('')
dfRestwID['sentence'] = dfRestwID.itemname.astype(str).str.cat(
    dfRestwID.description.astype(str), sep=' ', na_rep=' ')

print('Loading csv file into restaurantswids table')
dfRestwID.to_sql('restaurantswids', engine, if_exists='replace',
                 index=True, chunksize=10000)
