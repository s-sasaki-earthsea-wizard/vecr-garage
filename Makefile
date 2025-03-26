# Include .env file
include .env
export

# Define the Phony targets
.PHONY: build up down build-up restart logs ps clean backend-shell backend-start backend-stop backend-restart

# Define the default target
default: help

# Define docker compose command
COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

PROJECT_NAME := vecr-office

# ------------------------------------------------------------
# Docker commands
# ------------------------------------------------------------

build: ## Build the services
	$(COMPOSE) -p $(PROJECT_NAME) build

up: ## Start the services
	$(COMPOSE) -p $(PROJECT_NAME) up -d

down: ## Stop the services
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes

build-up: ## Build and start the services
	$(COMPOSE) -p $(PROJECT_NAME) up --build -d

restart: ## Restart the services
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes
	$(COMPOSE) -p $(PROJECT_NAME) up --build -d

logs: ## Show the logs of the services
	$(COMPOSE) -p $(PROJECT_NAME) logs -f

ps: ## Show the status of the services
	$(COMPOSE) -p $(PROJECT_NAME) ps

clean: ## Stop and remove all containers, volumes, and images
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
# Database container commands
# ------------------------------------------------------------

db-shell: ## Open a shell into the database container
	$(COMPOSE) -p $(PROJECT_NAME) exec db /bin/bash

db-start: ## Start the database container
	$(COMPOSE) -p $(PROJECT_NAME) start db

db-stop: ## Stop the database container
	$(COMPOSE) -p $(PROJECT_NAME) stop db

db-restart: ## Restart the database container
	$(COMPOSE) -p $(PROJECT_NAME) restart db

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