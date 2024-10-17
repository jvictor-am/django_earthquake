from datetime import datetime
from django.db import models
from geopy.geocoders import Nominatim


class City(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.latitude or not self.longitude:
            geolocator = Nominatim(user_agent="your_custom_user_agent")
            try:
                location = geolocator.geocode(self.name)
                if location:
                    self.latitude = location.latitude
                    self.longitude = location.longitude
            except GeocoderTimedOut:
                self.latitude = None
                self.longitude = None
        super().save(*args, **kwargs)
        CityLog.objects.create(city_name=self.name, action='add')

    def __str__(self):
        return self.name
    


class CityLog(models.Model):
    city_name = models.CharField(max_length=100)
    action = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.city_name} at {self.timestamp}"


class SearchResult(models.Model):
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    earthquake_magnitude = models.FloatField()
    earthquake_location = models.CharField(max_length=255)
    earthquake_date = models.DateField()
    search_start_date = models.DateField()
    search_end_date = models.DateField()
    nearest_distance = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.city.name} between {self.search_start_date.strftime("%B %d, %Y")} and {self.search_end_date.strftime("%B %d, %Y")}: " \
               f"The closest Earthquake to {self.city.name} was a M {self.earthquake_magnitude} - " \
               f"{self.earthquake_location} on {self.earthquake_date.strftime("%B %d, %Y")}"
