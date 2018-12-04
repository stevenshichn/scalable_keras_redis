import traceback
from PIL import Image, ExifTags
from keras.models import model_from_json
import numpy as np
import tensorflow as tf
from scipy.misc import imresize
import os

IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
model_file_path = 'alcohol_cnn.h5'
model_weight_file_path = './alcohol_model/model_vgg16.h5'
model_json_file_path = './alcohol_model/model_vgg16.json'


BUCKET_NAME = 'image-recognition-models'
MODEL_FILE_NAME = model_weight_file_path
MODEL_JSON_FILE_NAME = model_json_file_path

def rotate_by_exif(image):
    try :
        for orientation in ExifTags.TAGS.keys() :
            if ExifTags.TAGS[orientation]=='Orientation' : break
        exif=dict(image._getexif().items())
        if not orientation in exif:
            return image

        if   exif[orientation] == 3 :
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6 :
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8 :
            image=image.rotate(90, expand=True)
        return image
    except:
        return image

class Pred_Model_Base(object):
    def __init__(self):
        self.data = None
        self.graph = tf.get_default_graph()
        self.model = None
    
    def load_model(self, json_file, model_weight_file):
        with open(json_file, encoding='utf-8') as weight_file:
            self.data = weight_file.read()
        self.model = model_from_json(self.data)
        self.model.load_weights(model_weight_file)
    
    def _ml_predict(self, image):
        prediction = -1
        with self.graph.as_default():
            # Add a dimension for the batch
            if self.model is not None:
                prediction = self.model.predict(image[None, :, :, :])
        return prediction
    
    def predict_image(self, image):
#         image = rotate_by_exif(image) # current rotate function is so stable
        resized_image = imresize(image, (224, 224)) / 255.0
    
        # Model input shape = (224,224,3)
        # [0:3] - Take only the first 3 RGB channels and drop ALPHA 4th channel in case this is a PNG
        try:
            pred = self._ml_predict(resized_image[:, :, 0:3])
            prediction = np.float64(pred.take(0, axis=0)[0])
            return float('%.5f' % prediction)
        except:
            return 0        
    
    def predict(self, image_path):
        image = Image.open(image_path)
        return self.predict_image(image)
        

class Alcohol_Model(Pred_Model_Base):
    
    def __init__(self):
        Pred_Model_Base.__init__(self)
        json_file='./alcohol_model/model_vgg16.json'
        model_weight_file = './alcohol_model/model_vgg16.h5'
        self.load_model(json_file, model_weight_file)

class Gambling_Model(Pred_Model_Base):
    
    def __init__(self):
        Pred_Model_Base.__init__(self)
        json_file='./gambling_model/model_vgg16_gambling_v3.json'
        model_weight_file = './gambling_model/model_vgg16_gambling_v3.h5'
        self.load_model(json_file, model_weight_file)