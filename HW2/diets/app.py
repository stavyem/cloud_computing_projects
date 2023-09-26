# REST API server code
# It uses Flask to build a RESTful service in Python.

# flask run --port 8000     (or whatever port you want to run on.  if no "--port" option specified, it is port 5000)
# flask will return the IP and port the app is running on
# we installed the packages Flask and flask-restful before writing this program


from flask import Flask  # , jsonify
from flask_restful import Resource, Api, reqparse
from flask import request
from pymongo import MongoClient
import requests
import json

app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API

port = 27017
# client = MongoClient(f"mongodb://localhost:{port}/") # erased line
client = MongoClient(f"mongodb://mongo:{port}/") 
db = client['db']
diet_coll = db['diets']


class DietCollection:
    def change_to_json_format(self, doc):
        json_docs = json.dumps(doc, default=str)
        processed_docs = json.loads(json_docs)
        return processed_docs

    def insert_diet(self, name, cal, sodium, sugar):
        if name in [doc["name"] for doc in diet_coll.find()]:
            return -2  # diet of given name already exists

        diet_coll.insert_one({"name": name,
                              "cal": cal,
                              "sodium": sodium,
                              "sugar": sugar, })
        return 1

    def retrieve_all_diets(self):
        projection = {"_id": 0}
        documents = diet_coll.find({}, projection)
        list_documents = list(documents)
        return self.change_to_json_format(list_documents)

    def retrieve_diet_by_name(self, name):
        projection = {"_id": 0}
        doc = diet_coll.find_one({"name": name}, projection)
        if doc is not None:
            return self.change_to_json_format(doc)
        else:
            return -5  # name does not exist in the collection


diet_collection = DietCollection()


class Diets(Resource):
    global diet_collection

    def post(self):
        request_json_dictionary = request.get_json()
        result = diet_collection.insert_diet(
            request_json_dictionary["name"], request_json_dictionary["cal"],
            request_json_dictionary["sodium"], request_json_dictionary["sugar"])

        if result == -2:   # diet already exists
            return f"Diet with {request_json_dictionary['name']} already exists", 422

        return f"Diet {request_json_dictionary['name']} was created successfully", 201

    def get(self):
        return diet_collection.retrieve_all_diets(), 200


class DietName(Resource):
    global diet_collection

    def get(self, diet_name):
        result = diet_collection.retrieve_diet_by_name(diet_name)
        if result == -5:
            return f"Diet {diet_name} not found", 404
        else:
            return result, 200


api.add_resource(Diets, '/diets')
api.add_resource(DietName, '/diets/<string:diet_name>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
