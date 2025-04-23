FROM python:3.13.3-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python - --version 1.8.3 && \
    poetry config virtualenvs.create false && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /accbot

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-root --no-ansi && \
    playwright install --with-deps chromium

COPY . .
