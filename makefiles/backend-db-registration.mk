# backend-db-registrationサービス専用のMakeタスク
# サービス固有の操作を定義

.PHONY: backend-db-registration-test backend-db-registration-test-rollback backend-db-registration-logs backend-db-registration-health backend-db-registration-webhook-test backend-db-registration-register-members backend-db-registration-register-members-single backend-db-registration-register-human backend-db-registration-register-virtual backend-db-registration-db-connection backend-db-registration-start-api backend-db-registration-check-api backend-db-registration-start backend-db-registration-stop backend-db-registration-clean

backend-db-registration-test: ## Run tests for backend-db-registration service
	@echo "Running tests for backend-db-registration service..."
	docker exec vecr-garage-backend-db-registration pytest tests/ -v
	@echo "Tests completed!"

backend-db-registration-logs: ## Show logs for backend-db-registration service
	@echo "Showing logs for backend-db-registration service..."
	docker logs vecr-garage-backend-db-registration --tail=100 -f

backend-db-registration-health: ## Check health of backend-db-registration service
	@echo "Checking health of backend-db-registration service..."
	@curl -s http://localhost:3000/health || echo "❌ Service not responding"
	@echo ""
	@curl -s http://localhost:3000/health/storage-monitor || echo "❌ Storage monitor not responding"

backend-db-registration-webhook-test: ## Test webhook endpoint
	@echo "Testing webhook endpoint..."
	@curl -X POST http://localhost:3000/webhook/test \
		-H "Content-Type: application/json" \
		-s | python3 -m json.tool || echo "❌ Webhook test failed"

backend-db-registration-shell: ## Access backend-db-registration container shell
	@echo "Accessing backend-db-registration container shell..."
	docker exec -it vecr-garage-backend-db-registration /bin/bash

backend-db-registration-restart: ## Restart backend-db-registration service
	@echo "Restarting backend-db-registration service..."
	docker restart vecr-garage-backend-db-registration
	@echo "Service restarted!"

backend-db-registration-test-rollback: ## Test rollback and validation functionality
	@echo "Testing rollback and validation functionality..."
	docker exec vecr-garage-backend-db-registration python -m tests.test_rollback_functionality
	@echo "Rollback tests completed!"

backend-db-registration-register-members: ## Register members from YAML files (batch mode)
	@echo "Registering members in batch mode..."
	docker exec vecr-garage-backend-db-registration python -m src.scripts.register_members
	@echo "Batch registration completed!"

backend-db-registration-register-members-single: ## Register members from YAML files (individual mode)  
	@echo "Registering members in individual mode..."
	docker exec vecr-garage-backend-db-registration python -m src.scripts.register_members_single
	@echo "Individual registration completed!"

backend-db-registration-register-human: ## Register human members only (batch mode)
	@echo "Registering human members only..."
	docker exec vecr-garage-backend-db-registration python -m src.scripts.register_members --human
	@echo "Human member registration completed!"

backend-db-registration-register-virtual: ## Register virtual members only (batch mode) 
	@echo "Registering virtual members only..."
	docker exec vecr-garage-backend-db-registration python -m src.scripts.register_members --virtual
	@echo "Virtual member registration completed!"

backend-db-registration-db-connection: ## Check database connection
	@echo "Checking database connection..."
	docker exec vecr-garage-backend-db-registration /bin/sh -c 'cd /app && \
		if [ -z "$$MEMBER_DB_PASSWORD" ] || [ -z "$$MEMBER_DB_HOST" ] || [ -z "$$MEMBER_DB_PORT" ] || [ -z "$$MEMBER_DB_USER" ] || [ -z "$$MEMBER_DB_NAME" ]; then \
			echo "Error: Required environment variables are not set"; \
			echo "Please check Docker container environment variables"; \
			exit 1; \
		fi && \
		PGPASSWORD="$$MEMBER_DB_PASSWORD" psql -h "$$MEMBER_DB_HOST" -p "$$MEMBER_DB_PORT" -U "$$MEMBER_DB_USER" -d "$$MEMBER_DB_NAME" -c "\\conninfo"'

backend-db-registration-start-api: ## Start FastAPI server (development)
	@echo "Starting FastAPI server in development mode..."
	docker exec vecr-garage-backend-db-registration python -c "import uvicorn; uvicorn.run('src.app:app', host='0.0.0.0', port=3000, reload=True)"

backend-db-registration-check-api: ## Check API server status
	@echo "Checking API server status..."
	@curl -s http://localhost:3000/ || echo "❌ API server not responding"
	@echo ""
	@curl -s http://localhost:3000/health || echo "❌ Health endpoint not responding"

backend-db-registration-start: ## Start the backend-db-registration container
	@echo "Starting backend-db-registration container..."
	docker start vecr-garage-backend-db-registration
	@echo "Container started!"

backend-db-registration-stop: ## Stop the backend-db-registration container
	@echo "Stopping backend-db-registration container..."
	docker stop vecr-garage-backend-db-registration
	@echo "Container stopped!"

backend-db-registration-clean: ## Clean the backend-db-registration container and volumes
	@echo "Cleaning backend-db-registration container and volumes..."
	@read -p "Are you sure you want to remove backend-db-registration container and its volumes? [y/N] " confirm && \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			docker stop vecr-garage-backend-db-registration || true; \
			docker rm vecr-garage-backend-db-registration || true; \
			echo "Container and volumes cleaned successfully!"; \
		else \
			echo "Operation cancelled."; \
		fi