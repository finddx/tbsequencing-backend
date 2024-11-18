FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN  mkdir /app
WORKDIR /app

RUN apt update && apt install -y postgresql-client

COPY Pipfile* ./

RUN pip install --no-cache-dir --upgrade pip pipenv \
    && pipenv install --system --dev --deploy
