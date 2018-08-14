from bs4 import BeautifulSoup
import os, errno
import threading
import logging
import requests
import mimetypes
import sys
from directory_utils import Folder_Utils
from prediction import Prediction

class Download_Image(object):
    def __init__(self, html_data, folderName, website, create_folder=False):
        self.folderName = folderName
        self.html_data = html_data
        self.create_folder = create_folder
        self.website = website
    
    def _store_image_func(self, image, url_folderName, folder, links, index):
        try:
            if image is not None:
                if 'http' not in image or 'https' not in image:
                    image = 'http://' + url_folderName + '/' + image
                extension = None
                r2 = requests.get(image, stream = True)
                try:
                    content_type = r2.headers['content-type']
                    extension = mimetypes.guess_extension(content_type)
                except Exception as e:
                    print(e.__str__())
                if (extension is None):
                    extension = '.png'
                image_name = "{0}{1}".format(str(index), extension)
                image_path = os.path.join(folder, image_name)
                with open(image_path, "wb") as f:                    
                    f.write(r2.content)
                    index = index + 1
                prediction = Prediction(self.website, image_path, image_name, url_folderName, False)
                print('image_path : ' + image_path)
                if prediction.predict() >= 0.985:
                    return False
                return True
        except Exception as e:
            print('save image: ' + e.__str__())
            return True
        
    
    def _saveImages(self, url_folderName, folder, links, index):
        try:
            for link in links:
                image = link.get("src")
                alt_tag = link.get("alt")
                srcset_tag = link.get("srcset")
                if image is not None:
                    has_rec = self._store_image_func(image, url_folderName, folder, links, index)
                    if has_rec == False:
                        return False 
                    index +=1
                if alt_tag is not None:
                    has_rec1 = self._store_image_func(alt_tag, url_folderName, folder, links, index)
                    if has_rec1 == False:
                        return has_rec1
                    index += 1
                if srcset_tag is not None:
                    image_arr = srcset_tag.split(',')
                    for im in image_arr:
                        print(im)
                        has_rec2 = self._store_image_func(im.strip().split(' ')[0].split('?')[0], url_folderName, folder, links, index)
                        if has_rec2 == False:
                            return false;
                        index += 1             
            return True    
        except Exception as e:
            logging.exception(e.__str__())
            return True
    
    def downloadImages(self):
        soup = BeautifulSoup(self.html_data, "html.parser")
        index=1
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            folder = os.path.join(dir_path, 'static', self.folderName)
            if self.create_folder:
                dir_helper = Folder_Utils()
                dir_helper.createEmptyFolder(folder)
        except OSError as e:
            logging.exception('OSError ' + e.__traceback__.__str__())
        link_array = soup.find_all('img');
        return self._saveImages(self.folderName, folder, link_array, index)
#         count = len(link_array)
#         first_links = []
#         second_links = []
#         thrid_links = []
#         forth_links = []
#         if count >= 4:
#             quater_num = int(round(count/4))
#             first_links = link_array[:quater_num]
#             second_links = link_array[quater_num : 2*quater_num]
#             thrid_links = link_array[2*quater_num : 3 * quater_num]
#             forth_links = link_array[3 * quater_num :]
#             t1 = threading.Thread(target=self._saveImages, args=(self.folderName, folder, first_links, 1))
#             t2 = threading.Thread(target=self._saveImages, args=(self.folderName, folder, second_links, quater_num + 1))
#             t3 = threading.Thread(target=self._saveImages, args=(self.folderName, folder, thrid_links, 2 * quater_num + 1))
#             t4 = threading.Thread(target=self._saveImages, args =(self.folderName, folder, forth_links, 3 * quater_num + 1))
#             
#             t1.start()
#             t2.start()
#             t3.start()
#             t4.start()
#             
#             t1.join()
#             t2.join()
#             t3.join()
#             t4.join()    
#         else:
#             self._saveImages(self.folderName, folder, link_array, index)
