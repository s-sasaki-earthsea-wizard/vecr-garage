# Include .env file
include .env
export

# Define the Phony targets
.PHONY: docker-build docker-up docker-down docker-build-up docker-restart docker-logs docker-ps docker-clean member-manager-shell member-manager-start member-manager-stop member-manager-restart member-database-shell member-database-start member-database-stop member-database-restart storage-shell storage-start storage-stop storage-restart member-manager-shell

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
# Backend-db-operation service commands
# ------------------------------------------------------------

backend-db-registration-shell: ## Open a shell into the backend-db-registration container
	$(COMPOSE) -p $(PROJECT_NAME) exec backend-db-registration /bin/bash

backend-db-registration-start: ## Start the backend-db-registration container
	$(COMPOSE) -p $(PROJECT_NAME) start backend-db-registration

backend-db-registration-stop: ## Stop the backend-db-registration container
	$(COMPOSE) -p $(PROJECT_NAME) stop backend-db-registration

backend-db-registration-restart: ## Restart the backend-db-registration container
	$(COMPOSE) -p $(PROJECT_NAME) restart backend-db-registration

backend-db-registration-clean: ## Clean the backend-db-registration container
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes --rmi all --remove-orphans

# ------------------------------------------------------------
# Backend-llm-response service commands
# ------------------------------------------------------------

backend-llm-response-shell: ## Open a shell into the backend-llm-response container
	$(COMPOSE) -p $(PROJECT_NAME) exec backend-llm-response /bin/bash

backend-llm-response-start: ## Start the backend-llm-response container
	$(COMPOSE) -p $(PROJECT_NAME) start backend-llm-response

backend-llm-response-stop: ## Stop the backend-llm-response container
	$(COMPOSE) -p $(PROJECT_NAME) stop backend-llm-response

backend-llm-response-restart: ## Restart the backend-llm-response container
	$(COMPOSE) -p $(PROJECT_NAME) restart backend-llm-response

backend-llm-response-clean: ## Clean the backend-llm-response container
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes --rmi all --remove-orphans

# ------------------------------------------------------------
# Member database service commands
# ------------------------------------------------------------

db-member-shell: ## Open a shell into the member database container
	$(COMPOSE) -p $(PROJECT_NAME) exec db-member /bin/bash

db-member-start: ## Start the member database container
	$(COMPOSE) -p $(PROJECT_NAME) start db-member

db-member-stop: ## Stop the member database container
	$(COMPOSE) -p $(PROJECT_NAME) stop db-member

db-member-restart: ## Restart the member database container
	$(COMPOSE) -p $(PROJECT_NAME) restart db-member

# ------------------------------------------------------------
# Storage service commands
# ------------------------------------------------------------

storage-shell: ## Open a shell into the storage container
	$(COMPOSE) -p $(PROJECT_NAME) exec storage /bin/bash


# ------------------------------------------------------------
# Member manager service commands
# ------------------------------------------------------------

member-manager-shell: ## Open a shell into the member manager container
	$(COMPOSE) -p $(PROJECT_NAME) exec member-manager /bin/bash

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