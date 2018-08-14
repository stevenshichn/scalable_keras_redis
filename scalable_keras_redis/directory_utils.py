import os
import logging
import shutil
import uuid

def CreateFolderName(url):
    uid = '/'+str(uuid.uuid4())
    if '//' in url:
        folderName = url.split('//')[1].split('/')[0]
        return folderName + uid
    return url + uid

class Folder_Utils(object):

    def createEmptyFolder(self,directory):
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory, ignore_errors=True)
            os.makedirs(directory)
        except OSError as e:
            logging.exception('OSError ' + e.__str__())