.DEFAULT_GOAL := run

init: prepare run migrate createsuperuser

prepare:
	@cp .env.testing .env

run:
	@docker compose up -d

runbuild:
	@docker compose up -d --build

migrate:
	@docker compose exec web python unicorn/manage.py migrate

createsuperuser:
	@echo "Creating a Django superuser. Please fill in the details:"
	@docker compose exec web python unicorn/manage.py createsuperuser

loadseed:
	@docker compose exec web python unicorn/manage.py loaddata unicorn/seed.json

test:
	@docker compose exec web coverage run unicorn/manage.py test unicorn
	@docker compose exec web coverage html -d unicorn/htmlcov

coverage:
# 	@docker compose exec web coverage report -m
	@open unicorn/htmlcov/index.html