FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONPATH=/opt/convert
ENV ENV=development
ENV LOG_FILE=/var/log/api/zapo.log


RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    gcc \
    libpcre3 \
    libpcre3-dev \
    python3-dev \
    default-libmysqlclient-dev

## Making log file
RUN mkdir /var/log/api

WORKDIR /opt/convert

# Installing poetry to manage dependencies
RUN pip install poetry

COPY poetry.lock pyproject.toml ./

# Project initialization:
RUN poetry config settings.virtualenvs.create false \
 && poetry update $(test "$ENV" == production && echo "--no-dev") --no-interaction --no-ansi

# Making the user and group to application uwsgi
RUN groupadd -r convert && useradd -r -g convert convert

USER convert

#Run docker-entrypoint.sh script.
ENTRYPOINT [ "sh", "docker-entrypoint.sh" ]

CMD [ "uwsgi", "--ini", "config/uwsgi/uwsgi.ini"]

COPY --chown=convert:convert . ./

EXPOSE 8080
