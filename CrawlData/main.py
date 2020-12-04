# %%
import requests
from time import sleep

from tqdm import tqdm
import pymongo
from pymongo import MongoClient
import logging

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO
fmt_url = 'https://api.viblo.asia/posts?page={}'
client = MongoClient('localhost', 27017)
db = client['manage_post']
col = db['viblo_posts']
page = 1
# crawldata từ api về mongodb
# while page < 1000:
#     try:
#         req = requests.get(fmt_url.format(page))
#         if req.status_code != 200:
#             break
#         data = req.json()['data']
#         for post in data:
#             col.insert_one({
#                 'id': post['id'],
#                 'title': post['title'],
#                 'slug': post['slug'],
#                 'url': post['url'],
#                 'content': post['contents']
#             })
#
#         page += 1
#         sleep(0.1)
#
#         if page % 50 == 0:
#             print("page: ",page)
#             # print("col count: ")
#             # print(col.count())
#     except Exception as e:
#         print("error:")
#         print(e)
#         continue
#ls
#%%
from src.utils import markdown_to_text

posts = col.find()

type(posts)
for i, post in enumerate(posts):
    print(post['url'])
    if i == 10:
        break
posts = col.find()
test_post = next(posts)
raaw_content = test_post['content']
print(raaw_content)
content = markdown_to_text(raaw_content)
print(content)
test_post['_id']
for i, post in tqdm(enumerate(col.find()), total=col.count()):
    try:
        col.update_one({"_id": post["_id"]}, {"$set": {"idrs": i}})
        pp_content = markdown_to_text(post['content'])
        col.update_one({"_id": post["_id"]}, {"$set": {"pp_content": pp_content}})
    except Exception as e:
        print(e)
        continue
client = MongoClient('localhost', 27017)
db = client['manage_post']
col = db['viblo_posts']

posts = col.find()
test_post = next(posts)
test_post['pp_content']

# %%
import itertools

import gensim
from gensim.utils import simple_preprocess


# %%
def make_sentences():
    for post in col.find():
        yield post['pp_content']


# %%
# 2 hàm để thực hiện hỗ trợ việc fetch dữ liệu theo iterable object thay vì là 1 mảng (list hoặc numpy array) có trong gensim
def make_texts_corpus(sentences):
    for sentence in sentences:
        yield simple_preprocess(sentence, deacc=True)

class StreamCorpus(object):
    def __init__(self, sentences, dictionary, clip_docs=None):
        """
        Parse the first `clip_docs` documents
        Yield each document in turn, as a list of tokens.
        """
        self.sentences = sentences
        self.dictionary = dictionary
        self.clip_docs = clip_docs

    def __iter__(self):
        for tokens in itertools.islice(make_texts_corpus(self.sentences),
                                       self.clip_docs):
            yield self.dictionary.doc2bow(tokens)

    def __len__(self):
        return self.clip_docs

# %%
import sys

sys.path
# %%
sentences = make_sentences()
sentences = make_texts_corpus(sentences)
id2word = gensim.corpora.Dictionary(sentences)
id2word.filter_extremes(no_below=10, no_above=0.25)
id2word.compactify()

#map giữa index với từ .
id2word.save('F:/Project/Recommender_System_LDA_Viblo/models/id2word.dict')
len(id2word)
# %%
for i in range(10):
    print(id2word[i])
# %%
sentences = make_sentences()
sentences = make_texts_corpus(sentences)
print(next(sentences))
# %%
sentences = make_sentences()
cospus = StreamCorpus(sentences, id2word)

# save corpus
# map giữ index với tần số của từ
gensim.corpora.MmCorpus.serialize('F:/Project/Recommender_System_LDA_Viblo/models/corpus.mm', cospus)
# %%
corpus = gensim.corpora.MmCorpus('F:/Project/Recommender_System_LDA_Viblo/models/corpus.mm')
# %%
# số topic = 64 , quy định ma trận documents x topics tương ứng 64 chiều.
lda_model = gensim.models.ldamodel.LdaModel(corpus, id2word=id2word, num_topics=64, passes=10,
                                            chunksize=100, random_state=42, alpha=1e-2, eta=0.5e-2,
                                            minimum_probability=0.0, per_word_topics=False)
# %%
# save lda.model để sử dụng, mỗi 1 topic có các words với xác suất xuất hiện của nó .
lda_model.save('F:/Project/Recommender_System_LDA_Viblo/models/LDA.model')
lda_model.print_topics(10)

# %%
# thực hiện tính toán ma trận documents x topics rồi lưu vào file doc_topic_dist.dat
import numpy as np


doc_topic_dist = np.array(
    [[tup[1] for tup in lst] for lst in lda_model[corpus]]
)
# %%
doc_topic_dist.shape
# %%
import joblib

# %%
joblib.dump(doc_topic_dist, 'F:/Project/Recommender_System_LDA_Viblo/models/doc_topic_dist.dat')
# %%
