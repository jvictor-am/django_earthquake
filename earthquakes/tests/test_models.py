import pytest
from earthquakes.models import City

@pytest.mark.django_db
def test_city_creation():
    city = City.objects.create(name='Test City', latitude=10.0, longitude=20.0)
    assert city.name == 'Test City'
    assert city.latitude == 10.0
    assert city.longitude == 20.0
