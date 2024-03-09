start-db:
	docker-compose up -d

stop-db:
	docker-compose down

clear-db:
	docker-compose down -v

db-logs:
	docker-compose logs -f

.PHONY: up down build rebuild logs