from ml_core.domain_classifier import *
from state_tracker import GeneralStateTracker
import requests as req
import json
from ml_core.image_classifier import *
from ml_core.qa_system import QAAgent
from underthesea import pos_tag
from ml_core.deep_one_class import DeepOneClass

config_domain = ["NhaKhoaClassifier", "BanHangClassifier"]
config = {
    "THRESHOLD": 0.80
}
TAGSET = {
    "pronoun": "P"
};

class ChatbotService:
    __instance = None
    __THRESHOLD = config.get("THRESHOLD")

    def __init__(self):
        if ChatbotService.__instance is not None:
            raise Exception("Singleton class")
        else:
            ChatbotService.__instance = self
            self.initialize()

    def get_instance():
        if ChatbotService.__instance is None:
            ChatbotService()
        return ChatbotService.__instance

    def initialize(self):
        __cls = {}
        for domain in config_domain:
            __cls[domain] = globals()[domain]()
        self.__cls = __cls
        self.__states = {}
        # self.__qa = QAAgent()
        self.__doc = DeepOneClass()

    def score_domains(self, msg, threshold):
        res = {}
        for domain in self.__cls:
            score = self.__cls[domain].classify(msg)
            print(domain, score)
            if score > threshold:
                res[domain] = score
        return res

    def domain_recognize(self, msg):
        res = self.score_domains(msg, self.__THRESHOLD)
        if res == {}:
            return "default"
        else:
            return max(res, key=res.get)

    def receive(self, id, msg):
        res = {"domain": "default", "action": "default", "intent": "default"}
        state = self.__states.get(id, GeneralStateTracker(id))

        current_domain = state.get_domain()

        tags = [x[1] for x in pos_tag(msg)]
        isQuestion = any([(TAGSET["pronoun"] == x) for x in tags])
        res["isQuestion"] = isQuestion

        print("Before state", state)
        if current_domain == "default":
            domain = self.domain_recognize(msg)
            print(domain)
            if domain != "default":
                state.__domain = domain
                state.next_action = "connect"
                res["action"] = "connect"
                res["domain"] = domain
                res["intent"] = "connect"
        state.add_state(msg)
        print("After state", state)

        self.__states[id] = state

        return res

    def receive_image(self, base64):
        img_cls = FashionImageClassifier()
        isFashion = img_cls.classify(base64)
        res = {}
        res["domain"] = "Image"
        res["action"] = isFashion
        res["intent"] = "image_class"
        # if isFashion:
        #     payload = {"image": base64, "user": "master", "type": "image"}
        #     r = req.post(TMT_ENDPOINT, json=payload)
        #     data = r.json()
        #     print(data)

        return res

    def ask(self, question):
        try:
            result = self.__qa.get_answer(question)
        except:
            result = ["", "Câu hỏi này khó quá!!!", ""]

        return result


if __name__ == "__main__":
    service = ChatbotService.get_instance()
    res = service.domain_recognize("Hi")
    print(res)
