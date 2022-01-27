FROM python:3.10-slim-buster
ARG extra_dipdup_conf

# todo: don't run as root?

RUN pip install poetry

WORKDIR /landex
COPY ./ ./

RUN poetry config virtualenvs.create false && poetry install --no-dev

RUN poetry run dipdup -c dipdup.yml -c dipdup.docker.yml $extra_dipdup_conf init

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]