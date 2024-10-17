# earthquakes/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CityViewSet, search_earthquakes, search_earthquakes_api

app_name = 'earthquakes'


router = DefaultRouter()
router.register(r'cities', CityViewSet)


urlpatterns = [
    path('search/', search_earthquakes, name='search'),
    path('api/', include(router.urls)),
    path('api/search/', search_earthquakes_api, name='search_api'),
]
