import unittest
from unittest import mock
from app import app
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from marshmallow import ValidationError
from flask import jsonify
from flask_mail import Message
from flask_jwt_extended import create_access_token
import json

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.user_data = {
            'name': 'Test User',
            'email': 'testuser@test.com',
            'password': 'testpassword'
        }
        self.login_data = {
            'email': 'testuser@test.com',
            'password': 'testpassword'
        }

    def tearDown(self):
        # db.users.drop()
        pass

    @mock.patch('app.users_collection')
    def test_signup(self, mock_users_collection):
        response = self.app.post('/signup', json=self.user_data)
        # Check that the response status code is 201
        self.assertEqual(response.status_code, 201)
        # Check that the response message is 'User created successfully'
        self.assertEqual(response.json['message'], 'User created successfully')
        



    @mock.patch('app.users_collection')
    def test_login(self, mock_users_collection):
        # Mock the users collection find_one method to return the user_data
        mock_users_collection.find_one.return_value = self.login_data 
        # Mock the create_access_token function to return a dummy token
        with mock.patch('app.create_access_token') as mock_create_access_token:
            mock_create_access_token.return_value = 'dummy_token'
            response = self.app.post('/login', json=self.login_data)
            # Check that the response status code is 200
            self.assertEqual(response.status_code, 200)
            # Check that the response message is 'Logged in successfully'
            self.assertEqual(response.json['message'], 'Logged in successfully')
            # Check that the response access token is the dummy token returned by the mock create_access_token function
            self.assertEqual(response.json['access_token'], 'dummy_token')



    
    @mock.patch('flask_jwt_extended.get_jwt_identity')
    @mock.patch('flask.request')
    @mock.patch('app.task_schema.load')
    @mock.patch('pymongo.collection.Collection.insert_one')
    @mock.patch('flask_mail.Mail.send')
    @mock.patch('app.users_collection.find_one')
    def test_create_task(self, mock_find_one, mock_mail_send, mock_insert_one, mock_task_schema_load, mock_request, mock_get_jwt_identity):
        mock_get_jwt_identity.return_value = 'reporter@example.com'

        mock_request.json = {
            'title': 'Test Task',
            'description': 'Test Description',
            'reporter': {'email': 'reporter@example.com'},
            'assignee': {'email': 'assignee@example.com'}
        }

        mock_task_schema_load.return_value = {
            'title': 'Test Task',
            'description': 'Test Description',
            'reporter': {'email': 'reporter@example.com'},
            'assignee': {'email': 'assignee@example.com'}
        }

        mock_find_one.return_value = {'email': 'assignee@example.com'}

        response = app.test_client().post('/tasks', json=mock_request.json)

        mock_task_schema_load.assert_called_once_with(mock_request.json)
        mock_find_one.assert_called_once_with({'email': 'assignee@example.com'})
        mock_insert_one.assert_called_once_with({
            'title': 'Test Task',
            'description': 'Test Description',
            'reporter': {'email': 'reporter@example.com'},
            'assignee': {'email': 'assignee@example.com'}
        })
        mock_mail_send.assert_called_once()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data), {'task_id': 'mock_task_id', 'message': 'Task created successfully'})







if __name__ == '__main__':
    unittest.main() 
