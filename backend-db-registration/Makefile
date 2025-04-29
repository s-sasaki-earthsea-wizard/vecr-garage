.PHONY: show_sample_data_in_bucket help register-members set-pythonpath

default: help

set-pythonpath:  ## Set PYTHONPATH environment variable
	@echo "Setting PYTHONPATH to /app/src"
	@export PYTHONPATH="/app/src:$$PYTHONPATH"

db-member-connection:  ## Check connection to db-member
	PGPASSWORD=$$MEMBER_DB_PASSWORD psql -h $$MEMBER_DB_HOST -p $$MEMBER_DB_PORT -U $$MEMBER_DB_USER -d $$MEMBER_DB_NAME -c "\conninfo"

show_sample_data_in_bucket:  ## Show sample data in bucket
	python src/storage/storage_client.py

help: ## Show this help message
	@echo "------------------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo "------------------------------------------------------------------------------"
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "------------------------------------------------------------------------------"

register-members: set-pythonpath  ## Register members from YAML files
	docker-compose -p vecr-garage exec backend-db-registration python -m src.scripts.register_members

register-human-members: set-pythonpath  ## Register human members from YAML files
	python -m src.scripts.register_members --human

register-virtual-members: set-pythonpath  ## Register virtual members from YAML files
	python -m src.scripts.register_members --virtual