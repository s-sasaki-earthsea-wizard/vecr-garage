#!/usr/bin/env python3
"""
Member Manager Mock Application with Authentication
将来的にはJinjaテンプレートを使用してデータベースから動的にデータを取得する予定
現在はモックアップとしてハードコードされたデータを使用

認証システム実装計画:
- Phase 1 (現在): 環境変数ベース簡易認証 + Flask-Session
- Phase 2: Flask-Login + bcrypt + Redis
- Phase 3: AWS Cognito統合 + MFA対応
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_cors import CORS
from functools import wraps
import uuid
import os
from datetime import datetime
from database import DatabaseManager

app = Flask(__name__)
CORS(app)

# セッション設定
# 将来的にはRedisセッションストアを使用
app.secret_key = os.getenv('SECRET_KEY', 'vecr-garage-dev-key')
app.permanent_session_lifetime = 3600  # 1時間

# 認証設定（環境変数から取得）
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')

# データベースマネージャーの初期化
db_manager = DatabaseManager()

def login_required(f):
    """
    認証デコレーター（モック実装）
    将来的にはFlask-Loginの@login_requiredに置き換え
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# モックデータ（将来的にはデータベースから取得）
# TODO: 実際のデータベース接続を実装し、SQLAlchemyまたはpsycopg2を使用してデータを取得
MOCK_DATA = {
    'human_members': [
        {
            'member_id': 1,
            'member_uuid': str(uuid.uuid4()),
            'member_name': 'Syota',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'member_id': 2,
            'member_uuid': str(uuid.uuid4()),
            'member_name': 'Rin',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ],
    'human_member_profiles': [
        {
            'profile_id': 1,
            'profile_uuid': str(uuid.uuid4()),
            'member_id': 1,
            'member_uuid': str(uuid.uuid4()),
            'bio': 'ソフトウェアエンジニア。Pythonが得意。',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ],
    'virtual_members': [
        {
            'member_id': 1,
            'member_uuid': str(uuid.uuid4()),
            'member_name': 'Kasen',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        },
        {
            'member_id': 2,
            'member_uuid': str(uuid.uuid4()),
            'member_name': 'Darcy',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ],
    'virtual_member_profiles': [
        {
            'profile_id': 1,
            'profile_uuid': str(uuid.uuid4()),
            'member_id': 1,
            'member_uuid': str(uuid.uuid4()),
            'llm_model': 'gpt-4',
            'custom_prompt': 'あなたは優秀なAIアシスタントです。',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ],
    'member_relationships': [
        {
            'relationship_id': 1,
            'from_member_uuid': str(uuid.uuid4()),
            'to_member_uuid': str(uuid.uuid4()),
            'relationship_type': 'mentor',
            'name_suffix': 'さん',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    ]
}

# テーブルスキーマ定義（モック用）
# TODO: 将来的にはデータベースのメタデータから動的に取得
TABLE_SCHEMAS = {
    'human_members': ['member_id', 'member_uuid', 'member_name', 'created_at', 'updated_at'],
    'human_member_profiles': ['profile_id', 'profile_uuid', 'member_id', 'member_uuid', 'bio', 'created_at', 'updated_at'],
    'virtual_members': ['member_id', 'member_uuid', 'member_name', 'created_at', 'updated_at'],
    'virtual_member_profiles': ['profile_id', 'profile_uuid', 'member_id', 'member_uuid', 'llm_model', 'custom_prompt', 'created_at', 'updated_at'],
    'member_relationships': ['relationship_id', 'from_member_uuid', 'to_member_uuid', 'relationship_type', 'name_suffix', 'created_at', 'updated_at']
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    ログインページ（モック実装）
    将来的にはFlask-WTFでCSRF保護、bcryptでパスワード検証
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # モック認証（将来的にはデータベース＋ハッシュ化パスワードで検証）
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            flash('ログインしました', 'success')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """
    ログアウト処理
    """
    session.clear()
    flash('ログアウトしました', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """
    メインページ（認証が必要）
    将来的にはJinjaテンプレートでデータベースの内容を動的に表示
    """
    return render_template('index.html', 
                         tables=list(MOCK_DATA.keys()),
                         username=session.get('username'))

@app.route('/api/tables')
@login_required
def get_tables():
    """テーブル一覧を取得（認証が必要）"""
    return jsonify(list(MOCK_DATA.keys()))

@app.route('/api/table/<table_name>')
@login_required
def get_table_data(table_name):
    """
    指定されたテーブルのデータを取得（認証が必要）
    TODO: 実際のデータベースクエリに置き換え
    """
    if table_name not in MOCK_DATA:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify({
        'columns': TABLE_SCHEMAS.get(table_name, []),
        'data': MOCK_DATA[table_name]
    })

@app.route('/api/table/<table_name>/record', methods=['POST'])
@login_required
def add_record(table_name):
    """
    レコードを追加（モック・認証が必要）
    TODO: 実際のデータベースINSERT操作に置き換え
    """
    if table_name not in MOCK_DATA:
        return jsonify({'error': 'Table not found'}), 404
    
    new_record = request.json
    new_record['created_at'] = datetime.now().isoformat()
    new_record['updated_at'] = datetime.now().isoformat()
    
    # モックなので、メモリ上のデータに追加するだけ
    MOCK_DATA[table_name].append(new_record)
    
    return jsonify({'success': True, 'record': new_record})

@app.route('/api/table/<table_name>/record/<int:record_id>', methods=['PUT'])
@login_required
def update_record(table_name, record_id):
    """
    レコードを更新（モック・認証が必要）
    TODO: 実際のデータベースUPDATE操作に置き換え
    """
    if table_name not in MOCK_DATA:
        return jsonify({'error': 'Table not found'}), 404
    
    updated_data = request.json
    updated_data['updated_at'] = datetime.now().isoformat()
    
    # モック実装：IDで検索して更新
    for i, record in enumerate(MOCK_DATA[table_name]):
        if record.get('member_id') == record_id or record.get('profile_id') == record_id or record.get('relationship_id') == record_id:
            MOCK_DATA[table_name][i].update(updated_data)
            return jsonify({'success': True, 'record': MOCK_DATA[table_name][i]})
    
    return jsonify({'error': 'Record not found'}), 404

@app.route('/api/table/<table_name>/record/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(table_name, record_id):
    """
    レコードを削除（モック・認証が必要）
    TODO: 実際のデータベースDELETE操作に置き換え
    """
    if table_name not in MOCK_DATA:
        return jsonify({'error': 'Table not found'}), 404
    
    # モック実装：IDで検索して削除
    for i, record in enumerate(MOCK_DATA[table_name]):
        if record.get('member_id') == record_id or record.get('profile_id') == record_id or record.get('relationship_id') == record_id:
            deleted_record = MOCK_DATA[table_name].pop(i)
            return jsonify({'success': True, 'deleted': deleted_record})
    
    return jsonify({'error': 'Record not found'}), 404

# データベース接続テスト用エンドポイント
@app.route('/api/db/test')
@login_required
def test_database_connection():
    """データベース接続テスト（認証が必要）"""
    try:
        # 接続テスト実行
        success = db_manager.test_connection()
        sqlalchemy_success = db_manager.test_sqlalchemy_connection()
        
        if success and sqlalchemy_success:
            # テーブル一覧を取得
            tables = db_manager.get_table_list()
            
            # 各テーブルのレコード数を確認
            table_counts = {}
            for table in tables:
                count = db_manager.get_table_count(table)
                table_counts[table] = count
            
            return jsonify({
                'success': True,
                'message': 'データベース接続成功',
                'connection_info': {
                    'host': db_manager.db_host,
                    'port': db_manager.db_port,
                    'database': db_manager.db_name,
                    'user': db_manager.db_user
                },
                'tables': tables,
                'table_counts': table_counts
            })
        else:
            return jsonify({
                'success': False,
                'message': 'データベース接続失敗',
                'psycopg2_success': success,
                'sqlalchemy_success': sqlalchemy_success
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'データベース接続テスト中にエラーが発生: {str(e)}'
        }), 500

@app.route('/api/db/table/<table_name>')
@login_required
def get_database_table_data(table_name):
    """実際のデータベースからテーブルデータを取得（認証が必要）"""
    try:
        table_data = db_manager.get_table_data(table_name)
        
        if table_data:
            return jsonify({
                'success': True,
                'data': table_data
            })
        else:
            return jsonify({
                'success': False,
                'message': f'テーブル "{table_name}" のデータ取得に失敗しました'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'テーブルデータ取得中にエラーが発生: {str(e)}'
        }), 500

@app.route('/api/db/tables')
@login_required
def get_database_tables():
    """利用可能なデータベーステーブル一覧を取得（認証が必要）"""
    try:
        tables = db_manager.get_table_list()
        
        # 各テーブルのレコード数を取得
        table_info = []
        for table in tables:
            count = db_manager.get_table_count(table)
            table_info.append({
                'name': table,
                'record_count': count
            })
        
        return jsonify({
            'success': True,
            'tables': table_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'テーブル一覧取得中にエラーが発生: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)