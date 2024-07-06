FROM python:3.9-alpine3.13

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./requirements.txt /tmp/requirements.txt

COPY ./src /src
WORKDIR /src
EXPOSE 8000

ARG DEV=false
RUN python -m venv /py && \
    # upgrade pip image
    /py/bin/pip install --upgrade pip && \
    # install postgresql-client
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache libffi-dev && \
    # Set up a virtual dependence package - group packages and then delete them
    apk add --update --no-cache --virtual .tmp-build-deps \
    # List packages to install psycopg2
    build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    # delete tmp folder
    rm -rf /tmp && \
    # delete packages listed on line 20
    apk del .tmp-build-deps && \
    # add user diferent to root
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

ENV PATH="/py/bin:$PATH"

USER django-user
