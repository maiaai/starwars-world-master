import csv
import uuid
import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.core.files.base import ContentFile
import petl as etl


import requests
from datetime import datetime

from app.models import Collection


@csrf_exempt
def fetch(request):
    selected = request.POST.getlist("selected_pills", None)
    print(selected)
    return HttpResponse(request.GET)


class CollectionsView(ListView):
    model = Collection
    template_name = "starwars/collections.html"
    context_object_name = "collections"
    planets = dict()

    def post(self, request, *args, **kwargs):
        if "fetch" in request.POST:
            # Task requirement said to NOT store anything else in DB except metadata about the downloaded files
            # Hence we fetch and parse the planets "on the fly" whenever there is a POST request.
            self._fetch_planets()  # !!! CACHE THIS
            collection = self.fetch_people()
            if collection:
                messages.success(request, "Successfully retrieved a new collection!")
            return HttpResponseRedirect(request.path)
        # If no valid action was provided in the POST request, fallback to the default GET behavior
        return self.get(request, *args, **kwargs)

    def _fetch_planets(self):
        url = 'https://swapi.dev/api/planets/'
        full_response = []

        while url:  # This basically loops over the paginated results until there is no more "next" in the URL.
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"An error occurred while fetching from API. Error: {response.json()}")
            data = response.json()
            full_response.extend(data['results'])
            url = data['next']

        for planet in full_response:
            planet_id = planet.get("url", None).split("/")[-2]
            planet_name = planet.get("name", None)
            self.planets |= {planet_id: planet_name}  # Update the dictionary

    def _convert_timestamp(self, val, row):
        dt = datetime.strptime(row.edited, "%Y-%m-%dT%H:%M:%S.%f%z")
        return dt.strftime("%Y-%m-%d")

    def _resolve_homeworld(self, val, row):
        planet_id = row.homeworld.split("/")[-2]  # ['https:', '', 'swapi.dev', 'api', 'planets', '12', '']
        return self.planets[str(planet_id)]  # Retrieve the planet name from the planets dict in memory

    def fetch_people(self):
        url = 'https://swapi.dev/api/people/'
        full_response = []

        while url:  # This basically loops over the paginated results until there is no more "next" in the URL.
            response = requests.get(url)
            if response.status_code != 200:
                raise ValueError(f"An error occurred while fetching from API. Error: {response.json()}")
            data = response.json()
            full_response.extend(data['results'])
            url = data['next']

        # Make the transformations explicitly understandable
        table = etl.fromdicts(full_response)
        tb1 = etl.cutout(table, "films", "species", "vehicles", "starships", "url", "created")
        tb2 = etl.convert(tb1, "edited", self._convert_timestamp, pass_row=True).rename("edited", "date")
        tb3 = etl.convert(tb2, "homeworld", self._resolve_homeworld, pass_row=True)

        # Get memory source
        source = etl.MemorySource()
        # Dump the table into the memory source
        etl.tocsv(tb3, source)
        # Wrap the value from the memory source into a File-like object, ready for Django
        content_file = ContentFile(source.getvalue())

        filename = str(uuid.uuid4()) + ".csv"
        obj = Collection(filename=filename)
        obj.file.save(filename, content_file)
        obj.save()
        return obj


class GetCollection(DetailView):
    model = Collection
    template_name = "starwars/details.html"
    context_object_name = "collection"

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.object
        csv_file = collection.file.path
        table = etl.fromcsv(csv_file)

        selectedFilters = self.request.GET.get("checked")
        if selectedFilters:
            items = selectedFilters.split(',')
            aggregated_table = etl.aggregate(table, key=items, aggregation=len, value='name', field='count')
            header = etl.header(aggregated_table)
            data = etl.data(aggregated_table)
            # aggregated_data = etl.dicts(aggregated_table)
            paginator = Paginator(list(data), 9999)  # Show 10 rows per page
        else:
            header = etl.header(table)
            data = etl.data(table)
            paginator = Paginator(list(data), 10)  # Show 10 rows per page


        # Paginate the data
        page = self.request.GET.get('page', 1)
        # paginator = Paginator(list(data), 10)  # Show 10 rows per page
        paginated_data = paginator.get_page(page)

        context['header'] = header
        context['data'] = paginated_data
        context['filename'] = collection.filename
        return context
