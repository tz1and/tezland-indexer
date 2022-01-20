FROM python:3.10-slim-buster

# todo: don't run as root

RUN pip install poetry

WORKDIR /landex
COPY poetry.lock pyproject.toml /landex/

RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY . /landex

WORKDIR /landex/src

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]