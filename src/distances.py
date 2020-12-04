import numpy as np
from scipy.stats import entropy

# https://www.kaggle.com/ktattan/lda-and-document-similarity

# matrix là 1 ma trận doc x topics  => chính là ma trận chứa các từ word ứng với topic nào

#so sánh độ tương tự với từng mẫu trong ma trận documents x topics
def jensen_shannon(query, matrix):
    p = query[None, :].T  # take transpose
    print(p.shape)
    q = matrix.T  # transpose matrix
    print(q.shape)

    m = 0.5 * (p + q)
    return np.sqrt(0.5 * (entropy(p, m) + entropy(q, m)))



# sắp xếp các giá trị khoảng các đã tính ( độ tương đồng)
# khoảng cách càng nhỏ chứng tỏ sự tương đồng phân bố topics giữa 2 documents càng cao
# rồi trả về index của các documents trong cơ sở dữ liệu
def get_most_similar_documents(query, matrix, k=10):
    sims = jensen_shannon(query, matrix)
    return sims.argsort()[:k]
