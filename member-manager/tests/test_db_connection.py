#!/usr/bin/env python3
"""
データベース接続テストスクリプト
member-managerサービスがdb-memberサービスに接続できるかをテスト
"""

from database import DatabaseManager


def main():
    """メイン関数"""
    print("🔍 member-manager データベース接続テスト開始")
    print("=" * 50)

    # データベースマネージャーの初期化
    db_manager = DatabaseManager()

    # 接続情報の表示
    print("🔗 接続情報:")
    print(f"  接続先: {db_manager.db_host}:{db_manager.db_port}")
    print(f"  データベース: {db_manager.db_name}")
    print(f"  ユーザー: {db_manager.db_user}")
    print()

    # 接続テスト実行
    print("🧪 接続テスト実行中...")

    # psycopg2接続テスト
    print("1. psycopg2接続テスト...")
    psycopg2_success = db_manager.test_connection()

    if psycopg2_success:
        print("   ✅ 成功")
    else:
        print("   ❌ 失敗")

    # SQLAlchemy接続テスト
    print("2. SQLAlchemy接続テスト...")
    sqlalchemy_success = db_manager.test_sqlalchemy_connection()

    if sqlalchemy_success:
        print("   ✅ 成功")
    else:
        print("   ❌ 失敗")

    print()

    # 結果の表示
    if psycopg2_success and sqlalchemy_success:
        print("🎉 すべての接続テストが成功しました！")
        print()

        # テーブル一覧を取得
        print("📊 データベーステーブル情報:")
        tables = db_manager.get_table_list()

        if tables:
            for table in tables:
                count = db_manager.get_table_count(table)
                print(f"  📋 {table}: {count} 件")
        else:
            print("  ⚠️  テーブルが見つかりませんでした")

        print()
        print("✅ データベース接続テスト完了")

    else:
        print("💥 接続テストが失敗しました")
        print()
        print("🔧 トラブルシューティング:")
        print("  1. db-memberサービスが起動しているか確認")
        print("  2. 環境変数が正しく設定されているか確認")
        print("  3. ネットワーク設定を確認")
        print("  4. データベースの認証情報を確認")

        return False

    return True


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
