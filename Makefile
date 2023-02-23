lint:
	poetry run flake8 bot

test:
	poetry run pytest --cov=bot

test-coverage:
	poetry run pytest --cov=bot --cov-report xml

install:
	poetry install

selfcheck:
	poetry check

check: selfcheck test lint

start:
	poetry run bot
