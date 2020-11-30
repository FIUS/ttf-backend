FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN pip install pipenv cymysql

COPY Pipfile /app/
RUN pipenv lock
RUN pipenv install --system

WORKDIR /app

RUN mkdir --parents /app/instance
RUN mkdir --parents /app-mnt/data

COPY docker/prestart.sh /app/
COPY docker/uwsgi.ini /app/
COPY docker/total-tolles-ferleihsystem.conf /app/instance
COPY total_tolles_ferleihsystem /app/total_tolles_ferleihsystem
COPY migrations /app/migrations

ENV FLASK_APP total_tolles_ferleihsystem
ENV MODE production
ENV CONFIG_FILE /app-mnt/total-tolles-ferleihsystem.conf

VOLUME ["/app-mnt"]
