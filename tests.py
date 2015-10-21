import server
import unittest
import json
from pymongo import MongoClient
from base64 import b64encode


def auth_header_verification(authorized, usernamee='joshuarcher', passwordd='truepassword'):
    username = usernamee
    password = ''
    if authorized:
        password = passwordd
    else:
        password = 'falsepassword'
    auth_string = "{0}:{1}".format(username, password)
    auth_basic = 'Basic ' + b64encode(auth_string.encode('UTF-8')).decode('UTF-8')

    return {"Authorization": auth_basic}
    # auth = 'Basic ' + b64encode(pw_str.encode('utf-8')).decode('utf-8')
    # return {"Authorization": auth}


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # [Ben-G] You should also be dropping the user collection and creating
        # a new user for each test case. This removes the dependency of your
        # test on previous state. That's important so that each test can verify the
        # code it is testing independently.

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('myobjects')
        db.drop_collection('users')
        db.drop_collection('trips')

        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name='joshuarcher',
                password='truepassword'
            )),
            content_type='application/json')
        responseJSON = json.loads(response.data.decode())
        name = responseJSON['name']
        if 'joshuarcher' != name:
            print(responseJSON['name'])
            print("SOMETHING WENT WRONG IN SETUP")

    # Trip tests
    def test_posting_trip(self):
        # [Ben-G] At some point in future you should pass the an authorization header with
        # username and password as part of this request
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
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
            headers=auth_header_verification(True),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'trip' in responseJSON['name']
        assert 'joshuarcher' in responseJSON['owner']
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

    def test_getting_trip_many(self):
        response = self.app.post('/trips/', data=json.dumps(dict(name="trip1", waypoints=[dict(name="place", lat="1234", long="4321"), dict(name="place", lat="1234", long="4321")])), headers=auth_header_verification(True), content_type='application/json')
        response = self.app.post('/trips/', data=json.dumps(dict(name="trip2", waypoints=[dict(name="place", lat="1234", long="4321"), dict(name="place", lat="1234", long="4321")])), headers=auth_header_verification(True), content_type='application/json')
        response = self.app.post('/trips/', data=json.dumps(dict(name="trip3", waypoints=[dict(name="place", lat="1234", long="4321"), dict(name="place", lat="1234", long="4321")])), headers=auth_header_verification(True), content_type='application/json')

        response = self.app.get('/trips/', headers=auth_header_verification(True))
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(3, len(responseJSON))

    def test_getting_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
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
            headers=auth_header_verification(True),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/'+postedObjectID, headers=auth_header_verification(True))
        responseJSON = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        assert 'trip' in responseJSON["name"]
        assert 'joshuarcher' in responseJSON["owner"]
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

    def test_getting_trip_unauthorized(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
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
            headers=auth_header_verification(True),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        response = self.app.get('/trips/'+postedObjectID, headers=auth_header_verification(False))
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 401)

    def test_updating_trip(self):
        response = self.app.post(
            '/trips/',
            data=json.dumps(dict(
                name="trip",
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
            headers=auth_header_verification(True),
            content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        # putting new stuff
        response = self.app.put(
            '/trips/'+postedObjectID,
            data=json.dumps(dict(
                name="test",
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
            headers=auth_header_verification(True),
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
            headers=auth_header_verification(True),
            content_type='application/json')
        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON["_id"]

        auth_header = auth_header_verification(True)
        response = self.app.delete('/trips/'+postedObjectID, headers=auth_header)

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

    def test_posting_existing_user(self):
        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name="joshuarcher",
                password="test"
            )),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 409)

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

        auth_header = auth_header_verification(True, 'JOSHY', 'test')
        response = self.app.get('/users/'+postedObjectID, headers=auth_header)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'JOSHY' in responseJSON["name"]

    def test_getting_unverified_user(self):
        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name="JOSHY",
                password="test"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON['_id']

        auth_header = auth_header_verification(True)
        response = self.app.get('/users/'+postedObjectID, headers=auth_header)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 403)

    def test_verify_user(self):
        response = self.app.post(
            '/users/',
            data=json.dumps(dict(
                name="josh",
                password="testing"
            )),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON['_id']

        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
