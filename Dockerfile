FROM python:3.10-slim-buster
ARG extra_dipdup_conf

WORKDIR /indexer

#RUN pip install --upgrade pip
RUN pip install poetry

COPY ./ ./

RUN poetry config virtualenvs.create false && poetry install --no-dev

RUN poetry run dipdup -c dipdup.yml -c dipdup.docker.yml $extra_dipdup_conf init

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]