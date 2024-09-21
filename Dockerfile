FROM python:3.10-alpine3.20

# Force the stdout and stderr streams to the terminal (container logs)
ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry==1.8.3

WORKDIR /code

COPY pyproject.toml ./

RUN if poetry show --without dev > /dev/null 2>&1; then \
    poetry install --without dev --no-root; \
    else \
    poetry install --no-root; \
    fi && rm -rf $POETRY_CACHE_DIR

COPY .env ./

EXPOSE 8080

CMD ["poetry", "run", "fastapi", "run", "src/main.py", "--reload", "--port", "8080"]
