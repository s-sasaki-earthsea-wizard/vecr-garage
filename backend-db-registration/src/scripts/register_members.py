#!/usr/bin/env python
from operations.member_registration import register_human_members_batch, register_virtual_members_batch
import logging
import argparse
from db.database import SessionLocal
from models.members import HumanMember, VirtualMember
import uuid
import os
from storage.storage_client import StorageClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_yaml_files_from_storage():
    """ストレージからすべてのYAMLファイルのパスを動的に取得する"""
    storage_client = StorageClient()
    
    # 人間メンバーのYAMLファイルを動的に取得
    human_files = storage_client.list_yaml_files("data/human_members/")
    
    # 仮想メンバーのYAMLファイルを動的に取得
    virtual_files = storage_client.list_yaml_files("data/virtual_members/")
    
    return human_files, virtual_files

def main():
    parser = argparse.ArgumentParser(description='Register members from YAML files')
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
                print("Please ensure virtual member YAML files are uploaded to data/virtual_members/")
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
            print(f"\n=== Final Summary ===")
            total_success = human_count + virtual_count
            
            if human_success and virtual_success:
                print(f"🎉 All processing completed successfully!")
                print(f"   Human members: {human_count}/{len(human_files)} processed")
                print(f"   Virtual members: {virtual_count}/{len(virtual_files)} processed")
                print(f"   Total: {total_success}/{total_files} members processed")
            elif human_success or virtual_success:
                print(f"⚠️  Partial processing completed:")
                if human_success:
                    print(f"   ✅ Human members: {human_count}/{len(human_files)} processed")
                else:
                    print(f"   ❌ Human members: Failed")
                if virtual_success:
                    print(f"   ✅ Virtual members: {virtual_count}/{len(virtual_files)} processed")
                else:
                    print(f"   ❌ Virtual members: Failed")
                print(f"   Total: {total_success}/{total_files} members processed")
            else:
                print(f"❌ All processing failed:")
                print(f"   ❌ Human members: Failed")
                print(f"   ❌ Virtual members: Failed")
                print(f"   Total: 0/{total_files} members processed")
            
    except Exception as e:
        error_msg = f"Error getting YAML files from storage: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        print("Please check your storage connection and ensure YAML files are available.")
        raise

if __name__ == "__main__":
    main()