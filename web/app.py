import os
import logging
import random
from markdownify import markdownify

from flask import Flask, jsonify, render_template, redirect
import numpy as np
import pymongo
import settings
from src.distances import get_most_similar_documents
from src.utils import markdown_to_text, get_random_string
from gensim.utils import simple_preprocess
from flask import request
from bson.objectid import ObjectId


client = pymongo.MongoClient(settings.MONGODB_SETTINGS["host"])
db = client[settings.MONGODB_SETTINGS["db"]]
mongo_col = db[settings.MONGODB_SETTINGS["collection"]]

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "framgia123")

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

def make_texts_corpus(sentences):
    for sentence in sentences:
        yield simple_preprocess(sentence, deacc=True)

# load file models
def load_model():
    import gensim  # noqa
    import joblib  # noqa
    # load LDA model
    lda_model = gensim.models.LdaModel.load(
        settings.PATH_LDA_MODEL
    )
    # load corpus
    corpus = gensim.corpora.MmCorpus(
        settings.PATH_CORPUS
    )
    # load dictionary
    id2word = gensim.corpora.Dictionary.load(
        settings.PATH_DICTIONARY
    )
    # load documents topic distribution matrix
    doc_topic_dist = joblib.load(
        settings.PATH_DOC_TOPIC_DIST
    )
    # doc_topic_dist = np.array([np.array(dist) for dist in doc_topic_dist])

    return lda_model, corpus, id2word, doc_topic_dist


lda_model, corpus, id2word, doc_topic_dist = load_model()



def md2html(md_content):
    import markdown
    md = markdown.Markdown()
    html = md.convert(md_content)
    return html

def get_content_of_post(slug):
    import requests
    fmt_url = 'https://api.viblo.asia/posts/' + slug
    req = requests.get(fmt_url)
    if req.status_code != 200:
        return ''
    data = req.json()['post']
    content = data['data']['contents']
    return content


@app.route('/', methods=["GET"])
@app.route('/posts/', methods=["GET"])
def show_posts():
    # idrss = random.sample(range(0, mongo_col.count()), 10)
    # posts = mongo_col.find({"idrs": {"$in": idrss}})
    current_page = request.args.get('page')
    if current_page == None:
        current_page = 1
    else:
        current_page = int(current_page)
    total_post = mongo_col.count()
    posts = mongo_col.find().sort("title").skip((current_page - 1) * 30).limit(30)
    random_posts = [
        {
            "idrs": post["idrs"],
            "url": post["url"],
            "title": post["title"],
            "slug": post["slug"],
            "id": post["_id"],
            "is_active": post["is_active"]
        }
        for post in posts
    ]
    return render_template('list-post.html', random_posts=random_posts, total_post=total_post, current_page=current_page)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_text = request.form['search']
    else:
        search_text = request.args.get('search')

    print('search text : ', search_text)
    posts = mongo_col.find({
        "title": {
            "$regex": search_text
        }
    }).sort("title").limit(30)
    random_posts = [
        {
            "idrs": post["idrs"],
            "url": post["url"],
            "title": post["title"],
            "slug": post["slug"],
            "id": post["_id"],
            "is_active": post["is_active"]
        }
        for post in posts
    ]
    return render_template('list-post.html', random_posts=random_posts)

    # content = markdown_to_text(search_text)
    # text_corpus = make_texts_corpus([content])
    # bow = id2word.doc2bow(next(text_corpus))
    # doc_distribution = np.array(
    #     [doc_top[1] for doc_top in lda_model.get_document_topics(bow=bow)]
    # )
    # # recommender posts
    # most_sim_ids = list(get_most_similar_documents(
    #     doc_distribution, doc_topic_dist))[1:]

    # most_sim_ids = [int(id_) for id_ in most_sim_ids]
    # posts = mongo_col.find({"idrs": {"$in": most_sim_ids}})
    # related_posts = [
    #                     {
    #                         "url": post["url"],
    #                         "title": post["title"],
    #                         "slug": post["slug"]
    #                     }
    #                     for post in posts
    #                 ][1:]
    # return render_template('search.html',search=related_posts)

@app.route('/posts/<slug>', methods=["GET"])
def show_post(slug):
    main_post = mongo_col.find_one({"slug": slug})
    # md = get_content_of_post(slug)
    main_post = {
        "url": main_post["url"],
        "title": main_post["title"],
        "slug": main_post["slug"],
        "content": md2html(main_post["content"])
    }

    # preprocessing
    content = markdown_to_text(main_post["content"])
    text_corpus = make_texts_corpus([content])
    bow = id2word.doc2bow(next(text_corpus))
    # sử dụng dictionary và LDA model đã train và lưu lại để thu được vector document_dist, ứng với phân bố các topic của document đó
    doc_distribution = np.array(
        [doc_top[1] for doc_top in lda_model.get_document_topics(bow=bow)]
    )

    print("doc_distribution", doc_distribution)

    # recommender posts
    most_sim_ids = list(get_most_similar_documents(
        doc_distribution, doc_topic_dist))[1:]

    most_sim_ids = [int(id_) for id_ in most_sim_ids]
    posts = mongo_col.find({"idrs": {"$in": most_sim_ids}})
    related_posts = [
        {
            "url": post["url"],
            "title": post["title"],
            "slug": post["slug"]
        }
        for post in posts
    ][1:]

    return render_template(
        'index.html', main_post=main_post, posts=related_posts
    )

@app.route('/add', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    is_active = request.form['is_active']
    pp_content = markdown_to_text(content)
    slug = get_random_string(11)
    idrs = mongo_col.count()
    main_post = mongo_col.insert_one({
        'id': '',
        'title': title,
        'slug': slug,
        'url': '',
        'content': markdownify(content),
        'idrs': idrs,
        'pp_content': pp_content,
        'is_active': is_active
    })

    return render_template(
        'index.html', main_post=main_post
    )

@app.route('/update/<id>', methods=['POST'])
def update_post(id):
    title = request.form['title']
    content = request.form['content']
    pp_content = markdown_to_text(content)

    mongo_col.update_one({"_id": id}, {"$set": {
        "title": title,
        "content": content,
        "pp_content": pp_content
    }})

    main_post = mongo_col.find_one({"_id": ObjectId(id)})

    return render_template(
        'index.html', main_post=main_post
    )

@app.route('/delete/<id>', methods=['POST'])
def delete_post(id):
    mongo_col.delete_one({"_id": id})

    return redirect("/posts")


@app.route('/posts/detail/<id>', methods=["GET"])
def get_detail(id):
    post = mongo_col.find_one({"_id": ObjectId(id)})
    if post == None:
        return render_template('post-detail.html', post=None)

    print(md2html(post["content"]))
    post = {
        "url": post["url"],
        "title": str(post["title"]),
        "slug": post["slug"],
        "content": md2html(post["content"]),
        "is_active": post["is_active"],
        "id": post["_id"]
    }

    return render_template('post-detail.html', post=post)


@app.errorhandler(404)
def not_found(e):
    return render_template('not-found.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=False)
