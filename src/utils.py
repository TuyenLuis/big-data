import logging
import re
import random
import string
import pandas

from bs4 import BeautifulSoup
from markdown import markdown
from pyvi import ViTokenizer

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO


# lấy các stopwords vào mảng để so sánh
with open(r"F:\Project\Recommender_System_LDA_Viblo\data\vni_stopwords.txt",encoding="utf8") as f:
    stopwords = []
    for line in f:
        stopwords.append("_".join(line.strip().split()))


# xử lí các kí tự tags
def preprocessing_tags(soup, tags=None):
    if tags is not None:
        for tag in tags:
            for sample in soup.find_all(tag):
                sample.replaceWith('')
    else:
        raise NotImplementedError("Tags must be set!")

    return soup.get_text()


# convert markdown -> html -> text
# xóa words có trong stopwords  không mamng nhiều ý nghĩa
def markdown_to_text(markdown_string, parser="html.parser",
                     tags=['pre', 'code', 'a', 'img', 'i']):
    """ Converts a markdown string to plaintext
    https://stackoverflow.com/questions/18453176
    """

    import mistune  # noqa
    # md -> html -> text since BeautifulSoup can extract text cleanly
    markdown = mistune.Markdown()
    html = markdown(markdown_string)

    soup = BeautifulSoup(html, parser)
    # remove code snippets
    text = preprocessing_tags(soup, tags)

    text = remove_links_content(text)
    text = remove_emails(text)
    text = remove_punctuation(text)
    text = text.replace('\n', ' ')
    text = remove_numeric(text)
    text = remove_multiple_space(text)
    text = text.lower().strip()

    #dùng thuật toán tách từ của pyvi để tách các từ trong text
    text = ViTokenizer.tokenize(text)
    text = remove_stopwords(text, stopwords=stopwords)

    return text

# xóa các email
def remove_emails(text):
    return re.sub(r'\S*@\S*\s?', '', text)

# xóa các dấu xuống dòng -> space
def remove_newline_characters(text):
    return re.sub(r'\s+', ' ', text)

# xóa các đường dẫn có trong text
def remove_links_content(text):
    text = re.sub(r"http\S+", "", text)
    return text

# đổi nhiều dấu space thành 1 dấu space
def remove_multiple_space(text):
    return re.sub(r"\s\s+", " ", text)

# xóa các kí tự đặc biệt
def remove_punctuation(text):
    """https://stackoverflow.com/a/37221663"""
    import string  # noqa
    table = str.maketrans({key: None for key in string.punctuation})
    return text.translate(table)

# xóa số
def remove_numeric(text):
    import string  # noqa
    table = str.maketrans({key: None for key in string.digits})
    return text.translate(table)

# xóa các thẻ tags trong text
def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

# lọc ra các từ có nghĩa trong đoạn text
def remove_stopwords(text, stopwords):
    return " ".join([word for word in text.split() if word not in stopwords])

# random slug - for add new post
def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

