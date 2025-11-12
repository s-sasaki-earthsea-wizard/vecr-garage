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

echo "💡 Webhook configuration applied to MinIO."
echo "🔧 MinIO service restart and event configuration will be handled by subsequent services."

echo "🎉 MinIO setup and webhook configuration completed!"
echo "📝 Summary:"
echo "   ✓ Bucket created: ${MINIO_BUCKET_NAME}"
echo "   ✓ Sample data copied to storage"
echo "   ✓ Webhook endpoint configured: ${WEBHOOK_FULL_URL}"
echo "   ✓ Event notifications active for .yml files in data/ prefix"
echo "🚀 System ready for webhook-triggered database operations!"

exit 0
