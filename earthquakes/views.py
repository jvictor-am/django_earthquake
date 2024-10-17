import requests

from datetime import datetime
from django.core.cache import cache
from django.shortcuts import render
from django.utils import timezone
from geopy.distance import great_circle
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import City, SearchResult, CityLog
from .serializers import CitySerializer


CACHE_TIMEOUT = 60 * 60 * 24  # Cache timeout (24 hours)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer


def get_cached_or_api_response(start_date, end_date, min_magnitude):
    """
    Fetch the earthquake data from cache or API.
    """
    cache_key = f"api_response_{start_date}_{end_date}_{min_magnitude}"
    cached_api_response = cache.get(cache_key)
    
    if cached_api_response:
        return cached_api_response, "Using cached API response"

    # Query the USGS API
    url = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
    params = {
        'format': 'geojson',
        'starttime': start_date,
        'endtime': end_date,
        'minmagnitude': min_magnitude,
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Cache the API response
    cache.set(cache_key, data, timeout=CACHE_TIMEOUT)
    return data, "Querying the USGS API"


def find_nearest_city(data):
    """
    Find the nearest city based on earthquake data.
    """
    nearest_city = None
    nearest_distance = float('inf')
    closest_earthquake = None

    if data['features']:
        for earthquake in data['features']:
            magnitude = earthquake['properties']['mag']
            location = earthquake['properties']['place']
            date = datetime.fromtimestamp(earthquake['properties']['time'] / 1000.0).date()
            earthquake_coordinates = (earthquake['geometry']['coordinates'][1], 
                                      earthquake['geometry']['coordinates'][0])

            for city in City.objects.all():
                city_coordinates = (city.latitude, city.longitude)
                distance = great_circle(city_coordinates, earthquake_coordinates).kilometers

                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_city = city
                    closest_earthquake = (magnitude, location, date)

    return nearest_city, nearest_distance, closest_earthquake


def create_search_result(nearest_city, closest_earthquake, start_date, end_date, nearest_distance):
    """
    Create a SearchResult if one doesn't already exist.
    """
    existing_result = SearchResult.objects.filter(
        city=nearest_city,
        search_start_date=start_date,
        search_end_date=end_date,
        earthquake_magnitude=closest_earthquake[0],
        earthquake_location=closest_earthquake[1],
        earthquake_date=closest_earthquake[2]
    ).exists()

    if not existing_result:
        SearchResult.objects.create(
            city=nearest_city,
            earthquake_magnitude=closest_earthquake[0],
            earthquake_location=closest_earthquake[1],
            earthquake_date=closest_earthquake[2],
            search_start_date=start_date,
            search_end_date=end_date,
            nearest_distance=nearest_distance
        )


def format_result_message(nearest_city, nearest_distance, closest_earthquake, start_date, end_date, source):
    """
    Format the result message to display.
    """
    formatted_start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%B %d, %Y")
    formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%B %d, %Y")
    formatted_earthquake_date = closest_earthquake[2].strftime("%B %d, %Y")

    return (f"Result between <strong style='color:#205067'>{formatted_start_date} and {formatted_end_date}</strong>: "
            f"<br><br>"
            f"The closest impacted city was <strong style='color:#205067'>{nearest_city.name}</strong> with a distance of "
            f"<strong style='color:#205067'>{nearest_distance:.2f} km</strong> from the earthquake. <br>"
            f"The earthquake was a <strong style='color:#205067'>M {closest_earthquake[0]} - {closest_earthquake[1]}</strong>"
            f" on {formatted_earthquake_date}. <br><br>{source} !!!")


def search_earthquakes(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        min_magnitude = float(request.POST.get('min_magnitude', 5.0))

        # Get cached data or fetch from API
        data, source = get_cached_or_api_response(start_date, end_date, min_magnitude)

        # Find the nearest city to an earthquake
        nearest_city, nearest_distance, closest_earthquake = find_nearest_city(data)

        if nearest_city and closest_earthquake:
            create_search_result(nearest_city, closest_earthquake, start_date, end_date, nearest_distance)
            result_message = format_result_message(nearest_city, nearest_distance, closest_earthquake, start_date, end_date, source)
        else:
            result_message = "No results found."

        return render(request, 'earthquakes/search_results.html', {'result_message': result_message})

    return render(request, 'earthquakes/search.html')


@api_view(['GET'])
def search_earthquakes_api(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    min_magnitude = request.query_params.get('min_magnitude', 5.0)

    if not start_date or not end_date:
        return Response({"error": "Please provide both start_date and end_date parameters."}, status=400)
    
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

    data, source = get_cached_or_api_response(start_date, end_date, min_magnitude)

    nearest_city, nearest_distance, closest_earthquake = find_nearest_city(data)

    if nearest_city and closest_earthquake:
        create_search_result(nearest_city, closest_earthquake, start_date, end_date, nearest_distance)
        result = {
            "nearest_city": nearest_city.name,
            "nearest_distance": nearest_distance,
            "magnitude": closest_earthquake[0],
            "location": closest_earthquake[1],
            "date": closest_earthquake[2].strftime("%Y-%m-%d"),
            "source": source
        }
        return Response(result)
    else:
        return Response({"message": "No earthquakes found for the given parameters."})
