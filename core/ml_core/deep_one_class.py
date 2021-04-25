from tensorflow.keras import models
import numpy as np
import cv2 as cv
from PIL import Image
from tensorflow.keras import preprocessing
from tensorflow.keras import backend as K
import tensorflow as tf
import base64
import io
import joblib

# import tensorflow_datasets as tfds

input_shape = (96, 96, 3)
classes = 20
batchsize = 4
ENCODER_PATH = "./models/encoder-image"
LOF_PATH = "./models/localoutlinerfactor.joblib"
MMS_PATH = "./models/minmaxscaler.joblib"


class _DeepOneClass:
    instance = None

    def __init__(self):
        self.load_model()

    def load_model(self):
        self.__encoder = models.load_model(
            ENCODER_PATH, custom_objects={"original_loss": original_loss}
        )
        self.__ms = joblib.load(MMS_PATH)
        # data = (
        #     preprocessing.image_dataset_from_directory(
        #         image_dir,
        #         label_mode="int",
        #         image_size=input_shape[:2],
        #         batch_size=batchsize,
        #     )
        #     .map(normalize_img, tf.data.experimental.AUTOTUNE)
        #     .map(resize_img, tf.data.experimental.AUTOTUNE)
        #     .map(get_x, tf.data.experimental.AUTOTUNE)
        #     .cache()
        #     .prefetch(tf.data.experimental.AUTOTUNE)
        # )
        # train_data = self.__ms.fit_transform(self.__encoder.predict(data))
        self.__clf = joblib.load(LOF_PATH)

    def predict(self, image):
        image = decode_img(image)
        image = resize(image)
        feature = self.__encoder.predict(np.array([image]))
        feature = feature.reshape((len(feature), -1))
        feature = self.__ms.transform(feature)
        return self.__clf._decision_function(feature)


def DeepOneClass():
    if _DeepOneClass.instance is None:
        _DeepOneClass.instance = _DeepOneClass()
    return _DeepOneClass.instance


def original_loss(y_true, y_pred):
    lc = (
        1
        / (classes * batchsize)
        * batchsize ** 2
        * K.sum((y_pred - K.mean(y_pred, axis=0)) ** 2, axis=[1])
        / ((batchsize - 1) ** 2)
    )
    return lc


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32`."""
    return tf.cast(image, tf.float32) / 255.0, label


def resize_img(image, label):
    """Resize image to input shape"""
    return tf.image.resize(image, input_shape[:2]), label


def map_label(image, label):
    """remap label for target"""
    return image, tf.one_hot(label, classes)


def get_x(image, label):
    return image


def resize(image):
    return cv.resize(image, input_shape[:2]) / 255.0


def decode_img(msg):
    b64 = msg.split(",")[1]
    msg = base64.b64decode(b64)
    buf = io.BytesIO(msg)
    return np.array(Image.open(buf))