.PHONY: help test makemigrations migrate run .venv develop build

help: ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

APP_NAME=unicorn
PYTHON ?= $(if $(shell pipenv),$(shell which pipenv) run python,$(shell which python))
COVERAGE ?= $(if $(shell pipenv),$(shell which pipenv) run coverage,coverage)
BIN ?= $(if $(shell pipenv),$(shell which pipenv) run)
ENV_FILE?=.env.development

include ${ENV_FILE}
export $(shell sed 's/=.*//' ${ENV_FILE})

test: ## Run Django testsuite with `manage.py test` command
	${PYTHON} unicorn/manage.py test unicorn --verbosity=2

test-coverage: ## Run Django testsuite with `manage.py test` command - with coverage reporting
	${COVERAGE} run unicorn/manage.py test unicorn --verbosity=2
	${COVERAGE} report

show-coverage: ## Create coverage report and open it in browser
	${COVERAGE} html && python -mwebbrowser file://$$PWD/htmlcov/index.html

ci-codecov-upload: ## Uploads coverage report to Codecov.io
	${BIN} codecov

makemigrations: ## Run Django makemigrations to create migration
	${PYTHON} unicorn/manage.py makemigrations

migrate: ## Run Django migration script to apply changes
	${PYTHON} unicorn/manage.py migrate

run: migrate ## Run Django app
	${PYTHON} unicorn/manage.py runserver 0.0.0.0:8000

setup: ## Set up environment for development
	pipenv install --dev
	pre-commit install

build: ## Build the container
	docker build -t $(APP_NAME) .

run-docker: build ## Runs the container locally, with development env file
	docker run --name $(APP_NAME) --env-file=$(ENV_FILE) -t -p 8000:8000 $(APP_NAME)

clean-docker: ## removes running docker container
	docker stop $(APP_NAME) ; \
	docker rm $(APP_NAME)
