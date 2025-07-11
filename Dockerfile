FROM python:3.13 AS base

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml* ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=false
EXPOSE 8000

FROM base AS development
COPY . .
RUN poetry install && \
    pip install uvicorn


CMD ["poetry", "run", "dev"]

FROM base AS production
COPY . .
RUN poetry install && \
    pip install uvicorn

CMD ["poetry","run","prod"]
