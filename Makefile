lint:
	poetry run flake8 config bot users

test:
	poetry run pytest --cov=config --cov=bot --cov=users

test-coverage:
	poetry run pytest --cov=config --cov-report xml

install:
	poetry install

selfcheck:
	poetry check

check: selfcheck test lint

migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

static:
	poetry run python manage.py collectstatic

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) config.wsgi

dev:
	poetry run python manage.py runserver

#start-bot:
#	poetry run bot