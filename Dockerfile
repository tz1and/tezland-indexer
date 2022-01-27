FROM python:3.10-slim-buster
ARG extra_dipdup_conf

# add group and user with homedir
RUN groupadd -r landex && useradd -m -l -g landex landex
USER landex

WORKDIR /home/landex/indexer
ENV PATH="/home/landex/.local/bin:${PATH}"

RUN pip install --upgrade pip
RUN pip install poetry

COPY --chown=landex:landex ./ ./

RUN poetry config virtualenvs.create false && poetry install --no-dev

RUN poetry run dipdup -c dipdup.yml -c dipdup.docker.yml $extra_dipdup_conf init

ENTRYPOINT ["poetry", "run", "dipdup"]
CMD ["-c", "dipdup.yml", "-c", "dipdup.docker.yml", "run"]