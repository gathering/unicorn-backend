<h1 align="center">UNICORN 🦄</h1>
<p align="center">Unified Net-based Interface for Competition Organization, Rules and News.</p>


### Running locally

Either run `docker-compose up` or ...

1. Install dependencies - `make setup`

2. Set PostgreSQL up locally
   1. Install Postgresql (e.g. with `brew install postgresql`)
   2. Run it, the defaults should work, i.e. `postgres -D /usr/local/var/postgres`
   3. Create required role `CREATE ROLE postgres WITH LOGIN`

3. Export variables in .env.development - `export $(cat .env.development)`

4. Run app with `make run` or `make run-docker` - you may want to run `export DATABASE_HOST=localhost` first (or use /etc/hosts file to map db to localhost)

### Contributing

Ensure you have `pre-commit` installed - `brew install pre-commit` (using brew is preferred - adding pre-commit dependencies to your Python environment can cause libraries versions to drift)

Run `pre-commit install` (or `make setup`) to have it check your staged changes before allowing you to commit. To skip the pre-commit checks (usually not recommended, but helpful when you'd want to save WIP or similar), use `git commit --no-verify`.

## Docker 🐳

To start UNICORN development in Docker, you have to install Docker on your computer. Then you can run `docker-compose up` from the project root.

Before running you need to ensure that `run_app.sh` is executable (`chmod +x run_app.sh`).
