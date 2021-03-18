from abc import ABC, abstractmethod


class AbstractClassifier(ABC):
    @abstractmethod
    def classify(self, msg):
        pass
