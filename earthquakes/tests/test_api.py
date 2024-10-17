import json
import pytest
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from earthquakes.models import City

@pytest.mark.django_db
class TestSearchEarthquakesAPI:
    @pytest.fixture(autouse=True)
    def setup_cities(self):
        cities_data = [
            {"name": "Los Angeles, CA"},
            {"name": "San Francisco, CA"},
            {"name": "Tokyo, Japan"},
        ]

        for city_data in cities_data:
            City.objects.get_or_create(name=city_data["name"])

    @patch('earthquakes.views.requests.get')
    def test_search_earthquakes(self, mock_get):
        client = APIClient()

        mock_api_response = {
            "features": [
                {
                    "properties": {
                        "mag": 5.1,
                        "place": "11 km W of Ichihara, Japan",
                        "time": 1706324400000
                    },
                    "geometry": {
                        "coordinates": [140.059444, 35.636111]
                    }
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_api_response

        url = reverse('earthquakes:search_api')
        data = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
        }

        response = client.get(url, data)
        assert response.status_code == status.HTTP_200_OK

        response_data = json.loads(response.content)
        assert response_data['nearest_city'] == "Tokyo, Japan"
        assert response_data['nearest_distance'] == pytest.approx(27.337303358951942, rel=1e-2)
        assert response_data['magnitude'] == 5.1
        assert response_data['location'] == "11 km W of Ichihara, Japan"
        assert response_data['date'] == "2024-01-27"
