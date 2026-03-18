.PHONY: install dev run test format lint clean docker-build docker-run

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --port 8000

worker:
	celery -A app.celery_app worker --loglevel=info

run-all:
	(trap 'kill 0' SIGINT; uvicorn app.main:app --reload --port 8000 & celery -A app.celery_app worker --loglevel=info)

test:
	pytest

format:
	black app/
	isort app/

lint:
	ruff check app/
	mypy app/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

docker-build:
	docker build -t discovr-ai-service .

docker-run:
	docker run -p 8000:8000 --env-file .env discovr-ai-service
