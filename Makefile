.DEFAULT_GOAL := run

init: prepare run migrate createsuperuser

prepare:
	@cp .env.testing .env

run:
	@docker compose up -d

migrate:
	@docker compose exec web python unicorn/manage.py migrate

createsuperuser:
	@echo "Creating a Django superuser. Please fill in the details:"
	@docker compose exec web python unicorn/manage.py createsuperuser

loadseed:
	@docker compose exec web python unicorn/manage.py loaddata unicorn/seed.json

test:
	@docker compose exec web coverage run unicorn/manage.py test unicorn

coverage:
	@docker compose exec web coverage report -m
	@docker compose exec web coverage html -d unicorn/htmlcov
	@open unicorn/htmlcov/index.html