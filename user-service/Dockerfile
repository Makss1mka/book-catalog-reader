FROM python:3.13

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-cache

COPY . .

ARG APP_PORT
EXPOSE $APP_PORT

CMD ["poetry", "run", "python", "-m", "src.main"]