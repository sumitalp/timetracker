FROM python:3.8.4-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get -y update \
    && apt-get install -y \
        fonts-font-awesome \
        libffi-dev \
        libgdk-pixbuf2.0-0 \
        libpango1.0-0 \
        python-dev \
        python-lxml \
        shared-mime-info \
        libcairo2 \
        libpq-dev gcc \
    && apt-get -y clean

ADD ./requirements /app/requirements
RUN apt-get update && apt-get install git -y && apt-get install iputils-ping -y
RUN pip install -r /app/requirements/local.txt --no-cache-dir
RUN pip install psycopg2

COPY . /app
RUN useradd backend
RUN chown -R backend:backend /app
USER backend
RUN ./manage.py collectstatic --no-input