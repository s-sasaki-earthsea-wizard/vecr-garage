#!/usr/bin/env python3
"""
Database connection and operations for member-manager service
PostgreSQL接続とテーブル操作の実装
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """データベース接続管理クラス"""
    
    def __init__(self):
        """環境変数からデータベース接続情報を取得"""
        self.db_host = os.getenv('MEMBER_DB_HOST', 'db-member')
        self.db_port = os.getenv('MEMBER_DB_PORT', '5432')
        self.db_user = os.getenv('MEMBER_DB_USER', 'testuser')
        self.db_password = os.getenv('MEMBER_DB_PASSWORD', 'password')
        self.db_name = os.getenv('MEMBER_DB_NAME', 'member_db')
        
        # 接続文字列
        self.connection_string = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        self.engine = None
        self.session = None
    
    def test_connection(self):
        """データベース接続テスト（psycopg2使用）"""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            logger.info("✅ PostgreSQL接続成功 (psycopg2)")
            
            # 接続情報を表示
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            logger.info(f"PostgreSQL バージョン: {version[0]}")
            
            cur.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL接続失敗 (psycopg2): {e}")
            return False
    
    def test_sqlalchemy_connection(self):
        """SQLAlchemy接続テスト"""
        try:
            self.engine = create_engine(self.connection_string)
            
            # 接続テスト
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("✅ SQLAlchemy接続成功")
                return True
                
        except SQLAlchemyError as e:
            logger.error(f"❌ SQLAlchemy接続失敗: {e}")
            return False
    
    def get_table_list(self):
        """利用可能なテーブル一覧を取得"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()
            
            with self.engine.connect() as conn:
                # テーブル一覧を取得
                query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """)
                result = conn.execute(query)
                tables = [row[0] for row in result]
                logger.info(f"利用可能なテーブル: {tables}")
                return tables
                
        except Exception as e:
            logger.error(f"テーブル一覧取得失敗: {e}")
            return []
    
    def get_table_data(self, table_name, limit=100):
        """指定されたテーブルのデータを取得"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()
            
            with self.engine.connect() as conn:
                # テーブルの列情報を取得
                columns_query = text(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """)
                columns_result = conn.execute(columns_query)
                columns = [{"name": row[0], "type": row[1], "nullable": row[2]} for row in columns_result]
                
                # テーブルのデータを取得
                data_query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
                data_result = conn.execute(data_query)
                data = [dict(row._mapping) for row in data_result]
                
                logger.info(f"テーブル '{table_name}' から {len(data)} 件のデータを取得")
                
                return {
                    "table_name": table_name,
                    "columns": columns,
                    "data": data,
                    "total_count": len(data)
                }
                
        except Exception as e:
            logger.error(f"テーブル '{table_name}' のデータ取得失敗: {e}")
            return None
    
    def get_table_count(self, table_name):
        """指定されたテーブルのレコード数を取得"""
        try:
            if not self.engine:
                self.test_sqlalchemy_connection()
            
            with self.engine.connect() as conn:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = conn.execute(count_query)
                count = result.scalar()
                logger.info(f"テーブル '{table_name}' のレコード数: {count}")
                return count
                
        except Exception as e:
            logger.error(f"テーブル '{table_name}' のレコード数取得失敗: {e}")
            return 0

def test_database_connection():
    """データベース接続テストの実行"""
    logger.info("🔍 データベース接続テスト開始")
    
    db_manager = DatabaseManager()
    
    # 接続情報を表示
    logger.info(f"接続先: {db_manager.db_host}:{db_manager.db_port}")
    logger.info(f"データベース: {db_manager.db_name}")
    logger.info(f"ユーザー: {db_manager.db_user}")
    
    # psycopg2接続テスト
    psycopg2_success = db_manager.test_connection()
    
    # SQLAlchemy接続テスト
    sqlalchemy_success = db_manager.test_sqlalchemy_connection()
    
    if psycopg2_success and sqlalchemy_success:
        logger.info("🎉 すべての接続テストが成功しました！")
        
        # テーブル一覧を取得
        tables = db_manager.get_table_list()
        
        # 各テーブルのレコード数を確認
        for table in tables:
            count = db_manager.get_table_count(table)
            logger.info(f"テーブル '{table}': {count} 件")
        
        return True
    else:
        logger.error("💥 接続テストが失敗しました")
        return False

if __name__ == "__main__":
    test_database_connection()
