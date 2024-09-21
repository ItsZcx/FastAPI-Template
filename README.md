# FastAPI Template
A FastAPI template that integrates Poetry, Alembic, SQLAlchemy, dotenv, Docker, and PostgreSQL for a fully functional API setup.

Docker is set up to run both a FastAPI and PostgreSQL container.

Alembic files are included as references to help you understand how to modify them. However, as noted in the "Setup" section, you should remove and reinitialize these files before starting your own API project.

## Table of Contents
- [Project Structure](#project-structure)
- [Template Setup](#template-setup)
    - [1. Install Dependencies with Poetry](#1-install-dependencies-with-poetry)
    - [2. Set Up Environment Variables with dotenv](#2-set-up-environment-variables-with-dotenv)
    - [3. Set Up Alembic Database Migrations](#3-set-up-alembic-database-migrations)
    - [4. Run the Template with Docker](#4-run-the-template-with-docker)



## Project Structure
This project strucure is based on [project-structure-consistent--predictable](https://github.com/zhanymkanov/fastapi-best-practices#1-project-structure-consistent--predictable) by zhanymkanov. It has been modified to use poetry and docker instead of venv.

```
fastapi-template
├── alembic/
├── src
│   ├── auth               # package
│   │   ├── config.py        # local configs
│   │   ├── constants.py     # package-specific constants
│   │   ├── dependencies.py  # specific auth router dependencies
│   │   ├── exceptions.py    # package-specific errors
│   │   ├── models.py        # database models
│   │   ├── router.py        # auth router with endpoints
│   │   ├── schemas.py       # pydantic models
│   │   ├── service.py       # package-specific business logic
│   │   └── utils.py         # any other non-business logic functions
│   ├── aws
│   │   ├── client.py        # client model for external service communication
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── schemas.py
│   │   └── utils.py
│   └── package            # copy paste package
│   │   ├── constants.py
│   │   ├── dependencies.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── __init__.py
│   ├── config.py            # global configs (dotenv, etc)
│   ├── models.py            # global database models
│   ├── exceptions.py        # global exceptions
│   ├── pagination.py        # global module e.g. pagination
│   ├── database.py          # database connection related stuff
│   └── main.py
├── tests/
│   ├── auth
│   ├── aws
│   └── posts
├── .env.example             # Variables used/needed in this .env
├── .gitignore
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md
```

1. Store all domain directories inside `src` folder
   1. `src/` - highest level of an app, contains common models, configs, and constants, etc.
   2. `src/main.py` - root of the project, which inits the FastAPI app

2. Each package has its own router, schemas, models, etc.
   1. `config.py` - e.g. specific env vars
   2. `constants.py` - module specific constants and error codes
   3. `dependencies.py` - router dependencies
   4. `exceptions.py` - module specific exceptions, e.g. `PostNotFound`, `InvalidUserData`
   5. `models.py` - for database models
   6. `router.py` - is a core of each module with all the endpoints
   7. `schemas.py` - for pydantic models
   8. `service.py` - module specific business logic
   9. `utils.py` - non-business logic functions, e.g. response normalization, data enrichment, etc.

3. When package requires services or dependencies or constants from other packages - import them with an explicit module name
```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
from src.posts.constants import ErrorCode as PostsErrorCode  # in case we have Standard ErrorCode in constants module of each package
```

## Template Setup

### 1. Install Dependencies with Poetry
Ensure that [Poetry](https://python-poetry.org) is installed. If you plan to use Docker and don't require IDE support for package management, you can skip this step.

1. Update project dependencies, this will also create a virtualenv and install them. (100% they are outdated):
   ```bash
   poetry update
   ```

2. To add or update a package:
   ```bash
   poetry add <package-name>
   ```
   or for development dependencies:
   ```bash
   poetry add --group=dev <package-name>
   ```

### 2. Set Up Environment Variables with dotenv
Environment variables are handled via a `.env` file. The `.env.example` file contains the essential variables required to run this project out of the box.

1. Create a `.env` file at the project root:
   ```bash
   touch .env
   ```

2. Add your environment-specific variables:
   ```bash
    DB_URL=postgresql://postgres:1234@fastapi-postgres:5432/postgres
    ALEMBIC_DB_URL=postgresql://postgres:1234@{POSTGRESQL_CONTAINER_IP}:5432/postgresn
   ```

The `.env` file is used by the `python-dotenv` package to load environment variables into the FastAPI application. To locate the PostgreSQL container's IP address, inspect the Docker network that is created.

### 3. Set Up Alembic Database Migrations
1. Remove alembic example:
   ```bash
   rm -rf alembic/ alembic.ini
   ```
2. Initialize Alembic (creates the alembic dir and alembic.ini):
   ```bash
   alembic init alembic
   ```

3. Configure the `alembic/env.py` file to use your `ALEMBIC_DB_URL` from `.env`:
    ```python
    # Set up ALEMBIC_DB_URL from .env file
    from dotenv import load_dotenv
    load_dotenv()
    ALEMBIC_DB_URL = os.getenv("ALEMBIC_DB_URL")

    # Set up sqlalchemy.url (alembic.ini) variable
    config.set_main_option("sqlalchemy.url", ALEMBIC_DB_URL)

    # Import ALL the models from the app (even if unused)
    from src.database import Base
    from src.package.models import Todos
    ...

    # Set target_metadata
    target_metadata = Base.metadata
    ```

4. Create a new migration script (you can remove --autogenerate and create the change yourself):
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```

5. Apply the migrations:
   ```bash
   alembic upgrade {REVISION_ID}
   ```

### 4. Run the Template with Docker
1. Make sure [Docker](https://docs.docker.com/) is installed on your system.

2. Build and run the Docker containers:
   ```bash
   docker compose up -d
   ```

This will start both the FastAPI app and the PostgreSQL database as Docker containers.

3. To stop the containers (add --volumes to remove persistent PostgeSQL data):
   ```bash
   docker-compose down
   ```
