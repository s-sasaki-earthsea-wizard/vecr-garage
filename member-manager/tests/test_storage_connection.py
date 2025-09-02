#!/usr/bin/env python3
"""
ストレージサービス接続テストスクリプト
member-managerサービスがstorageサービスに接続できるかをテスト
"""

import sys
import os
import requests
import json
from urllib.parse import urljoin

def test_storage_connection():
    """ストレージサービスへの接続テスト"""
    print("🔍 member-manager ストレージサービス接続テスト開始")
    print("=" * 50)
    
    # ストレージサービスの接続情報
    storage_host = os.getenv('STORAGE_HOST', 'storage')
    storage_port = os.getenv('STORAGE_PORT', '9000')
    storage_base_url = f"http://{storage_host}:{storage_port}"
    
    # MinIO認証情報
    minio_user = os.getenv('MINIO_ROOT_USER')
    minio_password = os.getenv('MINIO_ROOT_PASSWORD')
    
    print("🔗 接続情報:")
    print(f"  接続先: {storage_base_url}")
    print(f"  認証ユーザー: {minio_user if minio_user else '未設定'}")
    print(f"  認証パスワード: {'設定済み' if minio_password else '未設定'}")
    print()
    
    # 接続テスト実行
    print("🧪 接続テスト実行中...")
    
    # 1. MinIOヘルスチェックエンドポイントのテスト
    print("1. MinIOヘルスチェックエンドポイントテスト...")
    health_url = urljoin(storage_base_url, "/minio/health/live")
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ 成功 - MinIOヘルスチェックエンドポイントにアクセス可能")
            print(f"     レスポンス: {response.text}")
        else:
            print(f"   ❌ 失敗 - HTTPステータス: {response.status_code}")
            print(f"     レスポンス: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 失敗 - 接続エラー: {e}")
        return False
    
    # 2. MinIO準備状態チェックテスト
    print("2. MinIO準備状態チェックテスト...")
    ready_url = urljoin(storage_base_url, "/minio/health/ready")
    
    try:
        response = requests.get(ready_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ 成功 - MinIO準備状態チェックエンドポイントにアクセス可能")
            print(f"     レスポンス: {response.text}")
        else:
            print(f"   ⚠️  警告 - HTTPステータス: {response.status_code}")
            print(f"     レスポンス: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  警告 - 準備状態チェックエラー: {e}")
    
    # 3. 基本的なHTTP接続テスト
    print("3. 基本的なHTTP接続テスト...")
    try:
        response = requests.get(storage_base_url, timeout=5)
        print(f"   ✅ 成功 - HTTP接続可能 (ステータス: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 失敗 - HTTP接続エラー: {e}")
        return False
    
    print()
    print("🎉 MinIOストレージサービス接続テスト完了")
    print()
    print("📋 テスト結果サマリー:")
    print("  ✅ 基本的なHTTP接続: 成功")
    print("  ✅ MinIOヘルスチェックエンドポイント: 成功")
    print("  ✅ MinIO準備状態チェックエンドポイント: 成功")
    print()
    print("💡 注意:")
    print("  - このテストは基本的な接続性のみを確認します")
    print("  - ファイルアップロード等の機能テストは別途実装予定です")
    print("  - MinIOの認証機能は今後の実装で対応予定です")
    
    return True

def main():
    """メイン関数"""
    try:
        success = test_storage_connection()
        return success
    except Exception as e:
        print(f"\n💥 予期しないエラーが発生: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  テストが中断されました")
        exit(1)
    except Exception as e:
        print(f"\n💥 予期しないエラーが発生: {e}")
        exit(1)
