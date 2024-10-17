import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_search_view(client):
    response = client.post(reverse('earthquakes:search'), {
        'start_date': '2024-01-01',
        'end_date': '2024-10-15',
        'min_magnitude': 5.5,
    })
    assert response.status_code == 200
    assert 'Result' in response.content.decode()
