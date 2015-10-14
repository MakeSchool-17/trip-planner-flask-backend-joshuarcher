import server
import unittest
import json
from pymongo import MongoClient


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('myobjects')
        db.drop_collection('users')

    # Trip tests
    def test_posting_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
                waypoints=[
                    "456N,466E",
                    "456N,445E"]
            )),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'trip' in responseJSON["name"]
        self.assertEqual(["456N,466E", "456N,445E"], responseJSON["waypoints"])

    def test_getting_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
                waypoints=[
                    "456N,466E",
                    "456N,445E"]
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'trip' in responseJSON["name"]
        self.assertEqual(["456N,466E", "456N,445E"], responseJSON["waypoints"])

    # User tests
    def test_posting_user(self):
        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name="JOSH"
            )),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'JOSH' in responseJSON["name"]

    def test_getting_user(self):
        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name="JOSHY"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/users/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'JOSHY' in responseJSON["name"]

    # MyObject tests
    def test_posting_myobject(self):
        response = self.app.post(
            '/myobject/',
            data=json.dumps(dict(
                name="A object"
            )),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'A object' in responseJSON["name"]

    def test_getting_object(self):
        response = self.app.post(
            '/myobject/',
            data=json.dumps(dict(
                name="Another object"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/myobject/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Another object' in responseJSON["name"]

    def test_getting_non_existent_object(self):
        response = self.app.get('/myobject/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
