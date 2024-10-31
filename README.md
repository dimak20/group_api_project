# Library API Service 📖

<a id="readme-top"></a>

![Django DRF Logo](logos/django-rest.jpg)
![Redis Logo](logos/redis-image.svg)
![Celery Logo](logos/celery.png)
![Prometheus Logo](logos/prometheus.png)
![Grafana Logo](logos/grafana.png)
![Stripe Logo](logos/stripe.png)
![Telegram Logo](logos/telegram.png)

> Group REST project 

This is a Django REST Framework (DRF) powered API for managing a library system, including books, authors, borrowers, and related entities. The API is designed to handle essential functionalities for a library management system, such as book cataloging, borrowing (checkouts) and returning of books, and user interactions. Additionally, it supports sending notifications via Telegram or email to keep users informed about due dates, overdue books, and other important updates.


## Run service on your machine

1. Clone repository  
```shell
git clone https://github.com/dimak20/group_api_project.git
cd group_api_project
```
2. Then, create and activate .venv environment  
```shell
python -m venv env
```
For Unix system
```shell
source venv/bin/activate
```

For Windows system

```shell
venv\Scripts\activate
```

3. Install requirements.txt by the command below  


```shell
pip install -r requirements.txt
```

4. You need to migrate
```shell
python manage.py migrate
```
5. (Optional) Also you can load fixture data
```shell
python manage.py loaddata data.json
```
email: admin@gmail.com

password: test_password

6. And finally, create superuser and run server

```shell
python manage.py createsuperuser
python manage.py runserver # http://127.0.0.1:8000/
```

## Run with Docker (simple version)

1. Clone repository  
```shell
git clone https://github.com/dimak20/group_api_project.git
cd group_api_project
```
2. Create .env file and set up environment variables
```shell
DATABASE_ENGINE=postgresql
POSTGRES_PASSWORD=airport
POSTGRES_USER=airport
POSTGRES_DB=airport
POSTGRES_HOST=db
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=true
DATABASE_URL=postgresql://airport:airport@db:5432/airport
USE_REDIS=false
```

3. Build and run docker containers 


```shell
docker-compose -f docker-compose.light.yaml up --build
```

4. (Optionally) Create super user inside docker container or load data

```shell
docker-compose exec library_service python manage.py createsuperuser
python manage.py loaddata data.json
```
email: admin@gmail.com

password: test_password


5. Access the API at http://localhost:8000/api/v1/

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Run with Docker (advanced monitoring version)

1. Clone repository  
```shell
git clone https://github.com/dimak20/group_api_project.git
cd group_api_project
```
2. Create .env file and set up environment variables
```shell
DATABASE_ENGINE=postgresql
POSTGRES_PASSWORD=postgresqlpass
POSTGRES_USER=postgresuser
POSTGRES_DB=postgresdb
POSTGRES_HOST=postgreshost
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data/pgdata
DJANGO_SECRET_KEY=123123
DJANGO_DEBUG=true
REDIS_URL=redis://redis:6379/0
REDIS_HOST=redis
REDIS_PORT=6379
DATABASE_URL=
CELERY_BROKER_URL=redis://redis:6379/0
USE_REDIS=true
PGADMIN_DEFAULT_EMAIL=admin@gmail.com
PGADMIN_DEFAULT_PASSWORD=admin
TELEGRAM_TOKEN=1234567890:AAABBB
STRIPE_TEST_SECRET_KEY=sk_test_AaSs
STRIPE_TEST_PUBLIC_KEY=pk_test_BbNn
WEBHOOK_SECRET=whsec_nnGR
HOME_DOMAIN=localhost
DEFAULT_FROM_EMAIL=service@gmail.com
SENDGRID_API_KEY=SG.ydhgn
AWS_ACCESS_KEY_ID=nhgn
AWS_S3_REGION_NAME=eu-north-1
AWS_SECRET_ACCESS_KEY=hgdnd
AWS_STORAGE_BUCKET_NAME=name
USE_AWS=true
FINE_MULTIPLIER=2

```

3. Build and run docker containers 


```shell
docker-compose -f docker-compose.advanced.yml up --build
```

4. (Optionally) Create super user inside docker container or load data

```shell
docker-compose exec library_service python manage.py createsuperuser
python manage.py loaddata data.json
```
email: admin@gmail.com

password: test_password


5. Access the API at http://localhost:8000/api/v1/


6. Monitoring
```shell
Prometheus: http://localhost:9090
Grafana: http://localhost:3000
Beat scheduler: http://localhost:8000/admin/ -> tasks
Flower: http://localhost:5555
PGAdmin: http://localhost:3333
Redis-command: http://localhost:8081
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Project configuration

Your project needs to have this structure


```plaintext
Project
├── books
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── filters.py
|   ├── models.py
│   ├── ordering.py
|   ├── serializers.py
|   ├── signals.py
|   ├── tasks.py
│   ├── urls.py
│   └── views.py
|
├── checkout
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── filters.py
|   ├── models.py
│   ├── ordering.py
|   ├── serializers.py
|   ├── signals.py
|   ├── tasks.py
│   ├── urls.py
│   └── views.py
|
├── group_api_library
│   ├── __init__.py
│   ├── asgi.py
│   ├── permissions.py
│   ├── celery.py
│   ├── settings.py
|   ├── wsgi.py
│   └── urls.py
│
|
├── management_utils
|   └── management
|   |  └── commands
|   |     └── wait_for_db.py
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── models.py
│   ├── urls.py
│   └── views.py
|
|
├── notifications
|   └── management
|   |  └── commands
|   |     └── run_bot.py
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── bot.py
|   ├── email_utils.py
│   ├── models.py
|   ├── tasks.py
|   ├── tests.py
|   ├── urls.py
│   └── views.py
|
|
├── payments
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── exceptions.py
|   ├── serializers.py
│   ├── models.py
|   ├── services.py
|   ├── tests.py
|   ├── urls.py
│   └── views.py
|   
├── media
│   
├── logos
│   
├── templates
|
├── user
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── managers.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .dockerignore
│
├── .env
|
├── .env.sample
│
├── .gitignore
│
├── docker-compose.light.yaml
│
├── docker-compose.advanced.yaml
│
├── Dockerfile
│
├── manage.py
│
├── prometheus.yml
│
├── README.md
|
└── requirements.txt
```


## Usage
* Library Endpoints: Manage books.
* Checkout Endpoints: Create and manage checkouts/borrowings, make payments.
* User Endpoints: User registration, login, and token authentication.
* Payements Endpoints: Manually create payments or retrieve payment session details.
* Hint - use http://localhost:8000/api/v1/doc/swagger/ to see all the endpoints

## Features
* JWT Authentication
* Admin panel /admin/
* Swagger documentation
* Managing checkouts
* Creating books, authors, genres
* Filtering and ordering all models by title, date, year etc.
* Celery usage for background tasks
* Redis usage for caching
* Prometheus usage for service monitoring
* Grafana for visualizing server usage
* Beat for scheduling background tasks

<p align="right">(<a href="#readme-top">back to top</a>)</p>
