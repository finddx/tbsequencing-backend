# TB-Kb Backend

Based on Django Rest Framework.

## Project setup

There are 2 main setup options to make project run on your machine,
which one do you need usually depends on your purposes.

Also, it is possible to run a project in both setups.

### Local setup

Local setup is good for development and debugging purposes.

To run the webservice locally,
you need **python >=3.10**, **pip** and **pipenv** installed.
Also, **Postgres** database connection is required.

If you're going to work with submission flow
(upload FASTQ files or use S3 storage backend),
you will need AWS connection, with at least 1 S3 bucket read/write access.

> You can spin up local database using `docker-compose`,
> by default it will be available at `localhost:5433/postgres`
> with username:password `postgres:postgres`
>
> ```commandline
> docker-compose up -d db
> ```

1. Initialize virtual environment and install packages.
   `--dev` flag will install packages, required to run tests and pre-commit hooks:

   ```commandline
   pipenv install --dev
   ```

2. If you are going to make changes to the repo,
   install **pre-commit** hooks into it:

   ```commandline
   pipenv run pre-commit install
   ```

   > You can exclude `pipenv run` from commands, after activating pipenv shell.
   > To activate it, run `pipenv activate` from project root.

3. Copy `.env.dist` into `.env`, and update necessary variables.

   > More on env vars and configuration in [Configuration](#configuration) section.

4. Run database migrations.

   `migrate` command will apply any pending migrations to the database.

   `postmigrate` command will perform necessary updates in database,
   such as updating frontend domain URL,
   setting custom postgres `SEARCH PATH`,
   filling genphen tables with initial data,
   and, for non-production environment, creating sample users.

   ```commandline
   pipenv run python manage.py migrate
   pipenv run python manage.py postmigrate
   ```

   > More on database change management and migrations
   > in [Database change management](#database-change-management) section.

5. Run local server.

   By default, it resides on [http://localhost:8000](http://localhost:8000)

   ```commandline
   pipenv run python manage.py runserver
   ```

6. When needed, you can run tests:

   ```commandline
    pipenv run pytest
    ```

   The tests will utilize current database connection.
   More on testing in [Testing](#testing) stage.

### docker-compose setup

docker-compose setup can be used by dependent projects, such as frontend,
to quick-start backend application with all necessary dependencies,
including Swagger UI for interactive API schema view.

Unlike local setup, docker-compose setup runs web application in production mode,
means serving static files through `nginx`, and Django through WSGI-server `gunicorn`.

To spin up docker-compose setup, run command:

```commandline
docker-compose up -d --build
```

This will update and start all services.

After services were launched, migrate database to the latest state:

```commandline
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py postmigrate
```

This will apply any necessary migrations, as well as fill database with initial data.

docker-compose services include:

#### Postgres database

Exposed on [localhost:5433/postgres](postgresql://postgres:postgres@localhost:5433/postgres)
with `postgres:postgres` credentials by default.

Can be used as standalone database service for [local setup](#local-setup) as well.

#### Mailcatcher

Intercepts all Django's outgoing emails, and shows them in a web interface.

Web interface is on [localhost:1080](http://localhost:1080),
SMTP server is on [localhost:1025](smtp://localhost:1025).

#### Nginx proxy

Proxies Django webapp and serves its static files.
Exposed on [localhost:8000](http://localhost:8000).

#### Django webapp

Exposed on [localhost:8001](http://localhost:8001),
but access through [nginx](#nginx-proxy) should be preferred over it.

#### Swagger UI

Interactive API schema exploration.
Exposed on [localhost:2080](http://localhost:2080).
Pre-pointed to backend API schema that is currently located inside project.

## Configuration

Django application is configured via environment variables.
They can be passed directly
or defined in `.env` file inside project root for **local setup**,
and `.dc.env` for **docker-compose setup**.

`.dc.env` already have some variables pre-defined,
according to `docker-compose.yml` settings.
You can change them as needed,
for instance if you want to connect different database to a docker-compose setup.

Reference file with all available variables and their descriptions
located at project root and called `.env.dist`.

To configure local setup, copy `.env.dist` file to `.env`,
and change all necessary variables.

## Making changes

To make changes to the project,
you will need to deploy a [local setup](#local-setup).

Standard approach to make changes:

- Make any necessary changes.
- Run `makemigrations` command to generate migrations
  if there are any changes to managed models:

  ```commandline
  pipenv run python manage.py makemigrations
  ```

- Run `migrate` command to apply new migrations (if any):

  ```commandline
  pipenv run python manage.py migrate
  ```

- [Run tests](#testing). Write additional tests if needed.
- [Update API schema](#updating-openapi-schema).
- Commit changes, fixing pre-commit checks suggestions.

### Testing

In order to launch tests against application,
you will need **local setup** configured.
After you have your local backend app working,
from project root run the command to launch tests:

```commandline
pipenv run pytest
```

### Updating OpenAPI schema

If your changes affected API, regenerate OpenAPI schema
to automatically reflect the changes.
Run the command from project root:

```commandline
pipenv run python manage.py generateschema --format openapi-json --file api/static/api/schema.json
```

After that, you can review changes (with text editor or [Swagger UI](#swagger-ui)).
If all good, feel free to commit the schema changes alongside with code changes.

## Managing database changes

See [Database change management](./docs/database-change-management.md) section
on how to deal with database changes.


## Connecting a local Django web container with a remote database

Use an ssh tunnel to allow the local container to connect to the remote database.
Use the `-g (Allows remote hosts to connect to local forwarded ports.)` and `-L (Specifies that connections to the given TCP port or Unix socket on the local (client) host are to be forwarded to the given host and port, or Unix socket, on the remote side.)` options.

```
ssh -g -L ${local_port}:${remote_database_host_name}:${remote_port} ec2-user@${ec2_hostname/ip_address}
```

If you use the default neworking mode in docker compose (i.e. `bridge`), you must the correct local ip address for the database host. 
It cannot be `localhost` (unless you change the networking mode to `host`). Usually it's `172.17.0.1`. 

Modify the following environment variable in `.dc.env`. You can fetch from secret manager the master username/master password.
```
DB_HOST=172.17.0.1
DB_PORT=5432
DB_USER=tbkbmasteruser
DB_PASSWORD=averysecretpassword
DB_NAME=tbkbdb
```
Only ever connect to the staging/test remote database. Connecting via SSH to the production database should be impossible anyway.
