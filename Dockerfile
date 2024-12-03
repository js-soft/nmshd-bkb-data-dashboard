FROM python:3.12-bookworm AS builder
ARG POETRY_VERSION="1.8.3"
WORKDIR /app
RUN pip install poetry==${POETRY_VERSION}
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
COPY pyproject.toml ./
RUN poetry install --no-root --only main \
    && rm -rf $POETRY_CACHE_DIR


FROM python:3.12-slim-bookworm AS runner
WORKDIR /app

# Dependencies for healthcheck and odbc driver
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg2 \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Install odbc driver for worker processes
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

ENV DASHBOARD_NUM_WORKERS=4
EXPOSE 5000/tcp

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY main.py .
RUN /app/.venv/bin/pip install gunicorn==23.0.0

# Note: We use exec to replace the shell process with the gunicorn process to receive UNIX signals (and use the shell for environment variable processing)
ENTRYPOINT ["/bin/sh", "-c", "exec /app/.venv/bin/python -m gunicorn --workers ${DASHBOARD_NUM_WORKERS} --bind 0.0.0.0:5000 'main:create_app()'"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=2s --retries=3 CMD curl -f http://localhost:5000/health || exit 1
