.PHONY: show_sample_data_in_bucket help register-members register-members-single register-human-members register-virtual-members db-member-connection test start-api test-webhook check-api

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

start-api:  ## Start FastAPI server with webhook endpoints (for development)
	@echo "🚀 Starting FastAPI server with webhook endpoints..."
	@echo "📡 Webhook endpoint: http://localhost:3000/webhook/file-change"
	@echo "📊 API documentation: http://localhost:3000/docs"
	@echo "🔍 Health check: http://localhost:3000/health"
	@echo ""
	@echo "💡 Note: In production, the API server starts automatically with the Docker container."
	@echo "   To set up webhook notifications, run in another terminal:"
	@echo "   python src/scripts/setup_webhook.py setup"
	@echo ""
	@echo "🔍 Checking if server is already running..."
	@if [ -f /proc/1/cmdline ] && grep -q "uvicorn" /proc/1/cmdline 2>/dev/null; then \
		echo "✅ API server process is already running (container entrypoint)"; \
		echo ""; \
		echo "💡 This appears to be running in a Docker container with uvicorn as entrypoint."; \
		echo "💡 To stop the server, use: docker-compose -p vecr-garage stop backend-db-registration"; \
		echo "💡 To view logs, use: docker-compose -p vecr-garage logs -f backend-db-registration"; \
		echo "💡 To start a new server outside container, run from host machine: make start-api"; \
		exit 0; \
	elif curl -s http://localhost:3000/health > /dev/null 2>&1; then \
		echo "✅ API server is already running on port 3000"; \
		echo "📊 Server status: http://localhost:3000/health"; \
		echo "📡 Webhook endpoint: http://localhost:3000/webhook/file-change"; \
		echo ""; \
		echo "💡 To stop the server, use: docker-compose -p vecr-garage stop backend-db-registration"; \
		echo "💡 To view logs, use: docker-compose -p vecr-garage logs -f backend-db-registration"; \
		exit 0; \
	else \
		echo "🚀 Starting new FastAPI server..."; \
		uvicorn src.app:app --host 0.0.0.0 --port 3000 --reload; \
	fi

test-webhook:  ## Test webhook functionality
	@echo "🧪 Testing webhook functionality..."
	@echo "Make sure the API server is running with 'make start-api' first."
	@echo ""
	python src/scripts/test_webhook.py

check-api:  ## Check API server status
	@echo "🔍 Checking API server status..."
	@echo ""
	@if [ -f /proc/1/cmdline ] && grep -q "uvicorn" /proc/1/cmdline 2>/dev/null; then \
		echo "✅ API server process is running (container entrypoint)"; \
		echo ""; \
		echo "💡 This is running in a Docker container with uvicorn as entrypoint."; \
		echo "💡 To check from host machine:"; \
		echo "   curl http://localhost:3000/health"; \
		echo "💡 To view logs:"; \
		echo "   docker-compose -p vecr-garage logs -f backend-db-registration"; \
	elif curl -s http://localhost:3000/health > /dev/null 2>&1; then \
		echo "✅ API server is running and healthy"; \
		echo "📊 Health check response:"; \
		curl -s http://localhost:3000/health; \
	else \
		echo "❌ API server is not running or not accessible"; \
		echo "💡 To start the server:"; \
		echo "   - Production: docker-compose -p vecr-garage up -d backend-db-registration"; \
		echo "   - Development: make start-api"; \
		exit 1; \
	fi