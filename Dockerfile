FROM python:3.10-alpine3.20

# Force the stdout and stderr streams to the terminal (container logs)
ENV PYTHONUNBUFFERED=1 \
    UV_NO_CACHE=1

RUN pip install --no-cache-dir uv==0.12.10

WORKDIR /code

# Install runtime dependencies from the committed lock file (dev tooling is excluded)
COPY pyproject.toml uv.lock ./

RUN uv sync --no-dev --frozen

EXPOSE 8080

CMD ["uv", "run", "--frozen", "fastapi", "run", "src/main.py", "--reload", "--port", "8080"]
