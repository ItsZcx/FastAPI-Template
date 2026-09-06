FROM python:3.10-alpine3.20

# Force the stdout and stderr streams to the terminal (container logs)
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry==2.3.2

WORKDIR /code

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

COPY .env ./

EXPOSE 8080

CMD ["poetry", "run", "fastapi", "run", "src/main.py", "--reload", "--port", "8080"]
