run:
	cd src; poetry run dipdup init; poetry run dipdup run

run-clean:
	cd src; poetry run dipdup init; poetry run dipdup schema wipe; poetry run dipdup run

clean:
	cd src; poetry run dipdup schema wipe

docker-build:
	docker-compose -f docker-compose.indexer.yml build

docker-up:
	docker-compose -f docker-compose.indexer.yml up -d

docker-down:
	docker-compose -f docker-compose.indexer.yml down -v

docker-push:
	docker save -o tezland-indexer-latest.tar tezland-indexer:latest
	rsync tezland-indexer-latest.tar docker-compose.indexer.yml nginx.conf .env.production tz1and.com:/home/yves/docker
	ssh tz1and.com "source .profile; cd docker; docker load -i tezland-indexer-latest.tar; mv .env.production .env; mv nginx.conf nginx/conf/indexer.conf; rm tezland-indexer-latest.tar"
	rm tezland-indexer-latest.tar
