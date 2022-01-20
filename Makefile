run:
	cd src; poetry run dipdup init; poetry run dipdup run

run-clean:
	cd src; poetry run dipdup init; poetry run dipdup schema wipe; poetry run dipdup run

clean:
	cd src; poetry run dipdup schema wipe

docker-build:
	cd src; poetry run dipdup init
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down -v
