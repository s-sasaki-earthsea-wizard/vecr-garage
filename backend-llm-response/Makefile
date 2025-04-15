.PHONY: db-member-connection help

default: help

db-member-connection:  ## Check connection to db-member
	PGPASSWORD=$${MEMBER_DB_PASSWORD} psql -h $${MEMBER_DB_HOST} -p $${MEMBER_DB_PORT} -U $${MEMBER_DB_USER} -d $${MEMBER_DB_NAME} -c "\conninfo"


help: ## Show this help message
	@echo "------------------------------------------------------------------------------"
	@echo "Usage: make [target]"
	@echo "------------------------------------------------------------------------------"
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo "------------------------------------------------------------------------------"

