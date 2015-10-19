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
        
        # [Ben-G] You should also be dropping the user collection and creating
        # a new user for each test case. This removes the dependency of your
        # test on previous state. That's important so that each test can verify the 
        # code it is testing independently.
        
        #db.drop_collection('users')
        db.drop_collection('trips')

    # Trip tests
    def test_posting_trip(self):
        # [Ben-G] At some point in future you should pass the an authorization header with 
        # username and password as part of this request
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
                creator="123456789",
                waypoints=[
                    dict(
                        name="place",
                        lat="1234",
                        long="4321"),
                    dict(
                        name="place",
                        lat="1234",
                        long="4321")]
            )),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'trip' in responseJSON["name"]
        assert '123456789' in responseJSON["creator"]
        waypoints_test = [
            dict(
                name="place",
                lat="1234",
                long="4321"),
            dict(
                name="place",
                lat="1234",
                long="4321")]
        self.assertEqual(waypoints_test, responseJSON["waypoints"])

    def test_getting_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
                creator="123456789",
                waypoints=[
                    dict(
                        name="place",
                        lat="1234",
                        long="4321"),
                    dict(
                        name="place",
                        lat="1234",
                        long="4321")]
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'trip' in responseJSON["name"]
        assert '123456789' in responseJSON["creator"]
        waypoints_test = [
            dict(
                name="place",
                lat="1234",
                long="4321"),
            dict(
                name="place",
                lat="1234",
                long="4321")]
        self.assertEqual(waypoints_test, responseJSON["waypoints"])

    def test_updating_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
                creator="123456789",
                waypoints=[
                    dict(
                        name="place",
                        lat="1234",
                        long="4321"),
                    dict(
                        name="place",
                        lat="1234",
                        long="4321")]
            )),
            content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        # putting new stuff
        response = self.app.put(
            '/trips/'+postedObjectID,
            data=json.dumps(dict(
                name="test",
                creator="123456789",
                waypoints=[
                    dict(
                        name="test",
                        lat="4321",
                        long="1234"),
                    dict(
                        name="test",
                        lat="4321",
                        long="1234")]
            )),
            content_type='application/json')

        newResponseJSON = json.loads(response.data.decode())
        newObjectID = newResponseJSON["_id"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(newObjectID, postedObjectID)
        assert 'application/json' in response.content_type
        assert 'test' in newResponseJSON["name"]
        waypoints_test = [
            dict(
                name="test",
                lat="4321",
                long="1234"),
            dict(
                name="test",
                lat="4321",
                long="1234")]
        self.assertEqual(waypoints_test, newResponseJSON["waypoints"])

    def test_deleting_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
                creator="123456789",
                waypoints=[
                    dict(
                        name="place",
                        lat="1234",
                        long="4321"),
                    dict(
                        name="place",
                        lat="1234",
                        long="4321")]
            )),
            content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.delete('/trips/'+postedObjectID)

        self.assertEqual(response.status_code, 204)

    # User tests
    def test_posting_user(self):
        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name="JOSH",
                password="test"
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
                name="JOSHY",
                password="test"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/users/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'JOSHY' in responseJSON["name"]

    # [Ben-G] You can rmove the MyObject tests, they were only meant
    # as starting point for your project

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
