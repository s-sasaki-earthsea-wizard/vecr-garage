# Include .env file
include .env
export

# Use bash for shell commands (required for 'source' command)
SHELL := /bin/bash

# Define the Phony targets
.PHONY: docker-build docker-up docker-down docker-build-up docker-restart docker-logs docker-ps docker-clean member-manager-shell member-manager-start member-manager-stop member-manager-restart member-database-shell member-database-start member-database-stop member-database-restart storage-shell storage-start storage-stop storage-restart member-manager-shell s3-cp s3-cp-sample s3-ls s3-setup-profile

# Define the default target
default: help

# Define docker compose command
COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; else echo "docker compose"; fi)

# Define environment variables
PROJECT_NAME := $(PROJECT_NAME)
MEMBER_DB_USER := $(MEMBER_DB_USER)
MEMBER_DB_NAME := $(MEMBER_DB_NAME)

# ------------------------------------------------------------
# Docker commands
# ------------------------------------------------------------

docker-build: ## Build the services
	@if [ -f .envrc ]; then source .envrc; fi && $(COMPOSE) -p $(PROJECT_NAME) build

docker-up: ## Start the services
	@if [ -f .envrc ]; then source .envrc; fi && $(COMPOSE) -p $(PROJECT_NAME) up -d

docker-down: ## Stop the services
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes

docker-build-up: ## Build and start the services
	@if [ -f .envrc ]; then source .envrc; fi && $(COMPOSE) -p $(PROJECT_NAME) up --build -d

docker-restart: ## Restart the services
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes
	@if [ -f .envrc ]; then source .envrc; fi && $(COMPOSE) -p $(PROJECT_NAME) up --build -d

docker-logs: ## Show the logs of the services
	$(COMPOSE) -p $(PROJECT_NAME) logs -f

docker-ps: ## Show the status of the services
	$(COMPOSE) -p $(PROJECT_NAME) ps

docker-clean: ## Stop and remove all containers, volumes, and images
	$(COMPOSE) -p $(PROJECT_NAME) down --volumes --rmi all --remove-orphans

# ------------------------------------------------------------
# Backend-db-operation service commands
# ------------------------------------------------------------

# Removed: backend-db-registration targets moved to makefiles/backend-db-registration.mk

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

db-member-psql: ## Connect to the member database using psql
	$(COMPOSE) -p $(PROJECT_NAME) exec db-member psql -U $(MEMBER_DB_USER) -d $(MEMBER_DB_NAME)

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

s3-cp: ## Copy files to MinIO storage using AWS CLI s3 cp command
	@echo "Copying files to MinIO storage..."
	@echo "Usage: make s3-cp LOCAL_FILE=<path_to_local_file> S3_KEY=<s3_object_key>"
	@echo "Example: make s3-cp LOCAL_FILE=./sample.yml S3_KEY=data/human_members/sample.yml"
	@if [ -z "$(LOCAL_FILE)" ] || [ -z "$(S3_KEY)" ]; then \
		echo "Error: LOCAL_FILE and S3_KEY parameters are required"; \
		echo "Example: make s3-cp LOCAL_FILE=./sample.yml S3_KEY=data/human_members/sample.yml"; \
		exit 1; \
	fi
	@if [ ! -f "$(LOCAL_FILE)" ]; then \
		echo "Error: Local file '$(LOCAL_FILE)' does not exist"; \
		exit 1; \
	fi
	aws s3 cp $(LOCAL_FILE) s3://$(MINIO_BUCKET_NAME)/$(S3_KEY) \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp $(LOCAL_FILE) s3://$(MINIO_BUCKET_NAME)/$(S3_KEY) \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request

# モジュール化されたMakefileをinclude
include makefiles/storage.mk
include makefiles/yml-file-operations.mk
include makefiles/backend-db-registration-tests.mk
include makefiles/integration.mk
include makefiles/backend-db-registration.mk
include makefiles/backend-llm-response.mk

# 便利なエイリアスと後方互換性
s3-cp-samples: samples-copy ## Copy normal sample files to MinIO storage
s3-cp-test-cases: test-cases-copy ## Copy test case files to MinIO storage
s3-cp-sample: samples-copy ## Backward compatibility: Copy normal sample files

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