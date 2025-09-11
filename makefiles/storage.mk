# ストレージ関連のMakeタスク
# MinIO/S3の基本操作を定義

.PHONY: s3-ls s3-setup-profile s3-clean-bucket

s3-ls: ## List files in MinIO storage bucket
	@echo "Listing files in MinIO storage bucket..."
	aws s3 ls s3://$(MINIO_BUCKET_NAME)/ \
		--endpoint-url $(STORAGE_BASE_URL) \
		--profile minio-local || \
		aws s3 ls s3://$(MINIO_BUCKET_NAME)/ \
		--endpoint-url $(STORAGE_BASE_URL) \
		--no-sign-request

s3-setup-profile: ## Setup AWS CLI profile for MinIO local storage
	@echo "Setting up AWS CLI profile for MinIO local storage..."
	@aws configure set aws_access_key_id $(MINIO_ROOT_USER) --profile minio-local || echo "Failed to set access key"
	@aws configure set aws_secret_access_key $(MINIO_ROOT_PASSWORD) --profile minio-local || echo "Failed to set secret key"
	@aws configure set region us-east-1 --profile minio-local || echo "Failed to set region"
	@aws configure set s3.signature_version s3v4 --profile minio-local || echo "Failed to set signature version"
	@echo "AWS CLI profile 'minio-local' configured successfully!"

s3-clean-bucket: ## Clean all files from MinIO storage bucket
	@echo "Cleaning all files from MinIO storage bucket..."
	@read -p "Are you sure you want to delete all files in bucket $(MINIO_BUCKET_NAME)? [y/N] " confirm && \
		if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
			aws s3 rm s3://$(MINIO_BUCKET_NAME)/ --recursive \
				--endpoint-url $(STORAGE_BASE_URL) \
				--profile minio-local || \
			aws s3 rm s3://$(MINIO_BUCKET_NAME)/ --recursive \
				--endpoint-url $(STORAGE_BASE_URL) \
				--no-sign-request; \
			echo "Bucket cleaned successfully!"; \
		else \
			echo "Operation cancelled."; \
		fi