# Albumz - Manage your music album collection and wishlist with Django
Albumz is a Django powered, containerized  portfolio web application created in order to showcase skills in Django, Docker, and modern backend practices.
# Prerequisites
In order to run this project locally, the following software is required to be installed:
- `Docker`
- `Docker-compose`
# Features
- User authentication (registration, login/logout, views restriction to authenticated users)
- Album collection & wishlist management (CRUD, custom logic for adding albums both to the collection and the wishlist, moving album from wishlist to collection, removing album from wishlist if it was added to collection)
- Searchable and scrollable album table
- Django REST API endpoints with custom actions (e.g. average album ratings of a user by genre)
# Tech stack
- **Backend**: Python 3.13, Django 5, Django REST Framework
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Containerization**: Docker, Docker Compose, Nginx
- **Testing**: Pytest (with fixtures)
- **Other tools**: Black, ruff, pre-commit, etc.
# Project structure
- albumz_app/ - core app logic (+ REST)
- accounts/ - authentication logic
- tests/ - pytest tests with fixtures
- templates/ - Django templates
- staticfiles/ - CSS/JSS assets (Bootstrap)
# Setup & installation (Dev setup)
1. Clone this repo into your local machine.
2. Create a file at the root of the project (at the same folder level where Dockerfiles and Docker-compose files are) called `dev.env`. Inside, provide `DEBUG=True` and set `DJANGO_SECRET_KEY` to any random string (usable only for dev).
3. Run `docker-compose -f docker-compose.dev.yaml up --build -d` (remember to have the Docker Engine running!)
4. Visit `localhost:8000/accounts/register/` to create an account and get started with using the app.
# Production deployment
Production setup consists of 3 Docker containers, namely postgresql (the database), web (the albumz app and the accounts app) and nginx reverse proxy server. Nginx listens on port 80 and transfers the incoming traffic into port 8000, on which the app listens. Lastly, the app communicates with the postgresql container.
## Prod setup guide
1. Clone this repo into your local machine.
2. Create a file at the root of the project (at the same folder level where Dockerfiles and Docker-compose files are) called `prod.env`. Inside, provide the following:
   
    - `DEBUG=False`
    - `DJANGO_SECRET_KEY=<your-production-secret>`
    - `POSTGRESQL_DATABASE=<db-name>`
    - `POSTGRESQL_USERNAME=<db-user>`
    - `POSTGRESQL_PASSWORD=<db-password>`
    - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web`
3. Run `docker-compose -f docker-compose.prod.yaml up --build -d` (remember to have the Docker Engine running!)
4. Visit `localhost/accounts/register/` to create an account and get started with using the app.
# Tests
The code is thoroughly tested (124+ tests) accross all of its use-cases, be it views, models or api endpoints. In order to run the tests, open up a terminal inside the spun up web container (in either dev or prod setups) and simply run `pytest`.
# Usage
After registering and logging in:
- Add albums to your collection or wishlist.
- Move album from wishlist to collection by clicking on "see details" button next to the album.
- Try adding an album with the same title and artist twice, an album with date of publication in the future, etc.
- Visit `localhost/api` (prod setup) or `localhost:8000/api` in order to make use of the Django REST Framework part of the app (check out "Average rating" located in Extra Actions in Albums List. In order to view average rating by genre, add a `?genre=<GENRE>` suffix, for example: `http://localhost/api/albums/average-rating/?genre=POP`).
