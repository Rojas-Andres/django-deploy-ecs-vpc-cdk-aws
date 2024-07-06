FROM public.ecr.aws/docker/library/python:3.11.9

ARG ENVIRONMENT=default
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/
COPY ./src /usr/src/app/

COPY start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./requirements.txt /usr/src/app

RUN apt update && apt install -y supervisor dos2unix curl && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN dos2unix /usr/local/bin/start.sh

EXPOSE 8000
ENTRYPOINT ["start.sh"]
