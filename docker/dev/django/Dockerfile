# define an alias for the specific python version used in this file.
FROM docker.io/python:3.12.7-slim-bookworm

ARG BUILD_ENVIRONMENT=dev
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
   build-essential \
   libpq-dev \
   git \
   curl \
   wait-for-it \
   && rm -rf /var/lib/apt/lists/*

RUN pip install -U uv
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"

COPY pyproject.toml .
RUN uv sync --extra ${BUILD_ENV}

COPY ./docker/dev/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/dev/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

# copy application code to WORKDIR
COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint"]
