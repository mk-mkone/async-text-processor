build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

stop:
	docker-compose stop

restart:
	docker-compose down
	docker-compose build
	docker-compose up -d

reset:
	docker-compose down -v

logs-worker:
	docker-compose logs -f worker

logs:
	docker-compose logs -f

freeze:
	. venv/bin/activate && pip install worker && pip freeze > worker/requirements.txt

formate:
	isort worker/app worker/core worker/tests
	black worker/app worker/core worker/tests

test:
	pytest

.PHONY: logs
