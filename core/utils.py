import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from functools import *
from sklearn.neighbors import KNeighborsClassifier


class Utils:
    def __init__(self):
        self.cls = KNeighborsClassifier()
        self.init_data()

    def init_data(self):
        with open("./train.json") as f:
            data_json = json.load(f)
        self.data = data_json["data"]
        self.contexts = self.preprocess_context()
        self.titles = self.preprocess_title()

        self.idx_context = reduce(
            lambda x, y: x + y, [[i] * len(x["qas"]) for i, x in enumerate(self.contexts)], [])

        self.idx_paragraph = reduce(
            lambda x, y: x + y, [[i] * len(z["qas"]) for i, z in enumerate(self.titles)], [])

        self.qas = list(reduce(lambda x, y: x + y["qas"], self.titles, []))

        print(len(self.idx_context), len(self.idx_paragraph), len(self.qas))

        self.tfidf_q = TfidfVectorizer()
        q_f = self.tfidf_q.fit_transform(self.qas)
        self.sample = list(zip(self.qas, q_f, self.idx_context, self.idx_paragraph))

        self.knn_cls_c = KNeighborsClassifier()
        self.knn_cls_c.fit(q_f, self.idx_context)
        self.knn_cls_p = KNeighborsClassifier()
        self.knn_cls_p.fit(q_f, self.idx_paragraph)

    def preprocess_title(self):
        data_answers_by_title = []
        for d in self.data:
            contexts = [x["context"] for x in d["paragraphs"]]
            context = " ".join(contexts)
            new_data = {}
            new_data["context"] = context
            qas = list(reduce(lambda x, y: x + list(map(lambda z: z["question"], y)), map(
                lambda z: z["qas"], d["paragraphs"]), []))
            new_data["qas"] = qas
            new_data["title"] = d["title"]
            data_answers_by_title.append(new_data)
        return data_answers_by_title

    def preprocess_context(self):
        data_answers_by_context = []
        for d in self.data:
            contexts = [{"title": d["title"], "context": x["context"], "qas": list(
                map(lambda x: x["question"], x["qas"]))} for x in d["paragraphs"]]
            data_answers_by_context.extend(contexts)
        return data_answers_by_context

    def predict_context(self, m):
        idx = self.knn_cls_c.predict(self.tfidf_q.transform([m]))[0]
        return self.contexts[self.sample[idx][2]]

    def predict_paragraph(self, m):
        idx = self.knn_cls_p.predict(self.tfidf_q.transform([m]))[0]
        return self.contexts[self.sample[idx][3]]


if __name__ == "__main__":
    utils = Utils()
    print(utils.predict_context("tại sao không chịu học"))
    print(utils.predict_paragraph("tại sao không chịu học"))
