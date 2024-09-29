# Makefile for Docker commands

# Variables
IMAGE_NAME = ocrktp
IMAGE_TAG = v1
CONTAINER_NAME = ocrktp-container

# Phony targets
.PHONY: build run stop clean

# Build the Docker image
build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Run the Docker container
run:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 8080:8080 \
		--env-file .env \
		-e FLASK_ENV=production \
		-v $(PWD)/logs:/app/logs \
		--restart unless-stopped \
		$(IMAGE_NAME):$(IMAGE_TAG)

# Stop and remove the container
stop:
	docker stop $(CONTAINER_NAME)
	docker rm $(CONTAINER_NAME)

# Remove the Docker image
clean:
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG)

# Remove dangling images
prune:
	docker image prune -f

# All-in-one command to rebuild and restart
restart: stop clean build run

migrate:
	flask db upgrade