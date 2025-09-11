# backend-db-registrationサービス専用のMakeタスク
# サービス固有の操作を定義

.PHONY: backend-db-registration-test backend-db-registration-logs backend-db-registration-health backend-db-registration-webhook-test

backend-db-registration-test: ## Run tests for backend-db-registration service
	@echo "Running tests for backend-db-registration service..."
	docker exec -it vecr-garage-backend-db-registration pytest tests/ -v
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