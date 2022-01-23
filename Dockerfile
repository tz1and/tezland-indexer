FROM python:3.10-slim-buster

# todo: don't run as root?

RUN pip install poetry

WORKDIR /landex
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY ./src ./src

WORKDIR /landex/src

RUN poetry run dipdup -c dipdup.yml -c dipdup.docker.yml init

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]