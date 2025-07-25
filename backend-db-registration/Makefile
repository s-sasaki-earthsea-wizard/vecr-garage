.PHONY: show_sample_data_in_bucket help register-members register-members-single register-human-members register-virtual-members db-member-connection test

default: help

db-member-connection:  ## Check connection to db-member
	@if [ -z "$$MEMBER_DB_PASSWORD" ] || [ -z "$$MEMBER_DB_HOST" ] || [ -z "$$MEMBER_DB_PORT" ] || [ -z "$$MEMBER_DB_USER" ] || [ -z "$$MEMBER_DB_NAME" ]; then \
		echo "Error: Required environment variables are not set"; \
		echo "Please set the following environment variables:"; \
		echo "  MEMBER_DB_HOST"; \
		echo "  MEMBER_DB_PORT"; \
		echo "  MEMBER_DB_USER"; \
		echo "  MEMBER_DB_PASSWORD"; \
		echo "  MEMBER_DB_NAME"; \
		exit 1; \
	fi
	@echo "Connecting to database..."
	PGPASSWORD="$$MEMBER_DB_PASSWORD" psql -h "$$MEMBER_DB_HOST" -p "$$MEMBER_DB_PORT" -U "$$MEMBER_DB_USER" -d "$$MEMBER_DB_NAME" -c "\conninfo"

show-sample-data-in-bucket:  ## Show sample data in bucket
	python src/storage/storage_client.py

help: ## Show this help message
	@echo "------------------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo "------------------------------------------------------------------------------"
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "------------------------------------------------------------------------------"

register-members:  ## Register members from YAML files (Batch Mode - Recommended)
	@echo "=== Batch Registration Mode ==="
	@echo "Processing all files in a single transaction."
	@echo "If any file has validation errors, all changes will be rolled back."
	python -m src.scripts.register_members

register-members-single:  ## Register members from YAML files (Single Mode - Individual processing)
	@echo "=== Single Registration Mode ==="
	@echo "Processing files individually. Each file is processed separately."
	@echo "Valid files will be registered even if some files have errors."
	python -m src.scripts.register_members_single

register-human-members:  ## Register human members from YAML files (Batch Mode)
	python -m src.scripts.register_members --human

register-virtual-members:  ## Register virtual members from YAML files (Batch Mode)
	python -m src.scripts.register_members --virtual

test:  ## Run tests
	pytest tests/ -v

test-rollback-functionality:  ## Test rollback and validation functionality
	python -m tests.test_rollback_functionality