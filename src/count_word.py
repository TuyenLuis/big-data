from tqdm import tqdm
from pymongo import MongoClient
import pandas as pd

client = MongoClient('localhost', 27017)
db = client['manage_post']
col = db['viblo_posts']

long_vn_word = pd.read_csv('preprocessing/long_vn_word.csv', header=0).values[:, 0]
short_vn_word = pd.read_csv('preprocessing/short_vn_word.csv', header=0).values[:, 0]
en_stopword = pd.read_csv('preprocessing/en_stopword.csv', header=0).values[:, 0]
major_word = pd.read_csv('preprocessing/major_word.csv', header=0).values[:, 0]
not_alphabet_word = pd.read_csv('preprocessing/not_alphabet_word.csv', header=0).values[:, 0]
only_one_letter = pd.read_csv('preprocessing/only_one_letter.csv', header=0).values[:, 0]
other_word = pd.read_csv('preprocessing/other_word.csv', header=0).values[:, 0]
print(short_vn_word)

import re

dict = {}

for i, post in tqdm(enumerate(col.find()), total=col.count()):
    num_long_vn_word = 0
    num_short_vn_word = 0
    num_en_stopword = 0
    num_major_word = 0
    num_not_alphabet_word = 0
    num_only_one_letter = 0
    num_other_word = 0
    try:
        text = post['pp_content']
        sentence_list = text.split()
        for sentence in sentence_list:
            for word in re.split('\s', sentence):
                try:
                    if word in long_vn_word:
                        num_long_vn_word += 1
                    elif word in short_vn_word:
                        num_short_vn_word += 1
                    elif word in en_stopword:
                        num_en_stopword += 1
                    elif word in major_word:
                        num_major_word += 1
                    elif word in not_alphabet_word:
                        num_not_alphabet_word += 1
                    elif word in only_one_letter:
                        num_only_one_letter += 1
                    else:
                        num_other_word += 1
                except KeyError:
                    num_other_word += 1
    except Exception as e:
        print(e)
        continue

    col.update_one({"_id": post["_id"]}, {"$set": {
        "num_long_vn_word": num_long_vn_word,
        "num_short_vn_word": num_short_vn_word,
        "num_en_stopword": num_en_stopword,
        "num_major_word": num_major_word,
        "num_not_alphabet_word": num_not_alphabet_word,
        "num_only_one_letter": num_only_one_letter,
        "num_other_word": num_other_word
    }})

print("Update done")
#
# col1 = db['frequence']
# array = []
# for word in dict:  # split with whitespace
#     try:
#         print(word)
#         print(dict[word])
#         col1.insert_one({
#             'text': word,
#             'total': dict[word]
#         })
#     except KeyError:
#         print()
