#!/usr/bin/env python
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml
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
    
    try:
        # 人間メンバーのYAMLファイルを動的に取得
        human_files = storage_client.list_yaml_files("data/human_members/")
        
        # 仮想メンバーのYAMLファイルを動的に取得
        virtual_files = storage_client.list_yaml_files("data/virtual_members/")
        
        return human_files, virtual_files
    except Exception as e:
        logger.error(f"Error getting YAML files from storage: {e}")
        # フォールバック: 既知のファイルリスト
        fallback_human_files = [
            "data/human_members/Syota.yml",
            "data/human_members/Rin.yml"
        ]
        fallback_virtual_files = [
            "data/virtual_members/Kasen.yml",
            "data/virtual_members/Darcy.yml"
        ]
        logger.info("Using fallback file list")
        return fallback_human_files, fallback_virtual_files

def register_members():
    session = SessionLocal()
    try:
        # サンプルの人間メンバーを登録
        human_member = HumanMember(
            member_name="山田太郎",
            bio="サンプルの人間メンバーです"
        )
        session.add(human_member)
        
        # サンプルの仮想メンバーを登録
        virtual_member = VirtualMember(
            member_name="AIアシスタント",
            llm_model="gpt-4",
            custom_prompt="あなたは親切なAIアシスタントです"
        )
        session.add(virtual_member)
        
        session.commit()
        logger.info("メンバーの登録が完了しました")
    except Exception as e:
        session.rollback()
        logger.error(f"エラーが発生しました: {e}")
        raise
    finally:
        session.close()

def main():
    parser = argparse.ArgumentParser(description='Register members from YAML files')
    parser.add_argument('--human', action='store_true', help='Register human members only')
    parser.add_argument('--virtual', action='store_true', help='Register virtual members only')
    args = parser.parse_args()
    
    try:
        if args.human:
            # 人間メンバーのみ登録
            human_files, _ = get_all_yaml_files_from_storage()
            print("=== Processing Human Members ===")
            for yaml_path in human_files:
                try:
                    print(f"Processing: {yaml_path}")
                    register_human_member_from_yaml(yaml_path)
                except Exception as e:
                    print(f"Failed to process {yaml_path}: {e}")
                    continue
            logger.info("Human member registration completed")
            
        elif args.virtual:
            # 仮想メンバーのみ登録
            _, virtual_files = get_all_yaml_files_from_storage()
            print("=== Processing Virtual Members ===")
            for yaml_path in virtual_files:
                try:
                    print(f"Processing: {yaml_path}")
                    register_virtual_member_from_yaml(yaml_path)
                except Exception as e:
                    print(f"Failed to process {yaml_path}: {e}")
                    continue
            logger.info("Virtual member registration completed")
            
        else:
            # デフォルトで全てのファイルを処理
            human_files, virtual_files = get_all_yaml_files_from_storage()
            
            print("=== Processing Human Members ===")
            for yaml_path in human_files:
                try:
                    print(f"Processing: {yaml_path}")
                    register_human_member_from_yaml(yaml_path)
                except Exception as e:
                    print(f"Failed to process {yaml_path}: {e}")
                    continue
            
            print("\n=== Processing Virtual Members ===")
            for yaml_path in virtual_files:
                try:
                    print(f"Processing: {yaml_path}")
                    register_virtual_member_from_yaml(yaml_path)
                except Exception as e:
                    print(f"Failed to process {yaml_path}: {e}")
                    continue
            
            logger.info("All member registration completed")
            
    except Exception as e:
        logger.error(f"Error during member registration: {e}")
        raise

if __name__ == "__main__":
    main()