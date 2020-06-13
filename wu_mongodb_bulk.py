#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 20:36:47 2019

@author: areed145
"""

import dns
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pymongo import MongoClient
import pandas as pd
import time

keys_main = ('station_id', 'station_type', 'observation_time_rfc822',
        'temp_f', 'relative_humidity',
        'wind_dir', 'wind_degrees', 'wind_mph', 'wind_gust_mph',
        'pressure_in', 'dewpoint_f', 'heat_index_f', 'windchill_f',
        'solar_radiation', 'UV', 'precip_1hr_in', 'precip_today_in')
keys_location = ('latitude', 'longitude', 'city', 'state', 'neighborhood','elevation','zip')

def convert(val):
    try:
        val = float(val)
    except:
        pass
    if val == ' ':
        val = None
    return val

def get_current(sid):
    url = 'http://api.wunderground.com/weatherstation/WXCurrentObXML.asp?ID='+sid
    xml = urllib.request.urlopen(url).read()
    tree = ET.fromstring(xml)
    message = dict()
    for key in keys_main:
        message[key] = convert(tree.find(key).text)
    for key in keys_location:
        message[key] = convert(tree.find('location').find(key).text)
    message['observation_time_rfc822'] = pd.to_datetime(message['observation_time_rfc822'])
    message['timestamp'] = datetime.utcnow()
    message['topic'] = 'wx/raw'
    message['elevation'] = convert(message['elevation'][:-2])
    message['ttl'] = datetime.utcnow()
    try:
        raw.insert_one(message)
        print(message)
    except:
        print('duplicate current post')

def get_history(sid, m, d, y):
    url = 'https://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID='+sid+'&day='+str(d)+'&month='+str(m)+'&year='+str(y)+'&graphspan=day&format=XML'
    print(url)
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    req = urllib.request.Request(url, headers=hdr)
    xml = urllib.request.urlopen(req).read()
    tree = ET.fromstring(xml)
    for i in range(len(tree)):
        message = dict()
        for key in keys_main:
            message[key] = convert(tree[i].find(key).text)
        for key in keys_location:
            message[key] = convert(tree[i].find('location').find(key).text)
        message['observation_time_rfc822'] = pd.to_datetime(message['observation_time_rfc822'])
        message['timestamp'] = datetime.utcnow()
        message['topic'] = 'wx/raw'
        message['elevation'] = convert(message['elevation'][:-2])
        try:
            raw.insert_one(message)
            print(message)
        except:
            print('duplicate history post')

if __name__ == '__main__':
    # MongoDB client
    #client=MongoClient('mongodb+srv://kk6gpv:ObqL7MKu4IrEvgyE@cluster0-li5mj.gcp.mongodb.net/test?retryWrites=true')
    client = MongoClient('mongodb://localhost:27017/', username='kk6gpv', password='kk6gpv', authSource='admin')
    db=client.wx
    raw=db.raw

    #sid = 'KTXHOUST1886'
    #sid = 'KTXHOUST686'
    #sid = 'KTXHOUST1930'
    #sid = 'KTXHOUST2624'
    sid = 'KTXHOUST1941'
    for m in range(9,11):
        for d in range(1,31):
            success = False
            while success == False:
                try:
                    get_history(sid, m, d, 2019)
                    success = True
                except:
                    print('sleeping')
                    time.sleep(5)
