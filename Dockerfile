FROM busybox as downloader
RUN wget https://github.com/snyk/driftctl/releases/download/v0.20.0/driftctl_linux_amd64
RUN chmod +x driftctl_linux_amd64

FROM python:3.9-slim

ENV PYTHONPATH=/usr/src \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.0.0

WORKDIR /usr/src

COPY --from=downloader /driftctl_linux_amd64 /usr/local/bin/driftctl

COPY pyproject.toml /usr/src/
COPY poetry.lock /usr/src/

RUN pip install poetry>=${POETRY_VERSION} && \
    poetry install --no-interaction --no-ansi
