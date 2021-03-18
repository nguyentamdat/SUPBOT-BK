from core.ml_core.abstract_classifier import AbstractClassifier
import joblib


class DomainClassifier(AbstractClassifier):
    __path = ""
    __cls = None

    def classify(self, msg):
        return self.__cls.predict_proba([msg])[0][1]

    def __init__(self, path: str):
        self.__path = path
        self.initialize()

    def initialize(self):
        self.__cls = joblib.load(self.__path)


class NhaKhoaClassifier(DomainClassifier):
    def __init__(self):
        super().__init__("../models/svm_nhakhoa.joblib")


class BanHangClassifier(DomainClassifier):
    def __init__(self):
        super().__init__("../models/svm_banhang.joblib")


if __name__ == "__main__":
    cls = NhaKhoaClassifier()
    print(cls.classify("Hello"))
