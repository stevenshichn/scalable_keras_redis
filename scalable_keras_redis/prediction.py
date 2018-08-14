from classifiers import Alcohol_Model, Gambling_Model
from mongodb_helper import Mongodb_helper
from pymongo import MongoClient
import image_helper
from threading import Thread
import queue

model = Alcohol_Model()
gm_model = Gambling_Model()
# nsfw_model = Nudity_Model()

def Generate_Record(website_folder, image_name, result):
    return {'website' : website_folder, 
            'image_name' : image_name,
            "result" : result}

class Prediction(object):
    def __init__(self, url, image_path, image_name, website_folder, is_slices):
        self.image_path = image_path
        self.image_name = "/static/{0}/{1}".format(website_folder, 'slices/'+image_name if is_slices else image_name)
        self.website_folder = website_folder
        self.url = url
        self.alcohol = model
        self.gambling = gm_model
#         self.nudity = nsfw_model
        self.is_slices = is_slices
        self.mongo_helper = Mongodb_helper()
        self.results = {}
    
    def _thread_func(self, func, image_path, out_queue, label):
        score = func(image_path)
        out_queue.put({label : score})
        
    def predict(self):
        if image_helper.check_image_with_pil(self.image_path):
            out_queue = queue.Queue()
            t1 = Thread(target=self._thread_func, args = (self.alcohol.predict, self.image_path, out_queue, 'alcohol'))
            t2 = Thread(target=self._thread_func, args = (self.gambling.predict, self.image_path, out_queue, 'gambling'))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            dict =  {'alcohol' : 0, 'gambling' : 0}
            max_pred = 0
            need_to_insert = False
            for q in range(out_queue.qsize()):
                for key, value in out_queue.get().items():
                    if key == 'alcohol':
                        dict['alcohol'] = value
                    if key == 'gambling':
                        dict['gambling'] = value
                    if max_pred <= value:
                        max_pred = value
#             nudity_diction = 
            if max_pred >= 0.8:
                record = Generate_Record(self.url, self.image_name, dict)
                self.mongo_helper.Insert_Record(record)
            print('predicted : ' + str(max_pred))
            return max_pred
        return -1;