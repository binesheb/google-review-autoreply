FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY config ./config
COPY knowledge ./knowledge
COPY frontend ./frontend
COPY entrypoint.sh ./entrypoint.sh

RUN pip install --no-cache-dir . \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
