from aitextgen import aitextgen
import os
import logging

MODEL_PATH = "202107112355final"
TOKENIZER_PATH = MODEL_PATH + "/aitextgen.tokenizer.json"
VOCAB_FILE = MODEL_PATH + "/aitextgen-vocab.json"
MERGES_FILE = MODEL_PATH + "/aitextgen-merges.txt"


class _TextGenerator:
    instance = None

    def __init__(self):
        # print(MODEL_PATH, TOKENIZER_PATH)
        self.ai = aitextgen(model_folder=MODEL_PATH,
                            tokenizer_file=TOKENIZER_PATH,
                            # vocab_file=VOCAB_FILE, 
                            # merges_file=MERGES_FILE
                            )

    def generate_one(self, text, idx):
        try:
            print(text)
            res = self.ai.generate_one(
                prompt=text + "\n", temperature=0.9, top_p=0.7)
            print(res)
            return res.split("\n")[idx].strip(" -\n")
        except BaseException:
            logging.exception("Generate error")
            return ""


def TextGenerator():
    if _TextGenerator.instance is None:
        _TextGenerator.instance = _TextGenerator()
    return _TextGenerator.instance
