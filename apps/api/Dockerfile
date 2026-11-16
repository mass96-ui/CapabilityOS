FROM python:3.12-slim@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base AS dependencies
COPY apps/api/requirements-runtime.txt /tmp/requirements-runtime.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --requirement /tmp/requirements-runtime.txt \
    && rm /tmp/requirements-runtime.txt

FROM base AS runtime
ENV PATH="/opt/venv/bin:${PATH}"

RUN groupadd --system --gid 10001 capabilityos \
    && useradd --system --uid 10001 --gid capabilityos --home-dir /app --no-create-home capabilityos \
    && mkdir --parents /app \
    && chown capabilityos:capabilityos /app

COPY --from=dependencies /opt/venv /opt/venv
COPY --chown=10001:10001 apps/api/app ./app
COPY --chown=10001:10001 apps/api/alembic ./alembic
COPY --chown=10001:10001 apps/api/alembic.ini ./alembic.ini

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health/ready', timeout=4)"

STOPSIGNAL SIGTERM

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
