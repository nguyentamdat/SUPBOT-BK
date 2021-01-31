from pickle import load

class DomainClassifier:
    __instance = None
    __path = ""
    __clf = None

    def predict(self, msg):
        return DomainClassifier.__path + msg

    def __new__(cls):
        if cls.__instance is None:
            print("Creating new instance")
            cls.__instance = super(DomainClassifier, cls).__new__(cls)
        return cls.__instance

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = super(DomainClassifier, cls).__new__(cls)
        return cls.__instance

    @staticmethod
    def set_path(path):
        DomainClassifier.__path = path
        try:
            DomainClassifier.__clf = load(open(path, 'rb'))
        except:
            print("load pickle error")

if __name__ == "__main__":
    DomainClassifier.set_path("/adb/asdf/")
    a = DomainClassifier.instance()
    print(a.predict("ABCSASD"))
