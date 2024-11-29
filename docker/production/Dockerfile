FROM python:3.12-bookworm AS builder
ARG POETRY_VERSION="1.8.3"
WORKDIR /app
RUN pip install poetry==${POETRY_VERSION}
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
COPY pyproject.toml ./
RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim-bookworm AS runner
# Install curl, gpg for healthcheck and odbc download
RUN apt-get update && apt-get install -y \
curl \
gnupg2 \
&& rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Install odbc driver for worker processes
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=y apt-get install -y \
        msodbcsql18 \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*
WORKDIR /app

# Set environment variables
ARG GUNICORN_VERSION="23.0.0"
ENV GUNICORN_WORKERS=4
ENV SERVER_HOST=0.0.0.0
ENV VIRTUAL_ENV=/app/.venv \
PATH="/app/.venv/bin:$PATH"
EXPOSE 5000/tcp

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY src/ src/
COPY main.py .
RUN pip install gunicorn==${GUNICORN_VERSION}
# env variables cannot be used in array form of entrypoint (cmd-form), but shell format is considered insecure, thus:
COPY --chmod=755 <<EOT /entrypoint.sh
#!/usr/bin/env bash
gunicorn --workers $GUNICORN_WORKERS --bind $SERVER_HOST:5000 "main:create_app()"
EOT
ENTRYPOINT [ "/entrypoint.sh" ]
HEALTHCHECK --interval=30s --timeout=30s --start-period=2s --retries=3 CMD curl -f http://localhost:5000/health || exit 1