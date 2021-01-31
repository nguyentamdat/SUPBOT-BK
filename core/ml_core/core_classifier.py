"""Template singleton class"""

class CoreClassifier(object):
    __instance = None

    def predict(cls, msg):
        pass

    def __new__(cls):
        if cls.__instance is None:
            print("Creating new instance")
            cls.__instance = super(CoreClassifier, cls).__new__(cls)
        return cls.__instance

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = super(CoreClassifier, cls).__new__(cls)
        return cls.__instance
