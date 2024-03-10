# Define default command to run when no target is specified
all: build up

# Build the Docker images
build:
	docker-compose build

# Start up the containers in the background
up:
	docker-compose up -d

# Stop the containers
down:
	docker-compose down

# Remove the containers and their volumes
clean:
	docker-compose down -v

# Access the Python container's shell
app-shell:
	docker-compose exec app /bin/bash

# Follow the logs of all containers
logs:
	docker-compose logs -f

# Rebuild the images and restart the containers
rebuild: down build up

# Show this help
help:
	@echo "Available commands:"
	@echo "  all      - Build images and start containers"
	@echo "  build    - Build the Docker images"
	@echo "  up       - Start up the containers in the background"
	@echo "  down     - Stop the containers"
	@echo "  clean    - Remove the containers and their volumes"
	@echo "  app-shell- Access the Python container's shell"
	@echo "  logs     - Follow the logs of all containers"
	@echo "  rebuild  - Rebuild the images and restart the containers"
	@echo "  help     - Show this help message"
