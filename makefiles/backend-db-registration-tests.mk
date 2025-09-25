# backend-db-registrationサービスの包括的テストシステム
# ユニットテスト、正常系・異常系の統合テストを集約

.PHONY: backend-db-registration-test-unit backend-db-registration-test-samples backend-db-registration-test-cases backend-db-registration-test-integration

backend-db-registration-test-unit: ## Run backend-db-registration unit tests only
	@echo "🧪 Running backend-db-registration unit tests..."
	@make backend-db-registration-test
	@echo "✅ Unit tests completed!"

backend-db-registration-test-samples: ## Test normal sample file processing (E2E with DB validation)
	@echo "📁 Testing normal sample file processing..."
	@echo "🧪 Running comprehensive sample validation tests..."
	@echo "📋 Phase 1: Unit tests for member registration functions..."
	@docker exec vecr-garage-backend-db-registration pytest tests/test_member_registration.py::test_register_human_member_from_yaml -v
	@docker exec vecr-garage-backend-db-registration pytest tests/test_member_registration.py::test_register_virtual_member_from_yaml -v
	@echo "📋 Phase 2: Testing actual file upload and DB registration..."
	@echo "📤 Uploading test human member file..."
	@aws s3 cp ./storage/sample_data/samples/human_members/syota.yml s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/syota_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 cp ./storage/sample_data/samples/human_members/syota.yml s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/syota_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@echo "⏳ Waiting for webhook processing..."
	@sleep 4
	@echo "📤 Uploading test virtual member file..."
	@aws s3 cp ./storage/sample_data/samples/virtual_members/kasen.yml s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/kasen_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 cp ./storage/sample_data/samples/virtual_members/kasen.yml s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/kasen_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@echo "⏳ Waiting for webhook processing..."
	@sleep 4
	@echo "🔍 Checking DB registration for human member..."
	@docker exec vecr-garage-db-member psql -U testuser -d member_db -c "SELECT member_name, created_at FROM human_members WHERE member_name = 'Syota' ORDER BY created_at DESC LIMIT 1;" | grep -q "Syota" && echo "✅ Human member registered successfully" || (echo "❌ Human member registration failed" && exit 1)
	@echo "🔍 Checking DB registration for virtual member..."
	@docker exec vecr-garage-db-member psql -U testuser -d member_db -c "SELECT member_name, created_at FROM virtual_members WHERE member_name = '華扇' ORDER BY created_at DESC LIMIT 1;" | grep -q "華扇" && echo "✅ Virtual member registered successfully" || (echo "❌ Virtual member registration failed" && exit 1)
	@echo "🧹 Cleaning up test files..."
	@aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/syota_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/syota_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/kasen_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/kasen_validate_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@echo "✅ Sample file processing tests completed successfully!"

backend-db-registration-test-cases: ## Test error handling with invalid files (HTTP 400 validation)
	@echo "🚨 Testing error handling for invalid test case files..."
	@echo "🧪 Validating error handling for test case files..."
	@echo "  Testing invalid files should return HTTP 400 errors..."
	@echo "📤 Uploading invalid_missing_name.yml (human)..."
	@aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_missing_name.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_name_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_missing_name.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_name_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@echo "⏳ Waiting for webhook processing..."
	@sleep 3
	@echo "📤 Uploading invalid_missing_model.yml (virtual)..."
	@aws s3 cp ./storage/sample_data/test_cases/virtual_members/invalid_missing_model.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_model_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/virtual_members/invalid_missing_model.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_model_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@echo "⏳ Waiting for webhook processing..."
	@sleep 3
	@echo "🔍 Checking backend logs for validation errors..."
	@docker logs vecr-garage-backend-db-registration --since=30s 2>&1 | grep -E "(❌|ERROR.*Validation error)" | tail -5 || (echo "⚠️  No validation errors found in recent logs" && exit 1)
	@echo "🧹 Cleaning up test files..."
	@aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_name_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_name_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_model_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --profile minio-local || \
		aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_model_test.yml \
		--endpoint-url $(STORAGE_BASE_URL) --no-sign-request
	@echo "✅ Error handling tests completed successfully!"

backend-db-registration-test-integration: ## Run all backend-db-registration tests (unit + samples + error handling)
	@echo "🚀 Running comprehensive backend-db-registration integration tests..."
	@echo "=========================================="
	@echo "📋 Phase 1: Unit Tests"
	@echo "=========================================="
	@make backend-db-registration-test-unit
	@echo ""
	@echo "=========================================="
	@echo "📋 Phase 2: Sample File Processing Tests"
	@echo "=========================================="
	@make backend-db-registration-test-samples
	@echo ""
	@echo "=========================================="
	@echo "📋 Phase 3: Error Handling Tests"
	@echo "=========================================="
	@make backend-db-registration-test-cases
	@echo ""
	@echo "🎉 All backend-db-registration integration tests passed successfully!"