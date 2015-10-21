from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
from bcrypt import hashpw, gensalt
from functools import wraps
# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
app.bcrypt_rounds = 12
api = Api(app)


def hash_pass(password, salt=None):
    if salt is None:
        salt = gensalt(app.bcrypt_rounds)
    encoded_pass = password.encode(encoding='UTF-8', errors='strict')
    return hashpw(encoded_pass, salt)


# User Auth code
def check_auth(username, password):
    user_collection = app.db.users
    user = user_collection.find_one({'name': username})
    if user is None:
        return False
    db_password = user['password']
    hashed_pass = hash_pass(password, db_password)

    return hashed_pass == db_password


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {'error': 'Basic Auth Required'}
            resp = jsonify(message)
            resp.status_code = 401
            return resp

        return f(*args, **kwargs)
    return decorated


class Trip(Resource):

    @requires_auth
    def post(self):
        new_trip = request.json
        # set owner to authorized user
        new_trip['owner'] = request.authorization['username']
        trip_collection = app.db.trips
        # insert new trip
        result = trip_collection.insert_one(new_trip)

        trip = trip_collection.find_one({"_id": ObjectId(result.inserted_id)})

        return trip

    @requires_auth
    def get(self, trip_id=None):
        # [TO:DO] This is where I'd want to return list
        # of trips belonging to the authroized user
        trip_collection = app.db.trips
        if trip_id is None:
            trips = trip_collection.find({'owner': request.authorization['username']})
            trips_array = list(trips)
            return trips_array
        else:
            # add owner in query TO:DO
            trip = trip_collection.find_one({"_id": ObjectId(trip_id),
                                            'owner': request.authorization['username']})
            if trip is None:
                # couldn't find the trip user was looking for
                response = jsonify(data=[])
                response.status_code = 404
                return response
            else:
                return trip

    @requires_auth
    def put(self, trip_id):
        updated_trip = request.json
        trip_collection = app.db.trips

        # [Ben-G] I assume this is still work in progress?
        # This should update the existing trip document in the DB
        old_trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        # Check if it's the authorized users trip
        if old_trip['owner'] != request.authorization['username']:
            response = jsonify(data=[])
            response.status_code = 403
            return response

        # Here I'm sending a whole new trip with the put method
        # then I update the trip name and the waypoints
        # by referencing the trip in the request
        old_trip["name"] = updated_trip["name"]
        old_trip["waypoints"] = updated_trip["waypoints"]

        return old_trip

    @requires_auth
    def delete(self, trip_id):
        trip_collection = app.db.trips
        # check if trip exists
        trip = trip_collection.find_one({'_id': ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        # Check if it's the authorized users trip
        if trip['owner'] != request.authorization['username']:
            response = jsonify(data=[])
            response.status_code = 403
            return response
                # check owner TO:DO
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
        # check if user already exists, return 409 if so
        user_collection = app.db.users
        user = user_collection.find_one({'name': new_user['name']})
        if user is not None:
            response = jsonify(data=[])
            response.status_code = 409
            return response
        # hash password
        user_pass = new_user['password']
        new_user['password'] = hash_pass(user_pass)
        user_collection = app.db.users
        result = user_collection.insert_one(new_user)

        user = user_collection.find_one({"_id": ObjectId(result.inserted_id)})
        del user['password']
        # print(user, type(user))

        return user

    @requires_auth
    def get(self, user_id):
        user_collection = app.db.users
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        # Check if it's the authorized user
        if user['name'] != request.authorization['username']:
            response = jsonify(data=[])
            response.status_code = 403
            return response

        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            del user['password']
            return user

# Add REST resource to API
api.add_resource(Trip, '/trips/', '/trips/<string:trip_id>')
# api.add_resource(Trip, '/trips/', '/trips/<string:trip_id>', '/trips/byuser/<string:user_id>')
api.add_resource(User, '/users/', '/users/<string:user_id>')


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
