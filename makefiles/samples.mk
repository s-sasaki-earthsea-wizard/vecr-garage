# サンプルデータ管理のMakeタスク
# 正常系サンプルファイルの操作を定義

.PHONY: samples-copy samples-copy-human samples-copy-virtual samples-clean samples-verify

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