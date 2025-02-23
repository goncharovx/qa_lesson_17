import json

import pytest
import requests
from jsonschema import validate

BASE_URL = "https://reqres.in/api"


def load_schema(filename):
    with open(f"schemas/{filename}", "r") as file:
        return json.load(file)


@pytest.mark.parametrize("page", [1, 2])
def test_get_list_users(page):
    response = requests.get(f"{BASE_URL}/users", params={"page": page})
    assert response.status_code == 200

    schema = load_schema("list_users_schema.json")
    validate(instance=response.json(), schema=schema)


@pytest.mark.parametrize("user_id", [2])
def test_get_single_user(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    assert response.status_code == 200

    schema = load_schema("single_user_schema.json")
    validate(instance=response.json(), schema=schema)


def test_get_single_user_not_found():
    response = requests.get(f"{BASE_URL}/users/23")
    assert response.status_code == 404
    assert response.text == "{}"


def test_create_user():
    payload = {"name": "morpheus", "job": "leader"}
    response = requests.post(f"{BASE_URL}/users", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["job"] == payload["job"]
    assert "id" in data
    assert "createdAt" in data


def test_create_user_invalid():
    response = requests.post(f"{BASE_URL}/users", json={})
    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert "createdAt" in data


def test_update_user():
    payload = {"name": "morpheus", "job": "zion resident"}
    response = requests.put(f"{BASE_URL}/users/2", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == payload["name"]
    assert data["job"] == payload["job"]
    assert "updatedAt" in data


def test_delete_user():
    response = requests.delete(f"{BASE_URL}/users/2")
    assert response.status_code == 204
    assert response.text == ""


def test_register_user():
    payload = {"email": "eve.holt@reqres.in", "password": "pistol"}
    response = requests.post(f"{BASE_URL}/register", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert "token" in data


def test_register_user_without_password():
    payload = {"email": "sydney@fife"}
    response = requests.post(f"{BASE_URL}/register", json=payload)
    assert response.status_code == 400

    data = response.json()
    assert data["error"] == "Missing password"


def test_login_user():
    payload = {"email": "eve.holt@reqres.in", "password": "cityslicka"}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "token" in data


def test_login_user_without_password():
    payload = {"email": "peter@klaven"}
    response = requests.post(f"{BASE_URL}/login", json=payload)
    assert response.status_code == 400

    data = response.json()
    assert data["error"] == "Missing password"
