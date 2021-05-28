from aitextgen import aitextgen
import os

MODEL_PATH = "opensub-gpt"
TOKENIZER_PATH = MODEL_PATH + "/aitextgen.tokenizer.json"


class _TextGenerator:
    instance = None

    def __init__(self):
        print(MODEL_PATH, TOKENIZER_PATH)
        self.ai = aitextgen(model_folder=MODEL_PATH, tokenizer_file=TOKENIZER_PATH)

    def generate_one(self, text, idx):
        try:
            res = self.ai.generate_one(prompt=text + "\n", temperature=1.0, top_p=0.9)
            # print(res)
            return res.split("\n")[idx]
        except:
            return ""



def TextGenerator():
    if _TextGenerator.instance is None:
        _TextGenerator.instance = _TextGenerator()
    return _TextGenerator.instance