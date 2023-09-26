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
dish_coll = db['dishes']
meal_coll = db['meals']
diet_coll = db['diets']

# DishCollection class stores the dishes and perform operations on them


class DishCollection:
    def __init__(self):
        # self.keynum is the number of insert_dish operations performed so far.
        # It will be used to generate unique id's to dishes inserted into collection
        count_doc = dish_coll.count_documents({})
        if count_doc != 0:
            self.keynum = dish_coll.find_one(
                sort=[("ID", -1)])["ID"]
        else:
            self.keynum = 0

    def change_to_json_format(self, doc):
        json_docs = json.dumps(doc, default=str)
        processed_docs = json.loads(json_docs)
        return processed_docs

    def insert_dish(self, i_dish):
        if i_dish in [doc["name"] for doc in dish_coll.find()]:
            return -2  # ID = -2 dish of given name already exists

        self.keynum += 1
        ID = self.keynum
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(
            i_dish)
        response = requests.get(
            api_url, headers={'X-Api-Key': 'rsxmQXdXLGYQXTo27o9WwA==kcPtOo9RsgtVe41K'})

        if response.status_code == requests.codes.ok:
            json_response_list = json.loads(response.text)
            # dish name isn't recognized.
            if len(i_dish.split(" and ")) != len(json_response_list):
                self.keynum -= 1
                return -3

            dish_coll.insert_one(
                {"name": i_dish, "cal": sum([food_dict["calories"] for food_dict in json_response_list]),
                 "size": sum([food_dict["serving_size_g"] for food_dict in json_response_list]),
                 "sodium": sum([food_dict["sodium_mg"] for food_dict in json_response_list]),
                 "sugar": sum([food_dict["sugar_g"] for food_dict in json_response_list]),
                 "ID": ID})
            return ID

        else:
            print("Error, API wasn't reachable")
            self.keynum -= 1
            return -4

    def retrieve_all_dishes(self):
        projection = {"_id": 0}
        documents = dish_coll.find({}, projection)
        list_documents = list(documents)
        return self.change_to_json_format(list_documents)

    def retrieve_dish_by_id(self, ID):
        projection = {"_id": 0}
        doc = dish_coll.find_one({"ID": ID}, projection)
        if doc is not None:  # the ID exists in collection
            return self.change_to_json_format(doc)
        else:
            return -5  # the ID does not exist in the collection

    def delete_dish_by_id(self, ID):
        doc = dish_coll.find_one({"ID": ID})
        if doc is not None:
            dish_list = ["appetizer", "main", "dessert"]
            for dish_type in dish_list:
                meal_coll.update_many({dish_type: ID}, {
                                      "$set": {"cal": None, "sodium": None, "sugar": None, dish_type: None}})
            filter = {"ID": doc["ID"]}
            dish_coll.delete_one(filter)
            return ID
        else:
            return -5

    def retrieve_dish_by_name(self, name):
        projection = {"_id": 0}
        doc = dish_coll.find_one({"name": name}, projection)
        if doc is not None:
            return self.change_to_json_format(doc)
        else:
            return -5  # name does not exist in the collection

    def delete_dish_by_name(self, name):
        doc = dish_coll.find_one({"name": name})
        if doc is not None:
            dish_list = ["appetizer", "main", "dessert"]
            for dish_type in dish_list:
                meal_coll.update_many({dish_type: doc["ID"]}, {
                                      "$set": {"cal": None, "sodium": None, "sugar": None, dish_type: None}})
            filter = {"name": doc["name"]}
            dish_coll.delete_one(filter)
            return doc["ID"]
        else:
            return -5  # name does not exist in the collection


# MealCollection class stores the meals and perform operations on them
class MealCollection:
    def __init__(self):
        # self.keynum is the number of insert_meal operations performed so far.
        # It will be used to generate unique id's to meals inserted into collection
        count_doc = meal_coll.count_documents({})
        if count_doc != 0:
            self.keynum = meal_coll.find_one(
                sort=[("ID", -1)])["ID"]
        else:
            self.keynum = 0

    def change_to_json_format(self, doc):
        json_docs = json.dumps(doc, default=str)
        processed_docs = json.loads(json_docs)
        return processed_docs

    def insert_meal(self, name, appetizer_id, main_id, dessert_id):
        if name in [doc["name"] for doc in meal_coll.find()]:
            return -2  # meal of given name already exists

        id_list = [appetizer_id, main_id, dessert_id]
        if not all(id in [doc["ID"] for doc in dish_coll.find()] for id in id_list):
            return -6

        self.keynum += 1
        ID = self.keynum
        filter = {"ID": {"$in": id_list}}
        doc_list_by_filter = self.change_to_json_format(
            list(dish_coll.find(filter)))
        meal_coll.insert_one({"name": name,
                              "appetizer": appetizer_id,
                              "main": main_id,
                              "dessert": dessert_id,
                              "cal": sum([doc["cal"] for doc in doc_list_by_filter]),
                              "sodium": sum([doc["sodium"] for doc in doc_list_by_filter]),
                              "sugar": sum([doc["sugar"] for doc in doc_list_by_filter]),
                              "ID": ID})
        print("cal", sum([doc["cal"] for doc in doc_list_by_filter]))
        print("sodium-", [doc["sodium"] for doc in doc_list_by_filter])
        return ID

    def retrieve_all_meals(self):
        projection = {"_id": 0}
        documents = meal_coll.find({}, projection)
        list_documents = list(documents)
        return self.change_to_json_format(list_documents)

    def retrieve_meal_by_id(self, ID):
        projection = {"_id": 0}
        doc = meal_coll.find_one({"ID": ID}, projection)
        if doc is not None:  # the ID exists in collection
            return self.change_to_json_format(doc)
        else:
            return -5  # the ID does not exist in the collection

    def delete_meal_by_id(self, ID):
        doc = meal_coll.find_one({"ID": ID})
        if doc is not None:
            filter = {"ID": doc["ID"]}
            meal_coll.delete_one(filter)
            return ID
        else:
            return -5

    def change_meal_by_id(self, ID, name, appetizer_id, main_id, dessert_id):
        id_list = [appetizer_id, main_id, dessert_id]
        if not all(id in [doc["ID"] for doc in dish_coll.find()] for id in id_list):
            return -6

        filter = {"ID": {"$in": id_list}}
        doc_list_by_filter = self.change_to_json_format(
            list(dish_coll.find(filter)))
        filter_for_meal = {"ID": ID}
        meal_coll.update_one(filter_for_meal, {"$set": {
            "name": name,
            "appetizer": appetizer_id,
            "main": main_id,
            "dessert": dessert_id,
            "cal": sum([doc["cal"] for doc in doc_list_by_filter]),
            "sodium": sum([doc["sodium"] for doc in doc_list_by_filter]),
            "sugar": sum([doc["sugar"] for doc in doc_list_by_filter]),
            "ID": ID,
        }})
        return ID

    def retrieve_meal_by_name(self, name):
        projection = {"_id": 0}
        doc = meal_coll.find_one({"name": name}, projection)
        if doc is not None:
            return self.change_to_json_format(doc)
        else:
            return -5  # name does not exist in the collection

    def delete_meal_by_name(self, name):
        doc = meal_coll.find_one({"name": name})
        if doc is not None:
            filter = {"name": doc["name"]}
            meal_coll.delete_one(filter)
            return doc["ID"]
        else:
            return -5  # name does not exist in the collection

    def retrieve_meals_by_diet(self, diet):
        diet_doc = diet_coll.find_one({"name": diet})
        if diet_doc is not None:
            diet_cal = diet_doc["cal"]
            diet_sodium = diet_doc["sodium"]
            diet_sugar = diet_doc["sugar"]
            filter = {
                "$and": [
                    {"cal": {"$lte": diet_cal}},
                    {"sodium": {"$lte": diet_sodium}},
                    {"sugar": {"$lte": diet_sugar}}
                ]
            }

            projection = {"_id": 0}
            results = list(meal_coll.find(filter, projection))
            return self.change_to_json_format(results)

        else:
            return -5  # diet does not exist in the collection


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


dish_collection = DishCollection()    # create dishes instance with global scope
# The Dishes class implements the REST operations for the /dishes resource


class Dishes(Resource):
    global dish_collection

    # POST adds a dish to /dishes and returns its ID.
    def post(self):
        if request.headers.get('Content-Type') != 'application/json':
            return 0, 415

        request_json_dictionary = request.get_json()
        if "name" not in request_json_dictionary.keys():
            return -1, 422

        ID = dish_collection.insert_dish(request_json_dictionary["name"])
        if ID == -2:   # dish already exists
            return ID, 422

        if ID == -3:  # does not recognize this dish name.
            return ID, 422

        if ID == -4:  # API was not reachable.
            return ID, 504

        return ID, 201

    # GET returns all the dishes in the collection with their nutritions in json
    def get(self):
        return dish_collection.retrieve_all_dishes(), 200

# The DishId class implements the REST operations for the /dishes/{id} resource


class DishId(Resource):
    global dish_collection

    def get(self, dish_id):
        result = dish_collection.retrieve_dish_by_id(dish_id)
        if result == -5:
            return -5, 404
        else:
            return result, 200

    def delete(self, dish_id):
        id_result = dish_collection.delete_dish_by_id(dish_id)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200

# The DishName class implements the REST operations for the /dishes/{name} resource


class DishName(Resource):
    global dish_collection

    def get(self, dish_name):
        result = dish_collection.retrieve_dish_by_name(dish_name)
        if result == -5:
            return -5, 404
        else:
            return result, 200

    def delete(self, dish_name):
        id_result = dish_collection.delete_dish_by_name(dish_name)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200


meal_collection = MealCollection()    # create meals instance with global scope

# The Meals class implements the REST operations for the /meals resource


class Meals(Resource):
    global meal_collection

    def post(self):
        if request.headers.get('Content-Type') != 'application/json':
            return 0, 415

        request_json_dictionary = request.get_json()
        request_fields = ["name", "appetizer", "main", "dessert"]
        if not all(field in request_json_dictionary.keys() for field in request_fields):
            return -1, 422

        ID = meal_collection.insert_meal(
            request_json_dictionary["name"], request_json_dictionary["appetizer"],
            request_json_dictionary["main"], request_json_dictionary["dessert"])
        if ID == -2:   # meal already exists
            return ID, 422

        if ID == -6:  # does not recognize one of the dishes name.
            return ID, 422

        return ID, 201

    def get(self):
        diet = request.args.get('diet')
        if diet:
            result = meal_collection.retrieve_meals_by_diet(diet)
            if result == -5:
                return f"Diet {diet} not found", 404
            else:
                return result, 200

        else:
            return meal_collection.retrieve_all_meals(), 200

# The MealId class implements the REST operations for the /meals/{id} resource


class MealId(Resource):
    global dish_collection

    def get(self, meal_id):
        result = meal_collection.retrieve_meal_by_id(meal_id)
        if result == -5:
            return -5, 404
        else:
            return result, 200

    def delete(self, meal_id):
        id_result = meal_collection.delete_meal_by_id(meal_id)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200

    def put(self, meal_id):
        if request.headers.get('Content-Type') != 'application/json':
            return 0, 415

        request_json_dictionary = request.get_json()
        request_fields = ["name", "appetizer", "main", "dessert"]
        if not all(field in request_json_dictionary.keys() for field in request_fields):
            return -1, 422

        ID = meal_collection.change_meal_by_id(meal_id,
                                               request_json_dictionary["name"], request_json_dictionary["appetizer"],
                                               request_json_dictionary["main"], request_json_dictionary["dessert"])

        if ID == -6:  # does not recognize one of the dishes name.
            return ID, 422

        return ID, 200

# The MealName class implements the REST operations for the /meals/{name} resource


class MealName(Resource):
    global meal_collection

    def get(self, meal_name):
        result = meal_collection.retrieve_meal_by_name(meal_name)
        if result == -5:
            return -5, 404
        else:
            return result, 200

    def delete(self, meal_name):
        id_result = meal_collection.delete_meal_by_name(meal_name)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200


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


api.add_resource(Dishes, '/dishes')
api.add_resource(DishId, '/dishes/<int:dish_id>')
api.add_resource(DishName, '/dishes/<string:dish_name>')
api.add_resource(Meals, '/meals')
api.add_resource(MealId, '/meals/<int:meal_id>')
api.add_resource(MealName, '/meals/<string:meal_name>')
api.add_resource(Diets, '/diets')
api.add_resource(DietName, '/diets/<string:diet_name>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
