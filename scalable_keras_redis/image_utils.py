import sys
from PIL import Image
import logging
import os
from directory_utils import Folder_Utils
from threading import Thread, Lock, current_thread
from prediction import Prediction

def check_image_with_pil(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True

def slice_image(url, website, dest_folder, image_file, height, width, step):
    dir_helper = Folder_Utils()
    lock = Lock()
    dir_helper.createEmptyFolder(dest_folder)
    im = Image.open(image_file)
    imgwidth, imgheight = im.size;
    count1 = [0]
    count2 = [0]
    if height > imgheight or width > imgwidth:
        try:
            im.save(os.path.join(dest_folder, "sliced.png"))
        except Exception as e:
            logging.exception(e.__str__())
        finally:
            return
    x_stop = imgwidth - width
    print('slicing')
    y_stop = imgheight - height
    half_y_stop = int(round(y_stop / 2))
    yes = crop_image(im, url, website, count1, dest_folder, width, height, x_stop, half_y_stop, step, 0)
    if yes:
        crop_image(im, url, website, count2, dest_folder, width, height, x_stop, y_stop, step, half_y_stop)
    

#     t1 = Thread(name="t1", target=crop_image, args=(im, website, count1, dest_folder, width, height, x_stop, half_y_stop, step, 0, lock))
#     t2 = Thread(name="t2", target=crop_image, args=(im, website, count2, dest_folder, width, height, x_stop, y_stop, step, half_y_stop, lock))
#     t1.start()
#     t2.start()
#     t1.join()
#     t2.join()
#     
#     for filename in glob.glob(dest_folder+"/**/*.*", recursive=True):
#             print("filename : ",filename)
#             predict = Prediction(os.path.join(dest_folder, filename), dest_folder, website, True)
#             if predict.predict() >= 0.985:
#                 break
    
    print('slicing finished, total {0}'.format(count1[0] + count2[0]))

def _crop_image_helper(im, url, website, box, dest_folder, count, name = "0"):
    try:
        count_value = count[0]     
        a = im.crop(box)
        count_value =count_value + 1
        file_name = "sliced-IMG-{0}-{1}.png".format(name, count_value)
        file_path = os.path.join(dest_folder, file_name)          
        a.save(file_path)
        predict = Prediction(url, file_path, file_name, website, True)
        count[0] = count_value
        if predict.predict() >= 0.92:
            return False
        return True
    except Exception as e:
        logging.exception(e.__str__())
        return True
    
def crop_image(im, url, website, count, dest_folder, target_width, target_height, x_stop, y_stop, step, start_y = 0, lock = None):
    for j in range(start_y, y_stop, step):
        for i in range(0, x_stop, step):        
            box = (i, j, target_width+i, target_height+j)
            if lock is not None:
                with lock:
                    if _crop_image_helper(im, url, website, box, dest_folder, count, current_thread().getName()) == False:
                        need_to_stop = True
                        return False       
            else:
                if _crop_image_helper(im, url, website, box, dest_folder, count) == False:
                    need_to_stop = True
                    return False
    return True
# slice_image("test", "etcanada.com/news/299494/canadian-tennis-star-eugenie-bouchard-goes-topless-in-sports-illustrated-swimsuit-2018-issue/26.png", 100, 100, 50)  