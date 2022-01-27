devconfig = -c dipdup.yml -c dipdup.dev.yml -c dipdup.dev.local.yml

run:
	source .venv/bin/activate; dipdup $(devconfig) init; dipdup $(devconfig) run

run-clean:
	source .venv/bin/activate; dipdup $(devconfig) schema wipe; dipdup $(devconfig) init; dipdup $(devconfig) run

clean:
	source .venv/bin/activate; dipdup $(devconfig) schema wipe

dev-docker-build:
	TAG=dev docker-compose -f docker-compose.indexer.yml -f docker-compose.indexer.dev.yml build --no-cache

dev-docker-up:
	TAG=dev docker-compose -f docker-compose.indexer.yml -f docker-compose.indexer.dev.yml up -d

dev-docker-down:
	TAG=dev docker-compose -f docker-compose.indexer.yml -f docker-compose.indexer.dev.yml down -v

docker-build:
	TAG=latest docker-compose -f docker-compose.indexer.yml build

docker-up:
	TAG=latest docker-compose -f docker-compose.indexer.yml up -d

docker-down:
	TAG=latest docker-compose -f docker-compose.indexer.yml down -v

docker-push:
	docker save -o tezland-indexer-latest.tar tezland-indexer:latest
	rsync tezland-indexer-latest.tar docker-compose.indexer.yml nginx.conf .env.production tz1and.com:/home/yves/docker
	ssh tz1and.com "source .profile; cd docker; docker load -i tezland-indexer-latest.tar; mv .env.production .env; mv nginx.conf nginx/conf/indexer.conf; rm tezland-indexer-latest.tar"
	rm tezland-indexer-latest.tar
