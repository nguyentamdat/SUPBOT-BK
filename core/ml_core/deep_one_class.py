from tensorflow.keras import models
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import cv2 as cv
from PIL import Image
from tensorflow.keras import preprocessing
from tensorflow.keras import backend as K

image_dir = "./dataset/image/"


class _DeepOneClass():
    instance = None
    def __init__(self):
        self.__clf = models.load_model("./models/image_process", custom_objects={"original_loss": original_loss})
        self.__ms = MinMaxScaler()
        self.load_data()

    def load_data(self):
        self.data = preprocessing.image_dataset_from_directory(image_dir)

def DeepOneClass():
    if _DeepOneClass.instance is None:
        _DeepOneClass.instance = _DeepOneClass()
    return _DeepOneClass.instance

def original_loss(y_true, y_pred):
    lc = 1/(classes*batchsize) * batchsize**2 * K.sum((y_pred -K.mean(y_pred,axis=0))**2,axis=[1]) / ((batchsize-1)**2)
    return lc