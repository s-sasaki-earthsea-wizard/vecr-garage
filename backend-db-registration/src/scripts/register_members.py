#!/usr/bin/env python
import argparse

from operations.member_registration import (
    register_human_members_batch,
    register_virtual_members_batch,
)
from storage.storage_client import StorageClient

from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def get_all_yaml_files_from_storage():
    """ストレージからすべてのYAMLファイルのパスを動的に取得する

    ストレージサービス（MinIO）から人間メンバーと仮想メンバーの
    YAMLファイルのパスを動的に取得します。ファイルの存在確認や
    ストレージ接続の確認も行います。

    Returns:
        tuple: (human_files, virtual_files) のタプル
            - human_files (list): 人間メンバーYAMLファイルのパスリスト
            - virtual_files (list): 仮想メンバーYAMLファイルのパスリスト

    Raises:
        Exception: ストレージ接続エラーやファイル取得エラーが発生した場合

    Note:
        - 人間メンバーファイルは "data/human_members/" ディレクトリから取得
        - 仮想メンバーファイルは "data/virtual_members/" ディレクトリから取得
        - .yml と .yaml の両方の拡張子に対応
    """
    storage_client = StorageClient()

    # 人間メンバーのYAMLファイルを動的に取得
    human_files = storage_client.list_yaml_files("data/samples/human_members/")

    # 仮想メンバーのYAMLファイルを動的に取得
    virtual_files = storage_client.list_yaml_files("data/samples/virtual_members/")

    return human_files, virtual_files


def main():
    """メンバー登録スクリプトのメイン関数（バッチモード）

    コマンドライン引数に基づいて、ストレージからYAMLファイルを取得し、
    バッチ処理でメンバー登録を実行します。全てのファイルを一括で処理し、
    エラーが発生した場合は該当するバッチ全体をロールバックします。

    処理モード:
    - --human: 人間メンバーのみをバッチ処理
    - --virtual: 仮想メンバーのみをバッチ処理
    - 引数なし: 人間メンバーと仮想メンバーの両方をバッチ処理

    特徴:
    - 複数ファイルを一括処理（バッチモード）
    - アトミック操作（全成功または全ロールバック）
    - 効率的なデータベース操作
    - 詳細な処理結果サマリーを表示

    Usage:
        python register_members.py                    # 全メンバーバッチ処理
        python register_members.py --human           # 人間メンバーのみバッチ処理
        python register_members.py --virtual         # 仮想メンバーのみバッチ処理

    Note:
        - バッチ処理のため、一つでもエラーがあると該当バッチ全体がロールバックされます
        - 人間メンバーと仮想メンバーは独立して処理されるため、一方が失敗しても他方は処理されます
        - 既存メンバーが存在する場合は新規作成せず、既存オブジェクトを返します
    """
    parser = argparse.ArgumentParser(description="Register members from YAML files")
    parser.add_argument("--human", action="store_true", help="Register human members only")
    parser.add_argument("--virtual", action="store_true", help="Register virtual members only")
    args = parser.parse_args()

    try:
        # ストレージからYAMLファイルを動的に取得
        human_files, virtual_files = get_all_yaml_files_from_storage()

        # ファイルが見つからない場合の処理
        if not human_files and not virtual_files:
            print("❌ No YAML files found in storage.")
            print("Please ensure YAML files are uploaded to the storage service.")
            return

        if args.human:
            # 人間メンバーのみ登録
            if not human_files:
                print("❌ No human member YAML files found in storage.")
                print("Please ensure human member YAML files are uploaded to data/human_members/")
                return

            print("=== Processing Human Members (Batch Mode) ===")
            print(f"Found {len(human_files)} human member files:")
            for file in human_files:
                print(f"  - {file}")

            try:
                created_members = register_human_members_batch(human_files)
                print(f"✅ Successfully processed {len(created_members)} human members.")
            except Exception as e:
                print(f"❌ Batch registration failed: {e}")
                return

        elif args.virtual:
            # 仮想メンバーのみ登録
            if not virtual_files:
                print("❌ No virtual member YAML files found in storage.")
                print(
                    "Please ensure virtual member YAML files are uploaded to data/virtual_members/"
                )
                return

            print("=== Processing Virtual Members (Batch Mode) ===")
            print(f"Found {len(virtual_files)} virtual member files:")
            for file in virtual_files:
                print(f"  - {file}")

            try:
                created_members = register_virtual_members_batch(virtual_files)
                print(f"✅ Successfully processed {len(created_members)} virtual members.")
            except Exception as e:
                print(f"❌ Batch registration failed: {e}")
                return

        else:
            # デフォルトで全てのファイルを処理
            human_success = False
            virtual_success = False
            human_count = 0
            virtual_count = 0
            total_files = len(human_files) + len(virtual_files)

            # 人間メンバーの処理
            if human_files:
                print("=== Processing Human Members (Batch Mode) ===")
                print(f"Found {len(human_files)} human member files:")
                for file in human_files:
                    print(f"  - {file}")

                try:
                    created_members = register_human_members_batch(human_files)
                    print(f"✅ Successfully processed {len(created_members)} human members.")
                    human_success = True
                    human_count = len(created_members)
                except Exception as e:
                    print(f"❌ Human member batch registration failed: {e}")
                    print("Continuing with virtual member processing...")
            else:
                print("ℹ️  No human member YAML files found in storage.")

            # 仮想メンバーの処理
            if virtual_files:
                print("\n=== Processing Virtual Members (Batch Mode) ===")
                print(f"Found {len(virtual_files)} virtual member files:")
                for file in virtual_files:
                    print(f"  - {file}")

                try:
                    created_members = register_virtual_members_batch(virtual_files)
                    print(f"✅ Successfully processed {len(created_members)} virtual members.")
                    virtual_success = True
                    virtual_count = len(created_members)
                except Exception as e:
                    print(f"❌ Virtual member batch registration failed: {e}")
            else:
                print("ℹ️  No virtual member YAML files found in storage.")

            # 最終結果サマリー
            print("\n=== Final Summary ===")
            total_success = human_count + virtual_count

            if human_success and virtual_success:
                print("🎉 All processing completed successfully!")
                print(f"   Human members: {human_count}/{len(human_files)} processed")
                print(f"   Virtual members: {virtual_count}/{len(virtual_files)} processed")
                print(f"   Total: {total_success}/{total_files} members processed")
            elif human_success or virtual_success:
                print("⚠️  Partial processing completed:")
                if human_success:
                    print(f"   ✅ Human members: {human_count}/{len(human_files)} processed")
                else:
                    print("   ❌ Human members: Failed")
                if virtual_success:
                    print(f"   ✅ Virtual members: {virtual_count}/{len(virtual_files)} processed")
                else:
                    print("   ❌ Virtual members: Failed")
                print(f"   Total: {total_success}/{total_files} members processed")
            else:
                print("❌ All processing failed:")
                print("   ❌ Human members: Failed")
                print("   ❌ Virtual members: Failed")
                print(f"   Total: 0/{total_files} members processed")

    except Exception as e:
        error_msg = f"Error getting YAML files from storage: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("Please check your storage connection and ensure YAML files are available.")
        raise


if __name__ == "__main__":
    main()
