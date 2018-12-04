# USAGE
# Start the server:
# 	python run_keras_server.py
# Submit a request via cURL:
# 	curl -X POST -F image=@jemma.png 'http://localhost:5000/predict'
# Submit a request via Python:
#	python simple_request.py 
# Submit a request via browser example
#       http://127.0.0.1:5000/predicturl?url=etcanada.com/news/299494/canadian-tennis-star-eugenie-bouchard-goes-topless-in-sports-illustrated-swimsuit-2018-issue

# import the necessary packages
from threading import Thread
from PIL import Image
from pymongo import MongoClient
from bson.json_util import dumps
from flask import Flask, render_template, request, jsonify
import time
import json
import sys
import io
import os, errno
import requests
import mimetypes
from io import BytesIO
from scraping import Scraping_Image
import mongodb_helper
from mongodb_helper import Mongodb_helper
from flask.templating import render_template
import directory_utils
from redis import Redis
# from rq import Queue

# initialize our Flask application, Redis server, and Keras model
app = Flask(__name__)

mongoclient = None
mongo = None

# q = Queue(connection=Redis())

@app.route("/predict", methods=["POST"])
def predict():
	# /predicturl?url=http://xxx.com/abcnews
	data = {"success": True}
	try:		
		data = json.loads(request.data.decode())
		print('data: ' + request.data.decode())
		website = data["website"]
		folderName = directory_utils.CreateFolderName(website)
		if mongo.Query({"website" : website.strip()}).count() > 0:
			return jsonify(data)
		print('scraping images at: ', website)
		print('folder name: ' + folderName)
# 		result = q.enqueue(process, website)
		scraping = Scraping_Image(website, folderName)
		if scraping.run():
			data = {"success": True}
	except:
		pass
	finally:
		return jsonify(data);

@app.route("/", methods=["GET", "POST"])
def index():
	return render_template('index.html')

def process(website):
	folderName = directory_utils.CreateFolderName(website)
	if mongo.Query({"website" : website.strip()}).count() > 0:
		data = {"success": True}
	else:
		scraping = Scraping_Image(website, folderName)
		if scraping.run():
			data = {"success": True}
			print('finishing')
		
	

@app.route("/result", methods=["POST"])
def get_results():
	data = json.loads(request.data.decode())
	website = data["web"]
	folderName = directory_utils.CreateFolderName(website)
	
	results = mongo.Query({"website" : website}, "result", 10)	
	
	s = dumps(results)
	st = json.loads(s)
	d = []
	if st is not None:
		for x in st:
		    o = {'website' : x['website'], 'result' : x['result'], 'image_name' : x['image_name']}
		    d.append(o)
	return jsonify(d)


# if this is the main thread of execution first load the model and
# then start the server
if __name__ == "__main__":
	# load the function used to classify input images in a *separate*
	# thread than the one used for main classification
	mongo = Mongodb_helper()
	mongo.Drop_DataBase(mongodb_helper.MONGODB_NAME)
	# start the web server
	print("* Starting web service...")
	app.run()
