import csv
import json
import os

import pytest
from django.urls import reverse
from requests_mock import Mocker
from django.core.files.base import File
from django.test import Client
from pytest import fixture
from .models import Collection

# Sample data for mocking the responses
planets_data = {
    "next": None,
    "results": [
        {"url": "https://swapi.dev/api/planets/1/", "name": "Tatooine"},
        {"url": "https://swapi.dev/api/planets/2/", "name": "Alderaan"},
    ]
}

people_data = {
    "next": None,
    "results": [
          {
              "name": "Luke Skywalker",
              "height": "172",
              "mass": "77",
              "hair_color": "blond",
              "skin_color": "fair",
              "eye_color": "blue",
              "birth_year": "19BBY",
              "gender": "male",
              "homeworld": "https://swapi.dev/api/planets/1/",
              "films": [
                  "https://swapi.dev/api/films/1/",
              ],
              "species": [],
              "vehicles": [
                  "https://swapi.dev/api/vehicles/14/",
              ],
              "starships": [
                  "https://swapi.dev/api/starships/12/",
              ],
              "created": "2014-12-09T13:50:51.644000Z",
              "edited": "2014-12-20T21:17:56.891000Z",
              "url": "https://swapi.dev/api/people/1/"
          },
          {
                "name": "Leia Organa",
                "height": "150",
                "mass": "49",
                "hair_color": "brown",
                "skin_color": "light",
                "eye_color": "brown",
                "birth_year": "19BBY",
                "gender": "female",
                "homeworld": "https://swapi.dev/api/planets/2/",
                "films": [
                    "https://swapi.dev/api/films/1/",
                ],
                "species": [],
                "vehicles": [
                    "https://swapi.dev/api/vehicles/30/"
                ],
                "starships": [],
                "created": "2014-12-10T15:20:09.791000Z",
                "edited": "2014-12-20T21:17:50.315000Z",
                "url": "https://swapi.dev/api/people/5/"
          },
    ]
}



@fixture
def client():
    return Client()


def create_collection_with_data():
    filename = "test_data.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["name", "date", "homeworld"])  # header
        writer.writerow(["Luke Skywalker", "2014-12-20", "Tatooine"])  # data
        writer.writerow(["Leia Organa", "2014-12-19", "Alderaan"])  # data
    collection = Collection(filename=filename)
    with open(filename, 'rb') as f:
        collection.file.save(filename, File(f))
    collection.save()
    os.remove(filename)  # Remove the temporary file
    return collection



@pytest.mark.django_db
def test_collections_view_post(client, requests_mock: Mocker):
    # Mock the external API calls
    requests_mock.get("https://swapi.dev/api/planets/", text=json.dumps(planets_data))
    requests_mock.get("https://swapi.dev/api/people/", text=json.dumps(people_data))

    # Make a POST request to the view (mimic the button click with value "fetch")
    response = client.post(reverse('app:collections'), data={"fetch": "true"})

    # Assert that the request was successful, and we redirect to show the new collection
    assert response.status_code == 302

    # Assert that the success message was added
    messages = list(response.wsgi_request._messages)
    assert len(messages) == 1
    assert str(messages[0]) == "Successfully retrieved a new collection!"

    # Assert that a Collection object was created and saved correctly
    assert Collection.objects.count() == 1
    collection = Collection.objects.first()
    assert collection.filename is not None

    # Read the CSV file and assert that it contains the expected data
    csv_data = collection.file.read().decode()
    assert "Luke Skywalker" in csv_data
    assert "Leia Organa" in csv_data
    # Homeworld resolution works fine ("homeworld": "https://swapi.dev/api/planets/2/", became Alderaan)
    assert "Tatooine" in csv_data
    assert "Alderaan" in csv_data
    # Date (edited) conversion works fine ("2014-12-20T21:17:50.315000Z" became "2014-12-20")
    assert "2014-12-20" in csv_data
    assert "date" in csv_data  # using petl transformation the "edited" became "date"


@pytest.mark.django_db
def test_get_collection_view_no_checked(client):
    collection = create_collection_with_data()

    response = client.get(reverse('app:details', args=[collection.id]))
    assert response.status_code == 200  # Expecting a successful response
    assert response.context["filename"] == collection.filename

    # Assert that the table contains the expected data
    header = response.context["header"]
    assert header == ("name", "date", "homeworld")

    data = response.context["data"]
    assert len(data) == 2
    assert ("Luke Skywalker", "2014-12-20", "Tatooine") in data
    assert ("Leia Organa", "2014-12-19", "Alderaan") in data


@pytest.mark.django_db
def test_get_collection_view_with_checked(client):
    collection = create_collection_with_data()

    # Send a GET request with the "checked" parameter
    response = client.get(reverse('app:details', args=[collection.id]), data={"checked": "homeworld"})

    assert response.status_code == 200  # Expecting a successful response
    assert response.context["filename"] == collection.filename

    # Assert that the table contains the expected aggregated data
    header = response.context["header"]
    assert header == ("homeworld", "count")

    data = response.context["data"].object_list
    assert len(data) == 2
    assert ("Tatooine", 1) in data
    assert ("Alderaan", 1) in data