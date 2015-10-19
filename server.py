from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
from bcrypt import hashpw, gensalt
# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
app.bcrypt_rounds = 12
api = Api(app)


class Trip(Resource):

    def post(self):
        new_trip = request.json
        trip_collection = app.db.trips
        result = trip_collection.insert_one(new_trip)

        trip = trip_collection.find_one({"_id": ObjectId(result.inserted_id)})

        return trip

    def get(self, trip_id=None):
        if trip_id is None:
            word = {"josh": "archer"}
            response = jsonify(data=[word])
            response.status_code = 404
            return response
        else:
            trip_collection = app.db.trips
            trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
            if trip is None:
                response = jsonify(data=[])
                response.status_code = 404
                return response
            else:
                return trip



    def put(self, trip_id):
        updated_trip = request.json
        trip_collection = app.db.trips

        old_trip = trip_collection.find_one({"_id": ObjectId(trip_id)})

        old_trip["name"] = updated_trip["name"]
        old_trip["waypoints"] = updated_trip["waypoints"]

        return old_trip

    def delete(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.delete_many({"_id": ObjectId(trip_id)})

        if trip.deleted_count is 1:
            response = jsonify(data=[])
            response.status_code = 204
            return response
        else:
            response = jsonify(data=[])
            response.status_code = 304
            return response


#Implement resource
class User(Resource):

    def post(self):
        new_user = request.json
        # hash password
        user_pass = new_user["password"]
        new_user['password'] = hash_pass(user_pass)
        user_collection = app.db.users
        result = user_collection.insert_one(new_user)

        user = user_collection.find_one({"_id": ObjectId(result.inserted_id)})
        del user['password']
        # print(user, type(user))

        return user

    def get(self, user_id):
        user_collection = app.db.users
        user = user_collection.find_one({"_id": ObjectId(user_id)})

        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            del user['password']
            return user


# Implement REST Resource
class MyObject(Resource):

    def post(self):
        new_myobject = request.json
        myobject_collection = app.db.myobjects
        result = myobject_collection.insert_one(new_myobject)

        myobject = myobject_collection.find_one({"_id": ObjectId(result.inserted_id)})

        return myobject

    def get(self, myobject_id):
        myobject_collection = app.db.myobjects
        myobject = myobject_collection.find_one({"_id": ObjectId(myobject_id)})

        if myobject is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return myobject

# Add REST resource to API
api.add_resource(Trip, '/trips/', '/trips/<string:trip_id>')
# api.add_resource(Trip, '/trips/', '/trips/<string:trip_id>', '/trips/byuser/<string:user_id>')
api.add_resource(User, '/users/', '/users/<string:user_id>')
api.add_resource(MyObject, '/myobject/', '/myobject/<string:myobject_id>')


def hash_pass(password):
    encoded_pass = password.encode(encoding='UTF-8', errors='strict')
    return hashpw(encoded_pass, gensalt(app.bcrypt_rounds))


# User Auth code
def check_auth(username, password):
    user_collection = app.db.users
    user = user_collection.find_one({'username': username})
    if user is None:
        return False
    db_password = user['password']
    hashed_pass = hash_pass(password)

    return hashed_pass == db_password


def requires_auth(f):
    @wraps
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {'error': 'Basic Auth Required'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        return f(*args, **kwargs)
    return decorated


# provide a custom JSON serializer for flask_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
