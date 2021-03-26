from ml_core.abstract_classifier import AbstractClassifier
import torch
from PIL import Image
from torchvision import transforms
import base64
import io
import json
import csv
from collections import OrderedDict
import numpy as np

_FASHION_CLASSES = ["clothing",
                    "hat", "sports equipment"]


class ImageClassifier(AbstractClassifier):
    def classify(self, msg):
        input_batch = self.preprocess_img(self.decode_img(msg))
        if torch.cuda.is_available():
            input_batch = input_batch.to('cuda')
            self.model.to('cuda')
        with torch.no_grad():
            output = self.model(input_batch)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        result = self.get_top5(probabilities)
        categories = self.get_category(result)

        return categories

    def get_top5(self, probabilities):
        with open('./models/image_classes.txt', 'r') as f:
            categories = [s.strip() for s in f.readlines()]
        top5_prob, top5_catid = torch.topk(probabilities, 5)
        result = []
        for i in range(top5_prob.size(0)):
            # print(categories[top5_catid[i]], top5_prob[i].item())
            result.append((categories[top5_catid[i]], top5_prob[i].item()))
        return result

    def get_category(self, list_subcategory):
        cat_to_lab, lab_to_cat = get_categories(
            "./models/imagenet_categories.csv")
        # all_cats = list(cat_to_lab.keys())
        categories = []
        for label, probs in list_subcategory:
            category = lab_to_cat.get(label)
            if category is not None and category not in categories:
                categories.append(category)
        return categories

    def __init__(self):
        self.model = torch.hub.load(
            'pytorch/vision:v0.6.0', 'resnet18', pretrained=True)
        self.model.eval()

    def decode_img(self, msg):
        b64 = msg.split(',')[1]
        msg = base64.b64decode(b64)
        buf = io.BytesIO(msg)
        return Image.open(buf)

    def preprocess_img(self, img):
        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[
                                 0.229, 0.224, 0.225]),
        ])
        return preprocess(img).unsqueeze(0)


class FashionImageClassifier(ImageClassifier):
    def classify(self, msg):
        categories = super().classify(msg)
        print(categories)

        return any([i in _FASHION_CLASSES for i in categories])


def get_categories(filename):
    # Open the file with list of categories and the imagenet classes
    # in each category
    # Return a dictionary of category names to the list of classes in the category
    # and a reverse lookup dictionary

    cat_to_lab = OrderedDict()
    lab_to_cat = OrderedDict()
    with open(filename) as csvfile:
        freader = csv.reader(csvfile)
        rownum = 0
        for row in freader:
            # Skip header row
            if rownum == 0:
                rownum += 1
                continue

            row = np.array(row)
            row = row[row != '']		# get rid of empty cells

            # The category is the first element in the row
            # the rest are the labels in that category
            cat = row[0]
            labs = row[1:]
            assert(1+len(labs) == len(row))

            # Store values in dictionaries if not yet there
            cat_to_lab[cat] = list(labs)
            for l in labs:
                lab_to_cat[l.strip()] = cat

    return cat_to_lab, lab_to_cat
