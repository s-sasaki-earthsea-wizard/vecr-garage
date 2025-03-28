# Include .env file
include .env
export

# Define the Phony targets
.PHONY: docker-build docker-up docker-down docker-build-up docker-restart docker-logs docker-ps docker-clean backend-shell backend-start backend-stop backend-restart

# Define the default target
default: help

# Define docker compose command
COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

PROJECT_NAME := vecr-office

# ------------------------------------------------------------
# Docker commands
# ------------------------------------------------------------

docker-build: ## Build the services
	$(COMPOSE) -p $(PROJECT_NAME) build

docker-up: ## Start the services
	$(COMPOSE) -p $(PROJECT_NAME) up -d

docker-down: ## Stop the services
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes

docker-build-up: ## Build and start the services
	$(COMPOSE) -p $(PROJECT_NAME) up --build -d

docker-restart: ## Restart the services
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes
	$(COMPOSE) -p $(PROJECT_NAME) up --build -d

docker-logs: ## Show the logs of the services
	$(COMPOSE) -p $(PROJECT_NAME) logs -f

docker-ps: ## Show the status of the services
	$(COMPOSE) -p $(PROJECT_NAME) ps

docker-clean: ## Stop and remove all containers, volumes, and images
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes --rmi all --remove-orphans

# ------------------------------------------------------------
# Backend container commands
# ------------------------------------------------------------

backend-shell: ## Open a shell into the backend container
	$(COMPOSE) -p $(PROJECT_NAME) exec backend /bin/bash

backend-start: ## Start the backend container
	$(COMPOSE) -p $(PROJECT_NAME) start backend

backend-stop: ## Stop the backend container
	$(COMPOSE) -p $(PROJECT_NAME) stop backend

backend-restart: ## Restart the backend container
	$(COMPOSE) -p $(PROJECT_NAME) restart backend

# ------------------------------------------------------------
# Member database container commands
# ------------------------------------------------------------

member-db-shell: ## Open a shell into the member database container
	$(COMPOSE) -p $(PROJECT_NAME) exec member-database /bin/bash

member-db-start: ## Start the member database container
	$(COMPOSE) -p $(PROJECT_NAME) start member-database

member-db-stop: ## Stop the member database container
	$(COMPOSE) -p $(PROJECT_NAME) stop member-database

member-db-restart: ## Restart the member database container
	$(COMPOSE) -p $(PROJECT_NAME) restart member-database

# ------------------------------------------------------------
# Storage container commands
# ------------------------------------------------------------

storage-shell: ## Open a shell into the storage container
	$(COMPOSE) -p $(PROJECT_NAME) exec storage /bin/bash


# ------------------------------------------------------------
# Help
# ------------------------------------------------------------

help: ## Show this help message
	@echo "------------------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo "------------------------------------------------------------------------------"
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "------------------------------------------------------------------------------"