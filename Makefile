lint:
	poetry run flake8 bot

test:
	poetry run pytest --cov=fluent_mind

test-coverage:
	poetry run pytest --cov=fluent_mind --cov-report xml

install:
	poetry install

selfcheck:
	poetry check

check: selfcheck test lint

start-bot:
	poetry run bot

dev:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) fluent_mind.wsgi