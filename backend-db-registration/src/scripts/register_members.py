#!/usr/bin/env python
from operations.member_registration import register_human_member_from_yaml, register_virtual_member_from_yaml
import logging
import argparse
from db.database import SessionLocal
from models.members import HumanMember, VirtualMember
import uuid
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    parser.add_argument('--human', action='store_true', help='Register human members')
    parser.add_argument('--virtual', action='store_true', help='Register virtual members')
    args = parser.parse_args()
    
    try:
        if args.human:
            # サンプルの人間メンバーを登録
            yaml_path = os.path.join("data", "human_members", "Syota.yml")
            register_human_member_from_yaml(yaml_path)
            logger.info("Human member registration completed")
            
        if args.virtual:
            # サンプルの仮想メンバーを登録
            yaml_path = os.path.join("data", "virtual_members", "Kasen.yml")
            register_virtual_member_from_yaml(yaml_path)
            logger.info("Virtual member registration completed")
            
        if not (args.human or args.virtual):
            # デフォルトで両方登録
            human_yaml_path = os.path.join("data", "human_members", "Syota.yml")
            virtual_yaml_path = os.path.join("data", "virtual_members", "Kasen.yml")
            register_human_member_from_yaml(human_yaml_path)
            register_virtual_member_from_yaml(virtual_yaml_path)
            logger.info("All member registration completed")
            
    except Exception as e:
        logger.error(f"Error during member registration: {e}")
        raise

if __name__ == "__main__":
    main()