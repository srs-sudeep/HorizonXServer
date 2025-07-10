FROM python:3.11-slim AS base

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml* ./
COPY poetry.lock* ./

ENV POETRY_VIRTUALENVS_IN_PROJECT=false
EXPOSE 8010

FROM base AS development
COPY . .
RUN poetry install --no-root && \
    pip install uvicorn && \
    chmod +x scripts/start.sh

CMD ["./scripts/start.sh"]

FROM base AS production
COPY . .
RUN poetry install --no-root && \
    pip install uvicorn

CMD ["poetry","run","prod"]
