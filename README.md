<h1 align="center">UNICORN 🦄</h1>
<p align="center">Unified Net-based Interface for Competition Organization, Rules and News.</p>


## Running with Docker 🐳

To start UNICORN development in Docker, you have to install Docker on your computer. Then you can run `docker-compose up -d` from the project root.

When running for the first time, or after creating migrations, remember to also run `docker-compose exec web python /unicorn/unicorn/manage.py migrate`

Create first local superuser: `docker-compose exec web python /unicorn/unicorn/manage.py createsuperuser`


## Running locally

0. Make sure you have Python 3.8 and pipenv installed

1. Set PostgreSQL up locally
   1. Install Postgresql (e.g. with `brew install postgresql`)
   2. Run it, the defaults should work, i.e. `postgres -D /usr/local/var/postgres`
   3. Create required role `CREATE ROLE postgres WITH LOGIN`

2. Install dependencies - `make setup`

3. Export variables in .env.development - `export $(cat .env.development)`

4. Run app with `make run` or `make run-docker` - you may want to run `export DATABASE_HOST=localhost` first (or use /etc/hosts file to map db to localhost)


## Contributing

Ensure you have `pre-commit` installed - `brew install pre-commit` (or replace brew with your package manager, such as yum or apt)

Run `pre-commit install` (or `make setup`) to have it check your staged changes before allowing you to commit. To skip the pre-commit checks (usually not recommended, but helpful when you'd want to save WIP or similar), use `git commit --no-verify`.


# Authentication providers
## Keycloak
1. Set up according to upstream docs: https://python-social-auth.readthedocs.io/en/latest/backends/keycloak.html
2. Create a mapper to get group memberships
   - Go to Clients -> [client name] -> Mappers
   - Click Create
   - Select "Group Membership" for Mapper Type
   - Name the mapper "groups"