ARG WORKDIR="/app"

FROM python:3.13-alpine AS base

# Remember to also update in pyproject.toml
ENV POETRY_VERSION=2.2.1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1


FROM base AS deps

ARG WORKDIR
WORKDIR ${WORKDIR}

# We need a compiler and some stuff
RUN apk add build-base libffi-dev \
    && rm -rf /var/cache/apk/*

# Install poetry separated from system interpreter
RUN pip install -U pip setuptools \
    && pip install poetry==${POETRY_VERSION}


# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true
RUN poetry install --only main


FROM base

ARG WORKDIR
WORKDIR ${WORKDIR}

COPY --from=deps ${WORKDIR}/.venv ${WORKDIR}/.venv
ENV PATH="${WORKDIR}/.venv/bin:$PATH"

COPY . .

EXPOSE 80
CMD ["gunicorn", "unicorn.wsgi", "--bind", "0.0.0.0:80", "--preload", "-w", "6", "--chdir", "unicorn/", "--access-logfile", "-", "--error-logfile", "-"]