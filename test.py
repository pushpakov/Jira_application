import mongomock
import unittest
import app

class SignupTestCase(unittest.TestCase):
    def setUp(self):
        # create a mock database
        self.mock_client = mongomock.MongoClient()
        app.users_collection = self.mock_client['jiraDB']['users']

        # create a test app
        app.app.config['TESTING'] = True
        app.app.config['JWT_SECRET_KEY'] = 'test-secret'
        self.app = app.app.test_client()

    def tearDown(self):
        # clean up mock database
        self.mock_client.drop_database('jiraDB')

    def test_signup(self):
        # define test data
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'test-password'
        }

        # send POST request to signup endpoint
        response = self.app.post('/signup', json=test_data)

        # check response status code and message
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['message'], 'User created successfully')

        # check user is inserted into mock database
        inserted_user = app.users_collection.find_one({'email': test_data['email']})
        self.assertIsNotNone(inserted_user)
        self.assertEqual(inserted_user['name'], test_data['name'])
        self.assertEqual(inserted_user['password'], test_data['password'])



if __name__ == '__main__':
    unittest.main() 
