#
# Django image
#
FROM python:3.9.16-alpine3.16 as django

ARG build_cache_version=20200107

RUN apk add --update postgresql-client --no-cache\
    bash \
    p7zip \
    gettext \
    libzmq \
    python3 \
    postgresql-dev \
    build-base \
    musl-dev \
    python3-dev \
    zeromq-dev \
    libzmq \
    jpeg-dev \
    zlib-dev \
    libxslt-dev \
    libxml2-dev \
    linux-headers \
    py3-setuptools \
    curl \
    libc-dev \
    gcc \
    libffi-dev

RUN pip install --upgrade pip setuptools wheel \
    && pip install six

# Install Poetry
WORKDIR /root
RUN curl -sSL https://install.python-poetry.org/ | python3 -
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /srv/app
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && PIP_NO_CACHE_DIR=false poetry install --no-cache

EXPOSE 8000/tcp

COPY docker/django/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh && ln -s /usr/local/bin/docker-entrypoint.sh /
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["python", "-Wd", "manage.py", "runserver", "--nostatic", "0.0.0.0:8000"]
#CMD ["python", "-Wd", "manage.py", "runprofileserver", "--use-cprofile", "--prof-path=/srv/app/", "0.0.0.0:8000"]
#CMD ["gunicorn","biblored.wsgi", "-b", "0.0.0.0:8000", "--config", "gunicorn_config.py"]
#CMD ["uwsgi", "--processes", "4", "--harakiri", "30", "--harakiri-verbose", "--http", ":8000", "--module", "biblored.wsgi"]
