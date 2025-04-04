#!/bin/bash

# Wait for MinIO to be ready
sleep 10

# Set up MinIO client
mc alias set myminio http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create bucket (if it doesn't exist)
mc mb --ignore-existing myminio/${MINIO_BUCKET_NAME}

# Copy sample data to bucket
mc cp --recursive /tmp/sample_data/* myminio/${MINIO_BUCKET_NAME}/

# Run MinIO server in the background
exec minio server /data --console-address ":9001"