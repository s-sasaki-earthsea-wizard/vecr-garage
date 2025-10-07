#!/usr/bin/env python
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml
import argparse
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
    """メンバー登録スクリプトのメイン関数（シングルモード）
    
    コマンドライン引数に基づいて、ストレージからYAMLファイルを取得し、
    個別にメンバー登録を実行します。各ファイルを一つずつ処理し、
    エラーが発生しても他のファイルの処理を継続します。
    
    処理モード:
    - --human: 人間メンバーのみを処理
    - --virtual: 仮想メンバーのみを処理
    - 引数なし: 人間メンバーと仮想メンバーの両方を処理
    
    特徴:
    - 各ファイルを個別に処理（シングルモード）
    - エラーが発生しても他のファイルの処理を継続
    - 詳細な進捗表示とエラー報告
    - 最終的な処理結果サマリーを表示
    
    Usage:
        python register_members_single.py                    # 全メンバー処理
        python register_members_single.py --human           # 人間メンバーのみ
        python register_members_single.py --virtual         # 仮想メンバーのみ
    """
    parser = argparse.ArgumentParser(description='Register members from YAML files (Single Mode)')
    parser.add_argument('--human', action='store_true', help='Register human members only')
    parser.add_argument('--virtual', action='store_true', help='Register virtual members only')
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
                
            print("=== Processing Human Members (Single Mode) ===")
            print(f"Found {len(human_files)} human member files:")
            for file in human_files:
                print(f"  - {file}")
            
            success_count = 0
            error_count = 0
            
            for yaml_path in human_files:
                try:
                    print(f"\nProcessing: {yaml_path}")
                    register_human_member_from_yaml(yaml_path)
                    print(f"✅ Successfully processed: {yaml_path}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ Failed to process {yaml_path}: {e}")
                    error_count += 1
                    continue
            
            print(f"\n=== Human Members Summary ===")
            print(f"✅ Successfully processed: {success_count}")
            print(f"❌ Failed to process: {error_count}")
            print(f"📊 Total files: {len(human_files)}")
            
        elif args.virtual:
            # 仮想メンバーのみ登録
            if not virtual_files:
                print("❌ No virtual member YAML files found in storage.")
                print("Please ensure virtual member YAML files are uploaded to data/virtual_members/")
                return
                
            print("=== Processing Virtual Members (Single Mode) ===")
            print(f"Found {len(virtual_files)} virtual member files:")
            for file in virtual_files:
                print(f"  - {file}")
            
            success_count = 0
            error_count = 0
            
            for yaml_path in virtual_files:
                try:
                    print(f"\nProcessing: {yaml_path}")
                    register_virtual_member_from_yaml(yaml_path)
                    print(f"✅ Successfully processed: {yaml_path}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ Failed to process {yaml_path}: {e}")
                    error_count += 1
                    continue
            
            print(f"\n=== Virtual Members Summary ===")
            print(f"✅ Successfully processed: {success_count}")
            print(f"❌ Failed to process: {error_count}")
            print(f"📊 Total files: {len(virtual_files)}")
            
        else:
            # デフォルトで全てのファイルを処理
            total_success = 0
            total_error = 0
            total_files = len(human_files) + len(virtual_files)
            
            # 人間メンバーの処理
            if human_files:
                print("=== Processing Human Members (Single Mode) ===")
                print(f"Found {len(human_files)} human member files:")
                for file in human_files:
                    print(f"  - {file}")
                
                human_success = 0
                human_error = 0
                
                for yaml_path in human_files:
                    try:
                        print(f"\nProcessing: {yaml_path}")
                        register_human_member_from_yaml(yaml_path)
                        print(f"✅ Successfully processed: {yaml_path}")
                        human_success += 1
                        total_success += 1
                    except Exception as e:
                        print(f"❌ Failed to process {yaml_path}: {e}")
                        human_error += 1
                        total_error += 1
                        continue
                
                print(f"\n--- Human Members Summary ---")
                print(f"✅ Successfully processed: {human_success}")
                print(f"❌ Failed to process: {human_error}")
            else:
                print("ℹ️  No human member YAML files found in storage.")
            
            # 仮想メンバーの処理
            if virtual_files:
                print("\n=== Processing Virtual Members (Single Mode) ===")
                print(f"Found {len(virtual_files)} virtual member files:")
                for file in virtual_files:
                    print(f"  - {file}")
                
                virtual_success = 0
                virtual_error = 0
                
                for yaml_path in virtual_files:
                    try:
                        print(f"\nProcessing: {yaml_path}")
                        register_virtual_member_from_yaml(yaml_path)
                        print(f"✅ Successfully processed: {yaml_path}")
                        virtual_success += 1
                        total_success += 1
                    except Exception as e:
                        print(f"❌ Failed to process {yaml_path}: {e}")
                        virtual_error += 1
                        total_error += 1
                        continue
                
                print(f"\n--- Virtual Members Summary ---")
                print(f"✅ Successfully processed: {virtual_success}")
                print(f"❌ Failed to process: {virtual_error}")
            else:
                print("ℹ️  No virtual member YAML files found in storage.")
            
            # 最終結果サマリー
            print(f"\n=== Final Summary ===")
            print(f"🎯 Total files processed: {total_files}")
            print(f"✅ Total successful: {total_success}")
            print(f"❌ Total failed: {total_error}")
            
            if total_error == 0:
                print(f"🎉 All files processed successfully!")
            elif total_success == 0:
                print(f"❌ All files failed to process.")
            else:
                print(f"⚠️  Partial success: {total_success}/{total_files} files processed successfully.")
            
    except Exception as e:
        error_msg = f"Error getting YAML files from storage: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("Please check your storage connection and ensure YAML files are available.")
        raise

if __name__ == "__main__":
    main() 