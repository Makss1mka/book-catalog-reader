FROM python:3.13

WORKDIR /app

RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-cache

COPY . .

ARG APP_PORT
EXPOSE $APP_PORT

CMD ["poetry", "run", "python", "-m", "src.main"]