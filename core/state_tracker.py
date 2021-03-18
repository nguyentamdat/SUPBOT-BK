from abc import ABC, abstractmethod

class StateTracker(ABC):
    @abstractmethod
    def get_next_action(self):
        pass

    @abstractmethod
    def add_state(self):
        pass


class GeneralStateTracker(StateTracker):
    def __init__(self, id):
        self.__state = []
        self.next_action = ""
        self.__domain = "default"
        self.__id = id

    def get_next_action(self):
        return self.next_action

    def add_state(self, msg):
        self.__state.append(msg)

    def get_domain(self):
        return self.__domain

    def __str__(self):
        return self.__state.__str__() + " " + self.next_action + " " + " " + self.__domain + " " + self.__id
