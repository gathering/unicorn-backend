FROM python:3.10-slim

WORKDIR /unicorn
RUN pip install pipenv

COPY Pipfile.lock .
COPY Pipfile .

ENV PYTHON=python

RUN pipenv install --system --deploy --ignore-pipfile

COPY . .

CMD gunicorn unicorn.wsgi --bind 0.0.0.0:80 -w 3 --chdir unicorn/ --access-logfile '-' --error-logfile '-'
