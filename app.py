from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
import re
import os
# from flask_wtf import FlaskForm
# from wtforms import StringField, DecimalField, BooleanField, SubmitField, FieldList

# uncomment this to supply variables from `config.py` file
# it will only work on local machine.
# from config import config

# use `heroku local` command to run the app
# environment variables are supplied from `.env` file
config = os.environ

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_PASSWORD = config["DB_PASSWORD"]
DB_NAME = config["DB_NAME"]
DB_USER = config["DB_USER"]
DB_CLUSTERNAME = config["DB_CLUSTERNAME"]
DB_URI = "mongodb+srv://"+DB_USER+":"+DB_PASSWORD+"@"+DB_CLUSTERNAME+".ovnng.mongodb.net/"+DB_NAME+"?retryWrites=true&w=majority"

app.config["MONGO_URI"] = DB_URI

mongo = PyMongo(app)

# Function to validate URL 
# using regular expression 
def isValidURL(str):

	# Regex to check valid URL 
	regex = ("((http|https)://)(www.)?" +
			"[a-zA-Z0-9@:%._\\+~#?&//=]" +
			"{2,256}\\.[a-z]" +
			"{2,6}\\b([-a-zA-Z0-9@:%" +
			"._\\+~#?&//=]*)")
	
	# Compile the ReGex
	p = re.compile(regex)

	# If the string is empty 
	# return false
	if (str == None):
		return False

	# Return if the string 
	# matched the ReGex
	if(re.search(p, str)):
		return True
	else:
		return False

@app.route('/')
def form():
    return render_template('base.html')

@app.route('/', methods=['POST'])
def form_post():
    # get form input as dictionary
    a = request.form.to_dict()
    # extract image URIs
    images = a["imageURI"].split(';')
    image_list = []
    # validate URIs and put them into list
    for image in images:
        if(isValidURL(image.strip())):
            image_list.append(image.strip())
    # replace imageURI string with image_list in input dictionary
    a["imageURI"] = image_list
    # generate custom ID for document
    id  = mongo.db.config["METADATA_COLLNAME"].count_documents(filter={}) + 1
    id_str = mongo.db.config["METADATA_COLLNAME"].find().sort({'_id':-1}).limit(1)
    a["_id"] = id
    print(id_str)
    # insert document
    data = mongo.db.config["METADATA_COLLNAME"].insert_one(a)
    # print the ID of the inserted document
    return render_template('output.html', doc_id=data.inserted_id)
    # return "your ID is: " + str(data.inserted_id)

@app.route('/metadata', methods=['GET', 'POST', 'PUT'])
def get_metadata():
    if request.method == 'GET':
        doc_id = int(request.args['id'])
    elif request.method == 'POST'or 'POST':
        doc_id = int(request.get_json()['id'])
    data = mongo.db.config["METADATA_COLLNAME"].find_one(filter={'_id' : doc_id})
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
