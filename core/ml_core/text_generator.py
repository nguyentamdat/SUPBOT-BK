from aitextgen import aitextgen

MODEL_PATH = "models/trained_model"
TOKENIZER_PATH = "models/aitextgen.tokenizer.json"


class _TextGenerator:
    instance = None

    def __init__(self):
        self.ai = aitextgen(model_folder="models/trained_model", tokenizer_file="models/aitextgen.tokenizer.json")

    def generate_response(self, text):
        res = self.ai.generate_one(prompt=text + "\n")
        return res.split("\n")[1]


def TextGenerator():
    if _TextGenerator.instance is None:
        _TextGenerator.instance = _TextGenerator()
    return _TextGenerator.instance