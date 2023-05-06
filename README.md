# Adverity Test - Star Wars World Explorer

## Up and running
1. Make sure to have at least python3.10 version installed (if not, google `pyenv`)
2. Create virtual environment (`python3.10 -m venv <venv-name>`)
3. Activate the venv (`source <venv-name>/bin/activate`)
4. Install the dependencies (`pip install -r requirements.txt`)
5. Run the migrations (`python manage.py migrate`)
6. Run the Django server (`python manage.py runserver`)
7. Run the test suit (`pytest`)

Open following URL (`http://127.0.0.1:8000/app/collections/`) with your preferred browser.


---

# Assignment introduction
Build a simple app which allows you to collect, resolve and inspect information about characters in
the Star Wars universe from the SWAPI.
The entry endpoint for data retrieval is: https://swapi.dev/api/people/
If the API should be inaccessible for some reason you can host your own version of it.

  - For the sake of simplicity everything should be running in the Django development server (no task queues or similar)
  - Interface does not have to be fancy (you can use plain HTML/CSS, Bootstrap, ...)
  - Keep things simple, additional comments on how your app can be further improved and optimized are welcome


## Data retrieval and storage

The user should have a way to download the latest complete dataset of characters from the API by
clicking on a button, the collected and transformed data should be stored as a CSV file in the file
system. Metadata for downloaded datasets (e.g. filename, date, etc.) should be stored inside the
database. Fetching and transformations should be implemented efficiently, minimize the amount of
requests, your app should be able to process large amounts of data.e

### Mandatory requirements
  - Django 2.0+
  - Python 3.6+
  - petl
#### Recommended
  - requests


#### Screenshots

![Collections Explorer](https://user-images.githubusercontent.com/640755/75017565-2ec0eb00-5485-11ea-913c-0b15ba62bf48.png)
![Collection Detailed View](https://user-images.githubusercontent.com/640755/74833466-6ad33f00-5311-11ea-8e3c-03c814dd863f.png)
![Collection Filters](https://user-images.githubusercontent.com/640755/74833446-5ee77d00-5311-11ea-95d8-ce1b2bb13404.png)