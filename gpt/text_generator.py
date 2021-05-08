from aitextgen import aitextgen
import os

MODEL_PATH = "trained_model"
TOKENIZER_PATH = "trained_model/aitextgen.tokenizer.json"


class _TextGenerator:
    instance = None

    def __init__(self):
        print(MODEL_PATH, TOKENIZER_PATH)
        self.ai = aitextgen(model_folder=MODEL_PATH, tokenizer_file=TOKENIZER_PATH)

    def generate_one(self, text, idx):
        try:
            res = self.ai.generate_one(prompt=text + "\n", temperature=1.0, top_p=0.9)
            return res.split("\n")[idx]
        except:
            return "Xin lỗi bạn, tôi không biết phải nói gì nữa!"



def TextGenerator():
    if _TextGenerator.instance is None:
        _TextGenerator.instance = _TextGenerator()
    return _TextGenerator.instance