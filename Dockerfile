FROM python:3.13.7-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 FLASK_APP=helpdesk:create_app HELPDESK_STATE_DIR=/data
WORKDIR /app
RUN groupadd --gid 10001 helpdesk && useradd --uid 10001 --gid 10001 --no-create-home helpdesk && mkdir /data && chown 10001:10001 /data && chmod 700 /data
COPY requirements.txt requirements.lock ./
RUN pip install --disable-pip-version-check -r requirements.lock
COPY helpdesk/ helpdesk/
COPY migrations/ migrations/
COPY docs/backlog.yml docs/backlog.yml
COPY scripts/entrypoint.sh scripts/entrypoint.sh
USER 10001:10001
EXPOSE 8000
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "30", "--access-logfile", "-", "--access-logformat", "%(m)s %(U)s %(s)s %(L)s", "--error-logfile", "-", "helpdesk:create_app()"]

FROM base AS test
USER root
COPY requirements-dev.txt requirements-dev.lock ./
RUN pip install --disable-pip-version-check -r requirements-dev.lock
COPY tests/ tests/
USER 10001:10001
ENTRYPOINT ["python", "-m", "pytest"]
CMD ["-q", "-p", "no:cacheprovider"]

FROM base AS runtime
