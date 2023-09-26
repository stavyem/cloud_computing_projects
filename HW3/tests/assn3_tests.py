import pytest
import requests

def test_post_dishes():
    dish_names = ["orange", "spaghetti", "apple pie"]
    ids = set()
    for dish_name in dish_names:
        url = 'http://127.0.0.1:8000/dishes'
        headers = {'Content-Type': 'application/json'}
        data = {'name': dish_name}

        response = requests.post(url, headers=headers, json=data)
        assert response.status_code == 201
        assert response.json() not in ids
        ids.add(response.json())

def test_get_dish():
    url_orange = f"http://127.0.0.1:8000/dishes/orange"
    response_get = requests.get(url_orange)
    orange_id = response_get.json()["ID"]

    url = f"http://127.0.0.1:8000/dishes/{orange_id}"
    response = requests.get(url)
    assert response.status_code == 200
    assert 0.9 <= response.json()['sodium'] <= 1.1

def test_get_dishes():
    url = "http://127.0.0.1:8000/dishes"
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_post_dishes_blah():
    url = 'http://127.0.0.1:8000/dishes'
    headers = {'Content-Type': 'application/json'}
    data = {'name': 'blah'}

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code in [404, 400, 422]
    assert response.text.strip() == "-3"

def test_post_dishes_orange():
    url = 'http://127.0.0.1:8000/dishes'
    headers = {'Content-Type': 'application/json'}
    data = {'name': 'orange'}

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code in [404, 400, 422]
    assert response.text.strip() == "-2"

def test_post_meals():
    url_orange = f"http://127.0.0.1:8000/dishes/orange"
    response_get = requests.get(url_orange)
    orange_id = response_get.json()["ID"]

    url_spaghetti = f"http://127.0.0.1:8000/dishes/spaghetti"
    response_get = requests.get(url_spaghetti)
    spaghetti_id = response_get.json()["ID"]

    url_apple_pie = f"http://127.0.0.1:8000/dishes/apple pie"
    response_get = requests.get(url_apple_pie)
    apple_pie_id = response_get.json()["ID"]


    url = 'http://127.0.0.1:8000/meals'
    headers = {'Content-Type': 'application/json'}
    data = {
        'name': 'delicious',
        'appetizer': orange_id,
        'main': spaghetti_id,
        'dessert': apple_pie_id
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code == 201
    assert response.json() > 0

def test_get_meals():
    url = 'http://127.0.0.1:8000/meals'
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert 400 <= response.json()['1']['cal'] <= 500


def test_post_meals_duplicate():
    url_orange = f"http://127.0.0.1:8000/dishes/orange"
    response_get = requests.get(url_orange)
    orange_id = response_get.json()["ID"]

    url = 'http://127.0.0.1:8000/meals'
    headers = {'Content-Type': 'application/json'}
    data = {
        'name': 'delicious',
        'appetizer': orange_id,
        'main': orange_id,
        'dessert': orange_id
    }

    response = requests.post(url, headers=headers, json=data)
    assert response.status_code in [400, 422]
    assert response.text.strip() == "-2"
