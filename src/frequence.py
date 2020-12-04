import sys

from tqdm import tqdm
import pymongo
from pymongo import MongoClient
import logging

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO
fmt_url = 'https://api.viblo.asia/posts?page={}'
client = MongoClient('localhost', 27017)
db = client['rsframgia']
col = db['viblo_posts']
page = 1

text = ""

import re

dict = {}

for i, post in tqdm(enumerate(col.find()), total=col.count()):
    try:
        text = post['pp_content']
        sentence_list = text.split()
        for sentence in sentence_list:
            for word in re.split('\s', sentence):  # split with whitespace
                try:
                    dict[word] += 1
                except KeyError:
                    dict[word] = 1
    except Exception as e:
        print(e)
        continue

# print(dict.keys())
# print(dict.values())
col1 = db['frequence']
array = []
for word in dict:  # split with whitespace
    try:
        print(word)
        print(dict[word])
        col1.insert_one({
            'text': word,
            'total': dict[word]
        })
    except KeyError:
        print()
