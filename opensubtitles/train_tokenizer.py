from tokenizers import ByteLevelBPETokenizer
from pathlib import Path

# tokenizer.set_special_tokens(SPECIAL_TOKENS)
# model.set_num_special_tokens(len(SPECIAL_TOKENS))


if __name__ == "__main__":
    SPECIAL_TOKENS = ["<bos>", "<eos>", "<speaker1>", "<speaker2>", "<pad>"]
    paths = [str(x) for x in Path(".").glob("**/*.txt")]
    tokenizer = ByteLevelBPETokenizer()
    tokenizer.train(files=paths, vocab_size=52000, min_frequency=2, special_tokens=SPECIAL_TOKENS)
    tokenizer.save_model("gpt2-chatbot")