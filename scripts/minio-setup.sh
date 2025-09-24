#!/bin/sh

# MinIO Setup and Webhook Configuration Script
# このスクリプトはMinIOの初期設定とWebhook通知の設定を行います

set -e  # エラー時に停止

echo "🚀 Starting MinIO setup and webhook configuration..."

# MinIOサービスが起動するまで待機
sleep 5

echo "📡 Setting up MinIO alias..."
mc alias set myminio http://storage:${STORAGE_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

echo "🪣 Creating bucket if not exists..."
mc mb -p myminio/${MINIO_BUCKET_NAME}

echo "📁 Copying sample data files..."
mc cp --recursive /sample_data/samples/ myminio/${MINIO_BUCKET_NAME}/data/samples/
mc cp --recursive /sample_data/test_cases/ myminio/${MINIO_BUCKET_NAME}/data/test_cases/

echo "🔗 Setting up webhook notification configuration..."
mc admin config set myminio/ notify_webhook:1 endpoint="${WEBHOOK_FULL_URL}" queue_limit=1000

echo "🔄 Attempting MinIO service restart to apply webhook config..."
# TTYエラーは無視し、設定は既に保存されているため続行
if mc admin service restart myminio/ 2>/dev/null; then
    echo "✅ MinIO service restarted successfully"
else
    echo "⚠️ MinIO service restart failed (TTY limitation), but config is saved"
fi

echo "⏳ Waiting for webhook configuration to become active..."
sleep 12

echo "🧹 Clearing any existing webhook event configurations..."
mc event remove myminio/${MINIO_BUCKET_NAME} arn:minio:sqs::1:webhook || echo "No existing events to remove"

echo "📢 Adding webhook event notifications with retry logic..."
max_retries=5
retry_count=0
retry_delay=8

while [ $retry_count -lt $max_retries ]; do
    retry_count=$((retry_count + 1))
    echo "🎯 Webhook setup attempt $retry_count of $max_retries..."

    if mc event add myminio/${MINIO_BUCKET_NAME} arn:minio:sqs::1:webhook --event put,delete --prefix "data/" --suffix ".yml" 2>/dev/null; then
        echo "✅ Webhook events configured successfully!"
        break
    else
        if [ $retry_count -lt $max_retries ]; then
            echo "⚠️ Webhook setup attempt $retry_count failed, retrying in $retry_delay seconds..."
            sleep $retry_delay
        else
            echo "❌ Failed to configure webhook events after $max_retries attempts"
            echo "💡 Manual webhook setup command:"
            echo "   docker run --rm --network vecr-garage-network --entrypoint /bin/sh minio/mc -c \\"
            echo "     'mc alias set myminio http://storage:${STORAGE_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD} && \\"
            echo "      mc event add myminio/${MINIO_BUCKET_NAME} arn:minio:sqs::1:webhook --event put,delete --prefix \"data/\" --suffix \".yml\"'"
            exit 1
        fi
    fi
done

echo "📋 Verifying webhook configuration..."
mc event list myminio/${MINIO_BUCKET_NAME} || echo "Event list verification failed, but setup may still be functional"

echo "🎉 MinIO setup and webhook configuration completed!"
echo "📝 Summary:"
echo "   ✓ Bucket created: ${MINIO_BUCKET_NAME}"
echo "   ✓ Sample data copied to storage"
echo "   ✓ Webhook endpoint configured: ${WEBHOOK_FULL_URL}"
echo "   ✓ Event notifications active for .yml files in data/ prefix"
echo "🚀 System ready for webhook-triggered database operations!"

exit 0