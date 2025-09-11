# テストケース管理のMakeタスク
# 異常系テストケースファイルの操作を定義

.PHONY: test-cases-copy test-cases-copy-human test-cases-copy-virtual test-cases-copy-single test-cases-clean test-cases-verify

test-cases-copy: test-cases-copy-human test-cases-copy-virtual ## Copy all test case files to MinIO storage

test-cases-copy-human: ## Copy human member test case files to MinIO storage
	@echo "Copying human member test case files to MinIO storage..."
	aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_missing_name.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_name.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_missing_name.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_name.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_missing_bio.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_bio.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_missing_bio.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_missing_bio.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_empty_file.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_empty_file.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/human_members/invalid_empty_file.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/human_members/invalid_empty_file.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Human member test case files copied successfully!"

test-cases-copy-virtual: ## Copy virtual member test case files to MinIO storage
	@echo "Copying virtual member test case files to MinIO storage..."
	aws s3 cp ./storage/sample_data/test_cases/virtual_members/invalid_missing_name.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_name.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/virtual_members/invalid_missing_name.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_name.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	aws s3 cp ./storage/sample_data/test_cases/virtual_members/invalid_missing_model.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_model.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/test_cases/virtual_members/invalid_missing_model.yml s3://$(MINIO_BUCKET_NAME)/data/test_cases/virtual_members/invalid_missing_model.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Virtual member test case files copied successfully!"

test-cases-copy-single: ## Copy a single test case file (usage: make test-cases-copy-single FILE=path/to/file.yml)
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make test-cases-copy-single FILE=path/to/file.yml"; \
		echo "Example: make test-cases-copy-single FILE=test_cases/human_members/invalid_missing_name.yml"; \
		exit 1; \
	fi
	@echo "Copying single test case file: $(FILE)"
	aws s3 cp ./storage/sample_data/$(FILE) s3://$(MINIO_BUCKET_NAME)/data/$(FILE) \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/$(FILE) s3://$(MINIO_BUCKET_NAME)/data/$(FILE) \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Test case file copied successfully: $(FILE)"

test-cases-clean: ## Clean test case files from MinIO storage
	@echo "Cleaning test case files from MinIO storage..."
	aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/test_cases/ --recursive \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/test_cases/ --recursive \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Test case files cleaned successfully!"

test-cases-verify: ## Verify test case files exist locally
	@echo "Verifying test case files exist locally..."
	@test -f ./storage/sample_data/test_cases/human_members/invalid_missing_name.yml || (echo "❌ Missing: invalid_missing_name.yml" && exit 1)
	@test -f ./storage/sample_data/test_cases/human_members/invalid_missing_bio.yml || (echo "❌ Missing: invalid_missing_bio.yml" && exit 1)
	@test -f ./storage/sample_data/test_cases/human_members/invalid_empty_file.yml || (echo "❌ Missing: invalid_empty_file.yml" && exit 1)
	@test -f ./storage/sample_data/test_cases/virtual_members/invalid_missing_name.yml || (echo "❌ Missing: virtual invalid_missing_name.yml" && exit 1)
	@test -f ./storage/sample_data/test_cases/virtual_members/invalid_missing_model.yml || (echo "❌ Missing: invalid_missing_model.yml" && exit 1)
	@echo "✅ All test case files verified successfully!"