EXTRA_ARGS?=

#localconfig = -c dipdup.yml
localconfig = -c dipdup.yml -c dipdup.dev.local.yml

run:
	source .venv/bin/activate && dipdup $(localconfig) init && dipdup $(localconfig) run

run-clean:
	source .venv/bin/activate && dipdup $(localconfig) schema wipe --force && dipdup $(localconfig) init && dipdup $(localconfig) run

clean:
	source .venv/bin/activate && dipdup $(localconfig) schema wipe --force

# Dev
DOCKER_DEV_CONF?=-f docker-compose.indexer.yml -f docker-compose.indexer.dev.yml

dev-docker-build:
	TAG=dev docker-compose ${DOCKER_DEV_CONF} build --pull $(EXTRA_ARGS)

dev-docker-up:
	TAG=dev docker-compose ${DOCKER_DEV_CONF} up -d
	TAG=dev docker-compose ${DOCKER_DEV_CONF} logs -f

dev-docker-down:
	TAG=dev docker-compose ${DOCKER_DEV_CONF} down -v

dev-docker-cycle:
	make dev-docker-down
	make dev-docker-build
	make dev-docker-up

# Staging
DOCKER_STAGING_CONF?=-f docker-compose.indexer.yml -f docker-compose.indexer.staging.yml

staging-docker-build:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} build --pull $(EXTRA_ARGS)

staging-docker-up:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} up -d -V
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} logs -f

staging-docker-logs:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} logs -f

staging-docker-down:
	TAG=staging docker-compose ${DOCKER_STAGING_CONF} down

staging-docker-cycle:
	make staging-docker-down
	make staging-docker-build
	make staging-docker-up
	make staging-docker-logs

# Prod
docker-build:
	TAG=latest docker-compose -f docker-compose.indexer.yml build --pull

docker-up:
	TAG=latest docker-compose -f docker-compose.indexer.yml up -d -V

docker-down:
	TAG=latest docker-compose -f docker-compose.indexer.yml down

docker-push:
	docker save -o tezland-indexer-latest.tar tezland/indexer:latest
	rsync tezland-indexer-latest.tar docker-compose.indexer.yml docker_postgresql_multiple_databases.sh nginx.conf .env.production tz1and.com:/home/yves/docker
	ssh tz1and.com "source .profile; cd docker; docker load -i tezland-indexer-latest.tar; mv .env.production .env; mv nginx.conf nginx/conf/indexer.conf"
#	; rm tezland-indexer-latest.tar"
	rm tezland-indexer-latest.tar
