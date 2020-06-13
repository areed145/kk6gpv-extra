#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 18:23:20 2019

@author: areed145
"""

from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/', username='kk6gpv', password='kk6gpv', authSource='admin')

db = client.wx
db.awc.delete_many({})

db = client.iot
db.raw.delete_many({})

db = client.aprs
db.raw.delete_many({'script':'radius'})