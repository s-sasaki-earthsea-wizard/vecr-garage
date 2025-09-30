# YMLファイル操作のMakeタスク
# サンプルファイルとテストケースファイルの操作を統合管理

.PHONY: samples-copy samples-copy-human samples-copy-virtual samples-copy-single samples-clean samples-verify
.PHONY: test-cases-copy test-cases-copy-human test-cases-copy-virtual test-cases-copy-single test-cases-clean test-cases-verify

# ------------------------------------------------------------
# Sample Files Operations (正常系ファイル)
# ------------------------------------------------------------

samples-copy: samples-copy-human samples-copy-virtual ## Copy all normal sample files to MinIO storage

samples-copy-human: ## Copy human member sample files to MinIO storage
	@echo "Copying human member sample files to MinIO storage..."
	aws s3 cp ./storage/sample_data/samples/human_members/syota.yml s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/syota.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/samples/human_members/syota.yml s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/syota.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	aws s3 cp ./storage/sample_data/samples/human_members/rin.yml s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/rin.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/samples/human_members/rin.yml s3://$(MINIO_BUCKET_NAME)/data/samples/human_members/rin.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Human member sample files copied successfully!"

samples-copy-virtual: ## Copy virtual member sample files to MinIO storage
	@echo "Copying virtual member sample files to MinIO storage..."
	aws s3 cp ./storage/sample_data/samples/virtual_members/kasen.yml s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/kasen.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/samples/virtual_members/kasen.yml s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/kasen.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	aws s3 cp ./storage/sample_data/samples/virtual_members/darcy.yml s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/darcy.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp ./storage/sample_data/samples/virtual_members/darcy.yml s3://$(MINIO_BUCKET_NAME)/data/samples/virtual_members/darcy.yml \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Virtual member sample files copied successfully!"

samples-copy-single: ## Copy a single sample file (usage: make samples-copy-single FILE=path/to/file.yml TARGET=target/path.yml)
	@if [ -z "$(FILE)" ] || [ -z "$(TARGET)" ]; then \
		echo "❌ Error: FILE and TARGET parameters are required"; \
		echo "Usage: make samples-copy-single FILE=./storage/sample_data/samples/human_members/syota.yml TARGET=data/samples/human_members/syota_copy.yml"; \
		exit 1; \
	fi
	@echo "Copying single sample file: $(FILE) -> s3://$(MINIO_BUCKET_NAME)/$(TARGET)"
	aws s3 cp $(FILE) s3://$(MINIO_BUCKET_NAME)/$(TARGET) \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp $(FILE) s3://$(MINIO_BUCKET_NAME)/$(TARGET) \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Single sample file copied successfully!"

samples-clean: ## Clean sample files from MinIO storage
	@echo "Cleaning sample files from MinIO storage..."
	aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/samples/ --recursive \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 rm s3://$(MINIO_BUCKET_NAME)/data/samples/ --recursive \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Sample files cleaned successfully!"

samples-verify: ## Verify sample files exist in local storage
	@echo "Verifying sample files exist locally..."
	@test -f ./storage/sample_data/samples/human_members/syota.yml || (echo "❌ Missing: syota.yml" && exit 1)
	@test -f ./storage/sample_data/samples/human_members/rin.yml || (echo "❌ Missing: rin.yml" && exit 1)
	@test -f ./storage/sample_data/samples/virtual_members/kasen.yml || (echo "❌ Missing: kasen.yml" && exit 1)
	@test -f ./storage/sample_data/samples/virtual_members/darcy.yml || (echo "❌ Missing: darcy.yml" && exit 1)
	@echo "✅ All sample files verified successfully!"

# ------------------------------------------------------------
# Test Cases Operations (異常系ファイル)
# ------------------------------------------------------------

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
		echo "❌ Error: FILE parameter is required"; \
		echo "Usage: make test-cases-copy-single FILE=path/to/file.yml"; \
		exit 1; \
	fi
	@echo "Copying single test case file: $(FILE)"
	@BASENAME=$$(basename "$(FILE)"); \
	if echo "$(FILE)" | grep -q "human_members"; then \
		TARGET="data/test_cases/human_members/$$BASENAME"; \
	elif echo "$(FILE)" | grep -q "virtual_members"; then \
		TARGET="data/test_cases/virtual_members/$$BASENAME"; \
	else \
		echo "❌ Error: Cannot determine target directory from file path"; \
		exit 1; \
	fi; \
	aws s3 cp "$(FILE)" "s3://$(MINIO_BUCKET_NAME)/$$TARGET" \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 cp "$(FILE)" "s3://$(MINIO_BUCKET_NAME)/$$TARGET" \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request
	@echo "Single test case file copied successfully!"

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