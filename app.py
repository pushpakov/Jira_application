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
# from databases.data_base import MongoConnection
from flask_jwt_extended import jwt_required, get_jwt_identity, JWTManager, create_access_token
from validations.validation import UserSchema, TaskSchema, CommentSchema, LoginSchema



from services.users import *

# connect to the MongoDB server
client = MongoClient("mongodb://localhost:27017")

# get a reference to the 'mydatabase' database
db = client["jiraDB"] 

# get a reference to the 'users' collection
task_collection = db["tasks"]

comment_collection = db["comments"] 


 
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
task_schema = TaskSchema()
comment_schema = CommentSchema()



logger = setup_logger() 

@app.route('/signup', methods=['POST'])
def signup_router():
     return signup() 



@app.route('/login', methods=['POST'])
def login_route(): 
     return login()
    


@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    try:
        token_data = get_jwt_identity()  
        
        # add the logged in user as the reporter
        task_data = task_schema.load(request.json) 
        # task_data['reporter'] = token_data 
        reporter_email = task_data['reporter']['email']
        assignee_email = task_data['assignee']['email']


        # check if the assignee exists
        assignee = users_collection.find_one({'email': assignee_email})   
        # print(json.dumps(assignee, indent=4))
        if not assignee:
            logger.error(f'Assignee with mail id {assignee_email} does not exist')
            return jsonify({'error': f'Assignee with mail id {assignee_email} does not exist'}), 400


        # check if the logged in user is the reporter
        if reporter_email != token_data:   
            logger.error('Only reporters can assign tasks')
            return jsonify({'error': 'Only reporters can assign tasks'}), 403

        # create the task
        task_id = task_collection.insert_one(task_data).inserted_id 

        # send an email to the assignee
        if assignee_email != token_data:
             # Create a message instance
            print(assignee_email)
            msg = Message('Task Assignment', recipients=[assignee_email])

            # Set the message body
            msg.body = f'You have been assigned a task. Please log in to your account to view it.'

            # Send the message
            mail.send(msg)  

        return jsonify({'task_id': str(task_id), 'message': 'Task created successfully'}), 201

    except ValidationError as e:
        logger.error(str(e))
        return jsonify({'error': str(e)}), 400





# Create a new comment
@app.route('/tasks/<task_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(task_id):
    # Validate the request body
    try:
        token_data = get_jwt_identity()  
        data = comment_schema.load(request.json)

    except ValidationError as e:
        return jsonify({'error': str(e)}), 400

    # Check if the task exists
    task = task_collection.find_one({'_id': ObjectId(task_id)})
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    


    # Check if the user exists
    user = users_collection.find_one({'email': token_data})    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    reporter_email = task['reporter']['email']
    assignee_email = task['assignee']['email'] 


    if reporter_email == token_data: 
         # Create a message instance
            print(assignee_email)
            msg = Message('Task Assignment', recipients=[assignee_email])

            # Set the message body
            msg.body = f'You have been assigned a task. Please log in to your account to view it.'

            # Send the message
            mail.send(msg)  
    
    elif assignee_email == token_data:
        # Create a message instance
            # print(assignee_email)
            msg = Message('Task Assignment', recipients=[reporter_email])

            # Set the message body
            msg.body = f'You have been assigned a task. Please log in to your account to view it.'

            # Send the message
            mail.send(msg)  

    else:  
        # Create a message instance
            # print(assignee_email)
            msg = Message('Task Assignment', recipients=[token_data]) 

            # Set the message body
            msg.body = f'You have been assigned a task. Please log in to your account to view it.'

            # Send the message
            mail.send(msg)  
    
    # Create the comment
    comment = {
        'task': task,  
        'author': {"name":data['author']['name'],
                   "email": data['author']['email']
                   },   
        'content': data['content'] 
    }

    # Insert the comment into the database
    try:
        result = comment_collection.insert_one(comment)
        print(result) 
        comment['_id'] = result.inserted_id 
        return jsonify(comment_schema.dump(comment)), 201 
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# to view own and others task 
@app.route('/users/<email>/tasks', methods=['GET'])
@jwt_required()
def get_user_tasks(email):
    # Get the user's assigned and reported tasks
    tasks = task_collection.find({
        '$or': [
            {'assignee_email': email},
            {'reporter_email': email}
        ]
    })
    
    # Return the result
    result = task_schema.dump(tasks, many=True)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5003)


