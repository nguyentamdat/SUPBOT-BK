from itertools import chain
from functools import reduce
from transformers import GPT2Tokenizer
from transformers import PreTrainedTokenizer
from torch.utils.data import DataLoader, Dataset, RandomSampler, SequentialSampler
import pickle
import os
import logging
import re
from sklearn.model_selection import train_test_split
logger = logging.getLogger(__name__)

SPECIAL_TOKENS = ["<bos>", "<eos>", "<speaker1>", "<speaker2>", "<pad>"]
ATTR_TO_SPECIAL_TOKEN = {'bos_token': '<bos>', 'eos_token': '<eos>',
                         'pad_token': '<pad>', 'additional_special_tokens': ['<speaker1>', '<speaker2>']}
MODEL_INPUTS = ["input_ids", "mc_token_ids",
                "lm_labels", "mc_labels", "token_type_ids"]
PADDED_INPUTS = ["input_ids", "lm_labels", "token_type_ids"]
tokenizer = GPT2Tokenizer.from_pretrained(
    args.tokenizer_name, additional_special_tokens=SPECIAL_TOKENS)

history = ["chào bạn", "xin chào"]
reply = "bạn khoẻ không?"
bos, eos, speaker1, speaker2 = "<bos>", "<eos>", "<speaker1>", "<speaker2>"


def average_distributed_scalar(scalar, args):
    """ Average a scalar over the nodes if we are in distributed training. We use this for distributed evaluation. """
    if args.local_rank == -1:
        return scalar
    scalar_t = torch.tensor(scalar, dtype=torch.float,
                            device=args.device) / torch.distributed.get_world_size()
    torch.distributed.all_reduce(scalar_t, op=torch.distributed.ReduceOp.SUM)
    return scalar_t.item()


def pad_dataset(dataset, padding=0):
    """ Pad the dataset. This could be optimized by defining a Dataset class and padding at the batch level, but this is simpler. """
    max_l = max(len(x) for x in dataset["input_ids"])
    for name in PADDED_INPUTS:
        dataset[name] = [x + [padding if name != "lm_labels" else -100]
                         * (max_l - len(x)) for x in dataset[name]]
    return dataset


def add_special_tokens_(model, tokenizer):
    """ Add special tokens to the tokenizer and the model if they have not already been added. """
    orig_num_tokens = len(tokenizer.encoder)
    num_added_tokens = tokenizer.add_special_tokens(
        ATTR_TO_SPECIAL_TOKEN)  # doesn't add if they are already there
    if num_added_tokens > 0:
        model.resize_token_embeddings(
            new_num_tokens=orig_num_tokens + num_added_tokens)


def build_inputs(history, reply, tokenizer):
    # Build our sequence by adding delimiters and concatenating
    reply = tokenizer.tokenize(reply) + [eos]
    history = [tokenizer.tokenize(x) for x in history] + [reply]
    history = [[speaker1 if (len(history) - i) %
                2 else speaker2] + s for i, s in enumerate(history)]
    history[0] = [bos] + history[0]
    sequence = history
    # Build our word, segments and position inputs from the sequence
    words = list(chain(*sequence))                         # word tokens
    segments = [speaker1 if (len(history) - i) % 2 else speaker2             # segment tokens
                for i, s in enumerate(sequence) for _ in s]
    position = list(range(len(words)))                      # position tokens
    return words, segments, position, sequence


def build_data(history, reply, distractor, tokenizer=tokenizer):
    words, segments, positions, sequence = build_inputs(history, reply)
    words_dis, segments_dis, _, _ = build_inputs(history, distractor)

    # build language model target
    lm_targets = ([-1] * sum(len(s) for s in sequence[:-1])) \
        + [-1] + tokenizer.convert_tokens_to_ids(sequence[-1][1:])
    lm_distractor = [-1] * len(words_distractor)

    # store position last token
    last_token = len(words) - 1
    last_token_distractor = len(words_distractor) - 1

    # Now we can pad reply and distractor inputs and targets to the same length
    padding_length = max(len(words), len(words_distractor))

    (words, words_distractor, segments, segments_distractor) = [pad(x, tokenizer.convert_tokens_to_ids(
        '<pad>')) for x in (words, words_distractor, segments, segments_distractor)]

    (lm_targets, lm_distractor) = [pad(x, -1)
                                   for x in (lm_targets, lm_distractor)]

    # And gather reply and distractor inputs to build the input tensors:
    # words tokens
    input_ids = torch.tensor([[words, words_distractor]], dtype=torch.long)
    # segment tokens
    token_type_ids = torch.tensor(
        [[segments, segments_distractor]], dtype=torch.long)
    # Positions tokens can be automatically created by the model as (0, 1, ..., N)
    # Last tokens location
    mc_token_ids = torch.tensor(
        [[last_token, last_token_distractor]], dtype=torch.long)
    # Language modeling labels
    lm_labels = torch.tensor([[lm_targets, lm_distractor]], dtype=torch.long)
    # Next-sentence prediction labels
    # Gold reply is 1st (index 0)
    mc_labels = torch.tensor([0], dtype=torch.long)

    return input_ids, token_type_ids, mc_token_ids, lm_labels, mc_labels


def pad(x, padding):
    return x + [padding] * (padding_length - len(x))


def build_input_from_segments(history, reply, tokenizer, lm_labels=False, with_eos=True):
    """ Build a sequence of input from 3 segments: persona, history and last reply. """
    bos, eos, speaker1, speaker2 = tokenizer.convert_tokens_to_ids(
        SPECIAL_TOKENS[:-1])
    input_ids, token_type_ids, mc_token_ids, lm_labels, mc_labels = build_data(
        history, reply, "", tokenizer)
    instance = {}
    instance["input_ids"] = input_ids
    instance["token_type_ids"] = token_type_ids
    instance["mc_token_ids"] = mc_token_ids
    if lm_labels:
        instance["lm_labels"] = ([-1] * sum(len(s)
                                 for s in sequence[:-1])) + [-1] + sequence[-1][1:]
    else:
        instance["lm_labels"] = lm_labels
    return instance


def get_data_loaders(args, tokenizer):
    """ Prepare the dataset for training and evaluation """
    personachat = get_dataset(tokenizer, args.dataset_path, args.dataset_cache)

    logger.info("Build inputs and labels")
    datasets = {"train": defaultdict(list), "valid": defaultdict(list)}
    for dataset_name, dataset in personachat.items():
        num_candidates = len(dataset[0]["utterances"][0]["candidates"])
        if args.num_candidates > 0 and dataset_name == 'train':
            num_candidates = min(args.num_candidates, num_candidates)
        for dialog in dataset:
            persona = dialog["personality"].copy()
            for _ in range(args.personality_permutations):
                for utterance in dialog["utterances"]:
                    history = utterance["history"][-(2*args.max_history+1):]
                    for j, candidate in enumerate(utterance["candidates"][-num_candidates:]):
                        lm_labels = bool(j == num_candidates-1)
                        instance = build_input_from_segments(
                            persona, history, candidate, tokenizer, lm_labels)
                        for input_name, input_array in instance.items():
                            datasets[dataset_name][input_name].append(
                                input_array)
                    datasets[dataset_name]["mc_labels"].append(
                        num_candidates - 1)
                    datasets[dataset_name]["n_candidates"] = num_candidates
                # permuted personalities
                persona = [persona[-1]] + persona[:-1]

    logger.info("Pad inputs and convert to Tensor")
    tensor_datasets = {"train": [], "valid": []}
    for dataset_name, dataset in datasets.items():
        dataset = pad_dataset(
            dataset, padding=tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS[-1]))
        for input_name in MODEL_INPUTS:
            tensor = torch.tensor(dataset[input_name])
            if input_name != "mc_labels":
                tensor = tensor.view(
                    (-1, datasets[dataset_name]["n_candidates"]) + tensor.shape[1:])
            tensor_datasets[dataset_name].append(tensor)

    logger.info("Build train and validation dataloaders")
    train_dataset, valid_dataset = TensorDataset(
        *tensor_datasets["train"]), TensorDataset(*tensor_datasets["valid"])
    train_sampler = torch.utils.data.distributed.DistributedSampler(
        train_dataset) if args.distributed else None
    valid_sampler = torch.utils.data.distributed.DistributedSampler(
        valid_dataset) if args.distributed else None
    train_loader = DataLoader(train_dataset, sampler=train_sampler,
                              batch_size=args.train_batch_size, shuffle=(not args.distributed))
    valid_loader = DataLoader(valid_dataset, sampler=valid_sampler,
                              batch_size=args.valid_batch_size, shuffle=False)

    logger.info("Train dataset (Batch, Candidates, Seq length): {}".format(
        train_dataset.tensors[0].shape))
    logger.info("Valid dataset (Batch, Candidates, Seq length): {}".format(
        valid_dataset.tensors[0].shape))
    return train_loader, valid_loader, train_sampler, valid_sampler


def _should_skip(line, min_length=9, max_length=127):
    """Whether a line should be skipped depending on the length."""
    return len(line) < min_length or len(line) > max_length


def create_example(previous_lines, line, num_history=3):
    example = {
        'history': previous_lines[-num_history:],
        'reply': line,
    }
    return example


def _preprocess_line(line):
    # line = line.decode("utf-8")

    # Remove the first word if it is followed by colon (speaker names)
    # NOTE: this wont work if the speaker's name has more than one word
    line = re.sub('(?:^|(?:[.!?]\\s))(\\w+):', "", line)

    # Remove anything between brackets (corresponds to acoustic events).
    line = re.sub("[\\[(](.*?)[\\])]", "", line)

    # Strip blanks hyphens and line breaks
    line = line.strip(" -\n")

    return line


class ConversationDataset(Dataset):
    def __init__(self, tokenizer: PreTrainedTokenizer, args, text_files, block_size=512):
        block_size = block_size - \
            (tokenizer.max_len - tokenizer.max_len_single_sentence)
        directory = args.cache_dir
        cached_features_file = os.path.join(
            directory, args.model_type + "_cached_lm_" + str(block_size)
        )
        if os.path.exists(cached_features_file) and not args.overwrite_cache:
            logger.info("Loading features from cached file %s",
                        cached_features_file)
            with open(cached_features_file, "rb") as handle:
                self.examples = pickle.load(handle)
        else:
            logger.info("Creating features from dataset file at %s", directory)

            self.examples = []
            self.f = None
            if (os.path.exists(text_files)):
                with open(text_files) as f:
                    buffer = []
                    for line in f:
                        new_line = _preprocess_line(line)
                        if (_should_skip(new_line)):
                            continue
                        if (len(buffer) >= args.num_history):
                            self.examples.append(create_example(
                                buffer, new_line, args.num_history))
                            # print(self.examples[-1])
                            buffer = buffer[1:]
                        buffer.append(new_line)
            self.train, self.valid = train_test_split(
                self.examples, test_size=0.3, random_state=81)

            # Note that we are loosing the last truncated example here for the sake of simplicity (no padding)
            # If your dataset is small, first you should loook for a bigger one :-) and second you
            # can change this behavior by adding (model specific) padding.

            logger.info("Saving features into cached file %s",
                        cached_features_file)
            with open(cached_features_file, "wb") as handle:
                pickle.dump(self.examples, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, item):
        return torch.tensor(self.examples[item], dtype=torch.long)


class Args():
    def __init__(self):
        self.output_dir = 'output'
        self.model_type = 'gpt2'
        self.model_name_or_path = 'microsoft/DialoGPT-small'
        self.config_name = 'microsoft/DialoGPT-small'
        self.tokenizer_name = 'gpt2-chatbot'
        self.cache_dir = 'cached'
        self.block_size = 512
        self.do_train = True
        self.do_eval = True
        self.evaluate_during_training = False
        self.per_gpu_train_batch_size = 4
        self.per_gpu_eval_batch_size = 4
        self.gradient_accumulation_steps = 1
        self.learning_rate = 5e-5
        self.weight_decay = 0.0
        self.adam_epsilon = 1e-8
        self.max_grad_norm = 1.0
        self.num_train_epochs = 3
        self.max_steps = -1
        self.warmup_steps = 0
        self.logging_steps = 1000
        self.save_steps = 3500
        self.save_total_limit = None
        self.eval_all_checkpoints = False
        self.no_cuda = False
        self.overwrite_output_dir = True
        self.overwrite_cache = True
        self.should_continue = False
        self.seed = 42
        self.local_rank = -1
        self.fp16 = False
        self.fp16_opt_level = 'O1'
        self.num_history = 3


args = Args()


if __name__ == "__main__":
    # ds = ConversationDataset(tokenizer, args, "./vi.txt")
    tokenizer = GPT2Tokenizer.from_pretrained(
        args.tokenizer_name, additional_special_tokens=SPECIAL_TOKENS)
