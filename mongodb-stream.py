#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 18:23:20 2019

@author: areed145
"""

from pymongo import MongoClient

client_from = MongoClient(
    'mongodb+srv://kk6gpv:ObqL7MKu4IrEvgyE@cluster0-li5mj.gcp.mongodb.net/test?retryWrites=true')
db_from = client_from.aprs
raw_from = db_from.raw

client_to = MongoClient('mongodb://localhost:27017/', username='kk6gpv', password='kk6gpv', authSource='admin')
db_to = client_to.aprs
raw_to = db_to.raw

raws = list(raw_from.find({}))

# raw_to.insert_many(raws)

len(raws)
skip = 252320

for idx, a in enumerate(raws[skip:]):
   try:
       raw_to.insert_one(a)
       #print(a)
       print('copied - '+str(idx+skip))
   except:
       print('did not copy - '+str(idx+skip))
