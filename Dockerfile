FROM python:3.10-slim-bullseye
ARG EXTRA_DIPDUP_CONF
ARG TZKT_URL
ENV TZKT_URL $TZKT_URL

WORKDIR /indexer

# alpine - doesn't work tho. some pytz error.
#RUN apk update && apk add gcc libc-dev python3-dev libffi-dev

# debian - if git needed
RUN apt update
RUN apt install postgresql-client -y

#RUN pip install --upgrade pip
RUN pip install poetry

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY ./ ./

RUN poetry run dipdup -c dipdup.yml -c dipdup.docker.yml $EXTRA_DIPDUP_CONF init

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]