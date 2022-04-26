EXTRA_ARGS?=

devconfig = -c dipdup.yml -c dipdup.dev.local.yml

run:
	source .venv/bin/activate && dipdup $(devconfig) init && dipdup $(devconfig) run

run-clean:
	source .venv/bin/activate && dipdup $(devconfig) schema wipe --force && dipdup $(devconfig) init && dipdup $(devconfig) run

clean:
	source .venv/bin/activate && dipdup $(devconfig) schema wipe --force

# Dev
DOCKER_DEV_CONF?=-f docker-compose.indexer.yml -f docker-compose.indexer.dev.yml

dev-docker-build:
	TAG=dev docker-compose ${DOCKER_DEV_CONF} build $(EXTRA_ARGS)

dev-docker-up:
	TAG=dev docker-compose ${DOCKER_DEV_CONF} up -d
	TAG=dev docker-compose ${DOCKER_DEV_CONF} logs -f

dev-docker-down:
	TAG=dev docker-compose ${DOCKER_DEV_CONF} down -v

# Staging
DOCKER_STAGING_CONF?=-f docker-compose.indexer.yml -f docker-compose.indexer.staging.yml

staging-docker-build:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} build $(EXTRA_ARGS)

staging-docker-up:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} up -d -V
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} logs -f

staging-docker-logs:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} logs -f

staging-docker-down:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} down

# Prod
docker-build:
	TAG=latest docker-compose -f docker-compose.indexer.yml build

docker-up:
	TAG=latest docker-compose -f docker-compose.indexer.yml up -d -V

docker-down:
	TAG=latest docker-compose -f docker-compose.indexer.yml down

docker-push:
	docker save -o tezland-indexer-latest.tar tezland/indexer:latest
	docker save -o tezland-metadata-latest.tar tezland/metadata:latest
	rsync tezland-indexer-latest.tar tezland-metadata-latest.tar docker-compose.indexer.yml docker_postgresql_multiple_databases.sh nginx.conf .env.production tz1and.com:/home/yves/docker
	ssh tz1and.com "source .profile; cd docker; docker load -i tezland-indexer-latest.tar; docker load -i tezland-metadata-latest.tar; mv .env.production .env; mv nginx.conf nginx/conf/indexer.conf"
#	; rm tezland-indexer-latest.tar"
	rm tezland-indexer-latest.tar
	rm tezland-metadata-latest.tar
