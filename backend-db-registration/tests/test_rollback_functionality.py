#!/usr/bin/env python3
"""
ロールバック機能とバリデーション機能をテストするスクリプト
"""
import sys

from operations.member_registration import (
    register_human_member_from_yaml,
    register_virtual_member_from_yaml,
)
from utils.logging_config import setup_logging
from validation.yaml_validator import ValidationError, YAMLValidator

logger = setup_logging(__name__)


def test_human_member_validation():
    """人間メンバーのバリデーションテスト"""
    print("\n=== Testing Human Member Validation ===")

    # テストケース: 必須フィールドが欠けている場合（既存の無効なファイル）
    print("\n1. Testing missing required field (name) using invalid_missing_name.yml")
    try:
        register_human_member_from_yaml("data/test_cases/human_members/invalid_missing_name.yml")
        print("❌ Test failed: Should have raised ValidationError")
    except ValidationError as e:
        print(f"✅ Test passed: ValidationError caught - {e.message}")
        if e.missing_fields:
            print(f"   Missing fields: {', '.join(e.missing_fields)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def test_virtual_member_validation():
    """仮想メンバーのバリデーションテスト"""
    print("\n=== Testing Virtual Member Validation ===")

    # テストケース: 必須フィールドが欠けている場合（既存の無効なファイル）
    print("\n1. Testing missing required fields (name) using invalid_missing_name.yml")
    try:
        register_virtual_member_from_yaml(
            "data/test_cases/virtual_members/invalid_missing_name.yml"
        )
        print("❌ Test failed: Should have raised ValidationError")
    except ValidationError as e:
        print(f"✅ Test passed: ValidationError caught - {e.message}")
        if e.missing_fields:
            print(f"   Missing fields: {', '.join(e.missing_fields)}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def test_successful_registration():
    """正常な登録のテスト"""
    print("\n=== Testing Successful Registration ===")

    # 人間メンバーの正常な登録
    print("\n1. Testing successful human member registration")
    try:
        result = register_human_member_from_yaml("data/samples/human_members/syota.yml")
        print(f"✅ Human member registration successful: {result.member_name}")
    except Exception as e:
        print(f"❌ Human member registration failed: {e}")

    # 仮想メンバーの正常な登録
    print("\n2. Testing successful virtual member registration")
    try:
        result = register_virtual_member_from_yaml("data/samples/virtual_members/kasen.yml")
        print(f"✅ Virtual member registration successful: {result.member_name}")
    except Exception as e:
        print(f"❌ Virtual member registration failed: {e}")


def test_validation_directly():
    """バリデーション機能を直接テスト"""
    print("\n=== Testing Validation Directly ===")

    # 無効な人間メンバーデータ（Rin.ymlと同じ内容）
    invalid_human_data = {"bio": "I'm a human member."}
    print("\n1. Testing invalid human member data directly (Rin.yml content)")
    try:
        YAMLValidator.validate_human_member_yaml(invalid_human_data)
        print("❌ Test failed: Should have raised ValidationError")
    except ValidationError as e:
        print(f"✅ Test passed: ValidationError caught - {e.message}")
        if e.missing_fields:
            print(f"   Missing fields: {', '.join(e.missing_fields)}")

    # 無効な仮想メンバーデータ（Darcy.ymlと同じ内容）
    invalid_virtual_data = {"custom_prompt": "I'm a virtual member.", "llm_model": "gpt-4o"}
    print("\n2. Testing invalid virtual member data directly (Darcy.yml content)")
    try:
        YAMLValidator.validate_virtual_member_yaml(invalid_virtual_data)
        print("❌ Test failed: Should have raised ValidationError")
    except ValidationError as e:
        print(f"✅ Test passed: ValidationError caught - {e.message}")
        if e.missing_fields:
            print(f"   Missing fields: {', '.join(e.missing_fields)}")


def main():
    """メイン関数"""
    print("🚀 Starting Rollback and Validation Functionality Tests")

    try:
        # 直接バリデーションテスト（ストレージに依存しない）
        test_validation_directly()

        # ストレージを使用したバリデーションテスト
        test_human_member_validation()
        test_virtual_member_validation()

        # 正常な登録テスト
        test_successful_registration()

        print("\n🎉 All tests completed!")

    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
