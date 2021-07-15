from utils.google_search import GoogleSearch
from utils.relevance_ranking import rel_ranking
from utils.reader import Reader


class _QAAgent:
    instance = None
    def __init__(self):
        self.googlesearch = GoogleSearch()
        self.reader = Reader()

    def get_answer(self, question):
        links, documents = self.googlesearch.search(question)

        passages = rel_ranking(question, documents)

        passages = passages[:20]

        answers = self.reader.getPredictions(question, passages)

        answers = [
            [passages[i], answers[i][0], answers[i][1]] for i in range(0, len(answers))
        ]
        answers = [a for a in answers if a[1] != ""]
        answers.sort(key=lambda x: x[2], reverse=True)

        # print("Final result: ")
        # print("Passage: ", answers[0][0])
        # print("Answer : ", answers[0][1])
        # print("Score  : ", answers[0][2])

        return answers[0] if len(answers) > 0 else ["", "", ""]

def QAAgent():
    if _QAAgent.instance is None:
        _QAAgent.instance = _QAAgent()
    return _QAAgent.instance