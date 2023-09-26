# REST API server code
# It uses Flask to build a RESTful service in Python.

# flask run --port 8000     (or whatever port you want to run on.  if no "--port" option specified, it is port 5000)
# flask will return the IP and port the app is running on
# we installed the packages Flask and flask-restful before writing this program


from flask import Flask  # , jsonify
from flask_restful import Resource, Api, reqparse
from flask import request
import requests
import json

app = Flask(__name__)  # initialize Flask
api = Api(app)  # create API


# DishCollection class stores the dishes and perform operations on them
class DishCollection:
    def __init__(self):
        # self.insert_num is the number of insert_dish operations performed so far.
        # It will be used to generate unique id's to dishes inserted into collection
        self.insert_num = 0
        # self.dishes is a dictionary of the form {ID:dish} where ID is an integer and dish is a request_json_dictionary
        self.dishes = {}  # dishes in the collection

    def insert_dish(self, i_dish):
        # i_dish is the name of the dish (a string)
        # This function SHOULD CHECK if dish already exists and if so return error.
        # Currently, it lets the same dish exist with different keys
        if i_dish in [self.dishes[ID]['name'] for ID in self.dishes]:  # dish already exists
            print("DishCollection: dish ", i_dish, " already exists")
            return -2  # ID = -2 dish of given name already exists

        self.insert_num += 1
        ID = self.insert_num
        api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(
            i_dish)
        response = requests.get(
            api_url, headers={'X-Api-Key': 'rsxmQXdXLGYQXTo27o9WwA==kcPtOo9RsgtVe41K'})

        if response.status_code == requests.codes.ok:
            json_response_list = json.loads(response.text)
            # dish name isn't recognized.
            if len(i_dish.split(" and ")) != len(json_response_list):
                print("DishCollection: dish ", i_dish, " cannot be found")
                self.insert_num -= 1
                return -3

            self.dishes[ID] = {"name": i_dish, "ID": ID, "cal": sum([food_dict["calories"] for food_dict in json_response_list]),
                               "size": sum([food_dict["serving_size_g"] for food_dict in json_response_list]),
                               "sodium": sum([food_dict["sodium_mg"] for food_dict in json_response_list]),
                               "sugar": sum([food_dict["sugar_g"] for food_dict in json_response_list])}

            print("DishCollection: inserted dish ", i_dish, " with ID ", ID)
            return ID

        else:
            print("Error, API wasn't reachable")
            self.insert_num -= 1
            return -4

    # returns all the request_json_dictionary containing all dishes
    def retrieve_all_dishes(self):
        print("DishCollection: retrieving all dishes:")
        print(self.dishes)
        return self.dishes

    def retrieve_dish_by_id(self, ID):
        if ID in self.dishes.keys():  # the ID exists in collection
            dict_id = self.dishes[ID]
            print("DishCollection: found nutriton of the dish \n", dict_id)
            return dict_id
        else:
            print("DishCollection: did not find ID", ID)
            return -5  # the ID does not exist in the collection

    def delete_dish_by_id(self, ID):
        if ID in self.dishes.keys():
            meal_list = ["appetizer", "main", "dessert"]
            for meal_dictionary in meal_collection.meals.values():
                for meal_type in meal_list:
                    if ID == meal_dictionary[meal_type]:
                        meal_dictionary[meal_type] = None
                        meal_dictionary["cal"] = None
                        meal_dictionary["sodium"] = None
                        meal_dictionary["sugar"] = None
            del self.dishes[ID]
            return ID
        else:
            return -5

    def retrieve_dish_by_name(self, name):
        dicts_list_by_name = [dict for dict in self.dishes.values(
        ) if name == dict["name"]]  # name exists in collection
        if len(dicts_list_by_name) == 1:
            print("DishCollection: found nutriton of the dish \n",
                  dicts_list_by_name[0])
            return dicts_list_by_name[0]
        else:
            print("DishCollection: did not find name", name)
            return -5  # name does not exist in the collection

    def delete_dish_by_name(self, name):
        dicts_list_by_name = [dict["ID"] for dict in self.dishes.values(
        ) if name == dict["name"]]  # name exists in collection
        if len(dicts_list_by_name) == 1:
            ID = dicts_list_by_name[0]
            meal_list = ["appetizer", "main", "dessert"]
            for meal_dictionary in meal_collection.meals.values():
                for meal_type in meal_list:
                    if ID == meal_dictionary[meal_type]:
                        meal_dictionary[meal_type] = None
                        meal_dictionary["cal"] = None
                        meal_dictionary["sodium"] = None
                        meal_dictionary["sugar"] = None
            del self.dishes[ID]
            return ID
        else:
            return -5  # name does not exist in the collection


# MealCollection class stores the meals and perform operations on them
class MealCollection:
    def __init__(self):
        # self.insert_num is the number of insert_meal operations performed so far.
        # It will be used to generate unique id's to meals inserted into collection
        self.insert_num = 0
        # self.meals is a dictionary of the form {ID:meal} where ID is an integer and meal is a request_json_dictionary
        self.meals = {}  # meals in the collection

    def insert_meal(self, name, appetizer_id, main_id, dessert_id):
        if name in [self.meals[ID]['name'] for ID in self.meals]:
            print("MealCollection: meal ", name, " already exists")
            return -2  # meal of given name already exists

        id_list = [appetizer_id, main_id, dessert_id]
        if not all(id in dish_collection.dishes.keys() for id in id_list):
            return -6

        self.insert_num += 1
        ID = self.insert_num
        self.meals[ID] = {"name": name,
                          "ID": ID,
                          "appetizer": appetizer_id,
                          "main": main_id,
                          "dessert": dessert_id,
                          "cal": sum([dish_collection.dishes[id]["cal"] for id in id_list]),
                          "sodium": sum([dish_collection.dishes[id]["sodium"] for id in id_list]),
                          "sugar": sum([dish_collection.dishes[id]["sugar"] for id in id_list])}

        print("MealCollection: inserted meal ", name, " with ID ", ID)
        return ID

    def retrieve_all_meals(self):
        print("MealsCollection: retrieving all meals:\n")
        print(self.meals)
        return self.meals

    def retrieve_meal_by_id(self, ID):
        if ID in self.meals.keys():  # the ID exists in collection
            dict_id = self.meals[ID]
            print("MealCollection: found nutriton of the meal \n", dict_id)
            return dict_id
        else:
            print("MealCollection: did not find ID", ID)
            return -5  # the ID does not exist in the collection

    def delete_meal_by_id(self, ID):
        if ID in self.meals.keys():
            del self.meals[ID]
            return ID
        else:
            return -5

    def insert_meal_by_id(self, ID, name, appetizer_id, main_id, dessert_id):
        if name in [self.meals[id]['name'] for id in self.meals]:
            print("MealCollection: meal ", name, " already exists")
            return -2  # meal of given name already exists

        id_list = [appetizer_id, main_id, dessert_id]
        if not all(id in dish_collection.dishes.keys() for id in id_list):
            return -6

        self.meals[ID] = {"name": name,
                          "ID": ID,
                          "appetizer": appetizer_id,
                          "main": main_id,
                          "dessert": dessert_id,
                          "cal": sum([dish_collection.dishes[id]["cal"] for id in id_list]),
                          "sodium": sum([dish_collection.dishes[id]["sodium"] for id in id_list]),
                          "sugar": sum([dish_collection.dishes[id]["sugar"] for id in id_list])}

        print("MealCollection: inserted meal ", name, " with ID ", ID)
        return ID
    
    def change_meal_by_id(self, ID, name, appetizer_id, main_id, dessert_id):
        id_list = [appetizer_id, main_id, dessert_id]
        if not all(id in dish_collection.dishes.keys() for id in id_list):
            return -6

        self.meals[ID] = {"name": name,
                          "ID": ID,
                          "appetizer": appetizer_id,
                          "main": main_id,
                          "dessert": dessert_id,
                          "cal": sum([dish_collection.dishes[id]["cal"] for id in id_list]),
                          "sodium": sum([dish_collection.dishes[id]["sodium"] for id in id_list]),
                          "sugar": sum([dish_collection.dishes[id]["sugar"] for id in id_list])}

        print("MealCollection: inserted meal ", name, " with ID ", ID)
        return ID

    def retrieve_meal_by_name(self, name):
        dicts_list_by_name = [
            dict for dict in self.meals.values() if name == dict["name"]]
        if len(dicts_list_by_name) == 1:  # name exists in collection
            print("MealCollection: found nutriton of the meal \n",
                  dicts_list_by_name[0])
            return dicts_list_by_name[0]
        else:
            print("MealCollection: did not find name", name)
            return -5  # name does not exist in the collection

    def delete_meal_by_name(self, name):
        dicts_list_by_name = [dict["ID"]
                              for dict in self.meals.values() if name == dict["name"]]
        if len(dicts_list_by_name) == 1:  # name exists in collection
            ID = dicts_list_by_name[0]
            del self.meals[ID]
            return ID
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
        id_result = dish_collection.retrieve_dish_by_id(dish_id)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200

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
        id_result = dish_collection.retrieve_dish_by_name(dish_name)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200

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
        return meal_collection.retrieve_all_meals(), 200

# The MealId class implements the REST operations for the /meals/{id} resource


class MealId(Resource):
    global dish_collection

    def get(self, meal_id):
        id_result = meal_collection.retrieve_meal_by_id(meal_id)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200

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
        id_result = meal_collection.retrieve_meal_by_name(meal_name)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200

    def delete(self, meal_name):
        id_result = meal_collection.delete_meal_by_name(meal_name)
        if id_result == -5:
            return -5, 404
        else:
            return id_result, 200


api.add_resource(Dishes, '/dishes')
api.add_resource(DishId, '/dishes/<int:dish_id>')
api.add_resource(DishName, '/dishes/<string:dish_name>')
api.add_resource(Meals, '/meals')
api.add_resource(MealId, '/meals/<int:meal_id>')
api.add_resource(MealName, '/meals/<string:meal_name>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
