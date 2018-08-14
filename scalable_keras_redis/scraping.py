import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import mimetypes
import os, errno
import argparse
from selenium.webdriver.support.wait import WebDriverWait
from pip.index import Link
import threading
from PIL import Image
import logging
from image_downloader import Download_Image
import image_utils
from multiprocessing import Process
import directory_utils
from directory_utils import Folder_Utils
from sys import platform
import uuid
import shutil
import tempfile

phantomjs_path = ''
if platform == "linux" or platform == "linux2":
    phantomjs_path = os.path.abspath('./tools/linux/phantomjs')
if platform == "win32":
    phantomjs_path = os.path.abspath('./tools/windows/phantomjs.exe')
browser = webdriver.PhantomJS(executable_path=phantomjs_path)

class Scraping_Image(object):
    def __init__(self, url, dest_folder=''):
        self.url = url
        self.dest_folder = dest_folder 
        self.browser = browser       
#         print('browser: ' + str(browser))
    
    def _download(self, data, folderName):
        image_downloader = Download_Image(data, folderName, self.url) 
        return image_downloader.downloadImages()        
    
    def run(self):
        i = 0
        print('run')
        folderName = self.url if self.dest_folder == '' else self.dest_folder
#         if folderName is not None or folderName != '':            
#             if '//' in self.url:
#                 folderName = directory_utils.CreateFolderName(self.url)
#                 self.dest_folder = folderName if self.dest_folder == '' else self.dest_folder
        ###browser = webdriver.PhantomJS("C:/Program Files/Python36/phantomjs-2.1.1-windows/bin/phantomjs.exe")
    #     browser = webdriver.Chrome('./chromedriver.exe')
        
        self.browser.get(self.url)
        print('get source')
        print(self.browser.title)
        self.browser.maximize_window()
        print('maximize window')
        pause = 10
        data=None
        folder=None
        screenshot_name = None
        lastHeight = self.browser.execute_script("return document.body.scrollHeight")
        print(lastHeight)
        try:
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
            data = self.browser.page_source
            dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static')
            folder = os.path.join(dir_path, folderName)
            dir_helper = Folder_Utils()
            dir_helper.createEmptyFolder(folder)
            screenshot_name = str(uuid.uuid4()) + '.png'
            self.browser.get_screenshot_as_file(screenshot_name)
        except Exception as  e:
            print('error in scraping : ' + e.__str__())
            pass
        finally:            
#             self.browser.quit()
            if data is not None and folder is not None and screenshot_name is not None:
                slice_success = image_utils.slice_image(self.url, folderName, os.path.join(folder, "slices"), screenshot_name, 400,400,150) 
                os.remove(screenshot_name)
                if slice_success:
                    if self._download(data, folderName): 
                        return True
                    else:
                        return False
                else:
                    return False
#             t1 = threading.Thread(target=self._download, args=(data, folderName))
#             t2 = threading.Thread(target=image_utils.slice_image, args=(os.path.join(folderName, "slices"), screenshot_name, 300,300,150))
#             t1.start()
#             t2.start()
#             t1.join()
#             t2.join()
            
            return True
#             
# scraping = Scraping_Image('https://www.pexels.com/search/alcohol/', os.path.join('www.pexels.com','1'))
# scraping.run()

