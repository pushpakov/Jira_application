from flask import Flask, request, jsonify
from flask_mail import Mail, Message  
from pymongo import MongoClient
from dotenv import load_dotenv  
import os
from bson.objectid import ObjectId
import json
from datetime import datetime, timedelta
from logs.logger import setup_logger 
from marshmallow import ValidationError
from databases.data_base import *
from databases.data_base import MongoConnection
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager, create_access_token
from validations.validation import UserSchema, TaskSchema, CommentSchema, LoginSchema


# load environment variables from .env file
load_dotenv()

# get environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
DB_NAME = os.getenv('DB_NAME')

USER_COLLECTION = os.getenv('USER_COLLECTION') 
TASK_COLLECTION = os.getenv('TASK_COLLECTION') 
COMMENT_COLLECTION = os.getenv('COMMENT_COLLECTION')  



db = MongoConnection(MONGODB_URI,DB_NAME)  
users_collection = db.get_collection(USER_COLLECTION)

task_collection = db.get_collection(USER_COLLECTION)
comment_collection = db.get_collection(USER_COLLECTION)


# create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here' 



# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'pk.kumar.jiraapp999311'
app.config['MAIL_PASSWORD'] = 'gfcfhersrkellxne'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'pk.kumar.jiraapp999311'
mail = Mail(app)  

# set JWT token location
jwt = JWTManager(app)
jwt.token_location = 'headers'


# initialize Marshmallow schemas
user_schema = UserSchema()
login_schema = LoginSchema() 
task_schema = TaskSchema()
comment_schema = CommentSchema()



logger = setup_logger() 

# @app.route('/signup', methods=['POST'])
def signup():
    # validate request body
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        logger.error(str(e)) 
        return jsonify({'error': str(e)}), 400

    # check if user already exists
    if users_collection.find_one({'email': user_data['email']}):
        return jsonify({'error': 'User with email already exists'}), 409

    # create new user
    users_collection.insert_one(user_data)   

    return jsonify({'message': 'User created successfully', "status_code": 201}), 201



# @app.route('/login', methods=['POST'])
def login():
    # validate request body
    try:
        user_data = login_schema.load(request.json)
        print(user_data)
    except ValidationError as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 400

    # check if user exists and password is correct
    user = users_collection.find_one({'email': user_data['email'], 'password': user_data['password']})
    if not user:
        logger.error('Invalid credentials')
        return jsonify({'error': 'Invalid credentials'}), 401 

    # create a JWT token with a 24-hour expiration time
    access_token = create_access_token(identity=user_data['email'], expires_delta=timedelta(hours=24))

    return jsonify({'access_token': access_token.decode('utf-8'), 'message': 'Logged in successfully'}), 200


