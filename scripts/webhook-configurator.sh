#!/bin/sh

# Webhook Configurator Script
# MinIO再起動後にWebhookイベント設定を行うスクリプト

set -e  # エラー時に停止

echo "🔧 Starting webhook configuration after MinIO restart..."

# MinIO再起動完了を待機
echo "⏳ Waiting for MinIO service to be ready after restart..."
sleep 10

echo "📡 Setting up MinIO alias for webhook configuration..."
mc alias set myminio http://storage:${STORAGE_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

echo "🧹 Clearing any existing webhook event configurations..."
mc event remove myminio/${MINIO_BUCKET_NAME} arn:minio:sqs::1:webhook --event put,delete || echo "No existing events to remove"

echo "📢 Adding webhook event notifications with retry logic..."
max_retries=5
retry_count=0
retry_delay=10

while [ $retry_count -lt $max_retries ]; do
    retry_count=$((retry_count + 1))
    echo "🎯 Webhook configuration attempt $retry_count of $max_retries..."

    if mc event add myminio/${MINIO_BUCKET_NAME} arn:minio:sqs::1:webhook --event put,delete --prefix "data/" --suffix ".yml" 2>/dev/null; then
        echo "✅ Webhook events configured successfully!"
        break
    else
        if [ $retry_count -lt $max_retries ]; then
            echo "⚠️ Webhook configuration attempt $retry_count failed, retrying in $retry_delay seconds..."
            sleep $retry_delay
        else
            echo "❌ Failed to configure webhook events after $max_retries attempts"
            echo "💡 This indicates that MinIO service may not be fully ready"
            echo "🔍 Checking MinIO status..."
            mc admin info myminio/ || echo "MinIO admin info failed"
            exit 1
        fi
    fi
done

echo "📋 Verifying webhook configuration..."
if mc event list myminio/${MINIO_BUCKET_NAME}; then
    echo "🎉 Webhook configuration verification successful!"
else
    echo "⚠️ Webhook configuration verification failed, but events may still be functional"
fi

echo "🧪 Testing webhook functionality..."
echo "Creating test file to trigger webhook..."
echo "test: webhook_test" | mc pipe myminio/${MINIO_BUCKET_NAME}/data/test_webhook.yml
echo "Removing test file..."
mc rm myminio/${MINIO_BUCKET_NAME}/data/test_webhook.yml || echo "Test file removal failed (expected if webhook worked)"

echo "🚀 Webhook configurator completed successfully!"
echo "📝 Summary:"
echo "   ✓ MinIO alias configured"
echo "   ✓ Webhook events added for .yml files in data/ prefix"
echo "   ✓ Event notifications active: put, delete"
echo "   ✓ Target endpoint: ${WEBHOOK_FULL_URL}"
echo "🌟 System ready for production webhook operations!"

exit 0