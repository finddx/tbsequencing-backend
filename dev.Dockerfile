FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN  mkdir /app
WORKDIR /app

COPY Pipfile* ./

RUN apt update && apt upgrade -y  \
    && pip install --no-cache-dir --upgrade pip pipenv \
    && pipenv install --system --dev --deploy

COPY . ./

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py"]
