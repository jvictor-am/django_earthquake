from django.db import migrations
 
 
def create_initial_cities(apps, schema_editor):
    City = apps.get_model('earthquakes', 'City')
    cities = [
        {"name": "Los Angeles, CA", "latitude": 34.0522, "longitude": -118.2437},
        {"name": "San Francisco, CA", "latitude": 37.7749, "longitude": -122.4194},
        {"name": "Tokyo, Japan", "latitude": 35.682839, "longitude": 139.759455},
    ]
    for city in cities:
        City.objects.create(**city)
 
 
class Migration(migrations.Migration):
    dependencies = [
        ('earthquakes', '0001_initial'),
    ]
 
    operations = [
        migrations.RunPython(create_initial_cities),
    ]
