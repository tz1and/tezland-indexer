run:
	cd src; poetry run dipdup init; poetry run dipdup run

run-clean:
	cd src; poetry run dipdup init; poetry run dipdup schema wipe; poetry run dipdup run

clean:
	cd src; poetry run dipdup schema wipe

#start:
#	docker-compose -f docker-compose.dev.yml up
#
#stop:
#	docker-compose -f docker-compose.dev.yml down
#
#db-start:
#	docker-compose -f docker-compose.dev.yml up -d db