# 💻 About

A system that will use the USGS Earthquake public data set.<br>
By default, the system will search for earthquakes above M 5.0, between 2 given dates (start_date and end_date), and give as result what was the city and the earthquake with the smallest distance between them.<br>
You can do this using [Django admin](http://localhost:8080/admin/earthquakes/city/earthquakes/search/), [DRF](http://localhost:8080/earthquakes/api/search/?start_date=2024-01-01&end_date=2024-10-14) or [*curl](.github/curl_sh.png).<br>
We have some interesting points:<br>
 - Totally Dockerized
 - Use of [Django Templates](.github/result_querying_usgs_api.png)
 - Use of Redis for [Caching](.github/result_redis_cache.png) the API response and avoiding duplicate search results (24h). The response is cached based on the search parameters, and the system avoids creating duplicate search results for the same parameters by checking if an entry already exists in the SearchResult table before creating a new one.
 - Tests with Pytest
 - [Images](.github)

#### * curl

```bash
curl -s "http://localhost:8080/earthquakes/api/search/?start_date=2024-01-01&end_date=2024-10-13" | jq .
```
<br>

# 🥞 Stack

- [Python v3.12](https://www.python.org/doc/)
- [Django v5.1](https://docs.djangoproject.com/en/5.1/)
- [Django REST Framework v3.15](https://www.django-rest-framework.org/community/release-notes/#315x-series)
- [Pytest v8.3](https://pypi.org/project/pytest/8.3.3/)
- PostgreSQL
- Redis

## ⚙️ Setting up the project

### ⚠️ Requirements

To execute locally you will need only [docker](https://docs.docker.com/engine/install/) and [docker compose](https://docs.docker.com/compose/install/).

## 🆙 Running the project

First, clone the project:

### HTTPS

```bash
git clone https://github.com/jvictor-am/django_earthquake.git
```

### SSH

```bash
git clone git@github.com:jvictor-am/django_earthquake.git
```

Now run on sh:

```bash
docker-compose up --build
```

If you need a clean up run:

```bash
docker-compose down --volumes --remove-orphans
```

You can now access [localhost:8080/admin](http://localhost:8080/admin) using admin as username and password (they were created with [create_superuser.py](./django_earthquake/management/commands/create_superuser.py))

You can run the tests with:

```bash
docker-compose exec web sh -c "poetry run pytest"
```

## Features

### Creat new city

 - [Django admin](http://localhost:8080/admin/earthquakes/city/add/)
 - [DRF](http://localhost:8080/earthquakes/api/cities/)

### Search for the nearest Earthquake above 5.0 (default) magnitude among the cities registered in the City table

 - [Django admin](http://localhost:8080/admin/earthquakes/city/earthquakes/search/)
 - [DRF](http://localhost:8080/earthquakes/api/search/?start_date=2024-01-01&end_date=2024-10-14)
