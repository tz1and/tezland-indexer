FROM python:3.10-slim-buster
ARG EXTRA_DIPDUP_CONF
ARG TZKT_URL
ENV TZKT_URL $TZKT_URL

WORKDIR /indexer

#RUN apt update
#RUN apt install git -y
#RUN pip install --upgrade pip
RUN pip install poetry

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY ./ ./

RUN poetry run dipdup -c dipdup.yml -c dipdup.docker.yml $EXTRA_DIPDUP_CONF init

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]