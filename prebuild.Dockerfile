FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN  mkdir /app
WORKDIR /app

COPY Pipfile* ./

RUN pip install --no-cache-dir --upgrade pip==22.1.2 pipenv==2022.6.7\
    && pipenv install --system --deploy
