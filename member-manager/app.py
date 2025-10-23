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
import logging
from datetime import datetime
from database import DatabaseManager

logger = logging.getLogger(__name__)

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

def get_column_description(column_name):
    """列の説明を取得"""
    descriptions = {
        # human_members
        'member_id': 'メンバーの一意識別子（自動採番）',
        'member_uuid': 'メンバーのUUID（グローバル一意識別子）',
        'member_name': 'メンバーの表示名',
        'created_at': 'レコード作成日時',
        'updated_at': 'レコード更新日時',
        
        # human_member_profiles
        'profile_id': 'プロフィールの一意識別子（自動採番）',
        'profile_uuid': 'プロフィールのUUID（グローバル一意識別子）',
        'bio': '自己紹介・プロフィール文',
        
        # virtual_members
        'llm_model': '使用するLLMモデル名',
        'custom_prompt': 'カスタムプロンプト設定',
        
        # member_relationships
        'relationship_id': '関係性の一意識別子（自動採番）',
        'from_member_uuid': '関係性の起点となるメンバーのUUID',
        'to_member_uuid': '関係性の終点となるメンバーのUUID',
        'relationship_type': '関係性の種類（mentor、mentee、peer等）',
        'name_suffix': '呼び方（さん、くん等）'
    }
    return descriptions.get(column_name, '列の説明')

# Jinja2テンプレートフィルターの登録
@app.template_filter('get_column_description')
def get_column_description_filter(column_name):
    """テンプレート用の列説明フィルター"""
    return get_column_description(column_name)

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

# ルート定義
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
    """ログアウト処理"""
    session.clear()
    flash('ログアウトしました', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/database')
@login_required
def database_view():
    """データベース管理画面を表示"""
    return render_template('database.html')

@app.route('/tables')
@login_required
def tables_view():
    """データベーステーブル一覧画面を表示"""
    try:
        # 利用可能なテーブル一覧を取得
        tables = db_manager.get_table_list()
        
        # 各テーブルの基本情報を取得
        table_info = []
        for table in tables:
            count = db_manager.get_table_count(table)
            table_info.append({
                'name': table,
                'record_count': count,
                'description': get_table_description(table)
            })
        
        return render_template('tables.html', tables=table_info)
        
    except Exception as e:
        flash(f'テーブル情報の取得に失敗しました: {str(e)}', 'error')
        return render_template('tables.html', tables=[])

@app.route('/table/<table_name>')
@login_required
def table_detail_view(table_name):
    """特定のテーブルの詳細画面を表示"""
    try:
        # テーブルの詳細データを取得
        table_data = db_manager.get_table_data(table_name)
        
        if table_data:
            return render_template('table_detail.html', 
                                table_data=table_data,
                                table_name=table_name)
        else:
            flash(f'テーブル "{table_name}" のデータ取得に失敗しました', 'error')
            return redirect(url_for('tables_view'))
            
    except Exception as e:
        flash(f'テーブル詳細の取得中にエラーが発生: {str(e)}', 'error')
        return redirect(url_for('tables_view'))

def get_table_description(table_name):
    """テーブルの説明を取得"""
    descriptions = {
        'human_members': '人間メンバーの基本情報（ID、名前、UUID等）',
        'human_member_profiles': '人間メンバーのプロフィール情報（自己紹介等）',
        'virtual_members': '仮想メンバーの基本情報（ID、名前、UUID等）',
        'virtual_member_profiles': '仮想メンバーのプロフィール情報（LLMモデル、プロンプト等）',
        'member_relationships': 'メンバー間の関係性情報（メンター・メンティー等）'
    }
    return descriptions.get(table_name, 'テーブルの説明')

@app.route('/api/table/<table_name>/record/<int:record_id>', methods=['PUT'])
@login_required
def update_record(table_name, record_id):
    """
    レコードを更新（UPSERT処理対応・認証が必要）
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'リクエストデータがありません'
            }), 400

        # メンバーテーブルでYMLファイルURIを持つ場合はWebhookフローを使用
        if table_name in ['human_members', 'virtual_members'] and 'yml_file_uri' in data:
            try:
                from storage_client import StorageClient
                from yaml_generator import YAMLGenerator

                member_name = data.get('member_name', '')
                yml_file_uri = data.get('yml_file_uri', '')

                # ストレージクライアントの初期化
                storage_client = StorageClient()

                # 更新データの準備
                form_data = {
                    'member_name': member_name
                }

                # テーブルタイプに応じた追加データ処理
                if table_name == 'human_members':
                    if 'bio' in data:
                        form_data['bio'] = data['bio']
                    yaml_content = YAMLGenerator.generate_human_member_yaml(form_data)
                else:  # virtual_members
                    # 仮想メンバーはllm_modelが必須
                    form_data['llm_model'] = data.get('llm_model', 'Claude')
                    if 'custom_prompt' in data:
                        form_data['custom_prompt'] = data['custom_prompt']
                    yaml_content = YAMLGenerator.generate_virtual_member_yaml(form_data)

                # ストレージにアップロード（Webhookが自動的にDB更新を実行）
                upload_result = storage_client.upload_yaml_file(yaml_content, yml_file_uri)

                return jsonify({
                    'success': True,
                    'message': f'{table_name}テーブルのレコードがWebhook経由で更新されます',
                    'upload_result': upload_result,
                    'webhook_note': 'データベースの更新はWebhookにより自動的に実行されます'
                })

            except Exception as e:
                logger.error(f"Webhook flow update error: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Webhook経由更新中にエラーが発生: {str(e)}'
                }), 500

        else:
            # 通常のUPDATE処理
            try:
                result = db_manager.update_record(table_name, record_id, data)

                if result:
                    # 関連テーブルの同期更新
                    db_manager.sync_related_tables(table_name, record_id, data)

                    return jsonify({
                        'success': True,
                        'message': f'{table_name}テーブルのレコードが更新されました',
                        'data': result
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'レコードの更新に失敗しました'
                    }), 500
            except Exception as e:
                logger.error(f"Database update error: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'データベース更新エラー: {str(e)}'
                }), 500

    except Exception as e:
        logger.error(f"Record update error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'レコード更新中にエラーが発生: {str(e)}'
        }), 500

@app.route('/api/table/<table_name>/record/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(table_name, record_id):
    """
    レコードを削除（認証が必要）
    """
    try:
        result = db_manager.delete_record(table_name, record_id)

        if result:
            return jsonify({
                'success': True,
                'message': f'{table_name}テーブルのレコードが削除されました'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'レコードの削除に失敗しました'
            }), 500

    except Exception as e:
        logger.error(f"Record deletion error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'レコード削除中にエラーが発生: {str(e)}'
        }), 500

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

@app.route('/api/table/<table_name>', methods=['GET'])
@login_required
def get_table_data_api(table_name):
    """テーブルデータをJSON形式で返すAPI"""
    try:
        table_data = db_manager.get_table_data(table_name)

        if table_data:
            return jsonify({
                'success': True,
                'table_name': table_name,
                'columns': [col.name for col in table_data.columns],
                'data': [dict(row._mapping) for row in table_data.data]
            })
        else:
            return jsonify({
                'success': False,
                'error': f'テーブル "{table_name}" のデータ取得に失敗しました'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'テーブルデータ取得中にエラーが発生: {str(e)}'
        }), 500

@app.route('/api/table/<table_name>/record', methods=['POST'])
@login_required
def create_table_record_api(table_name):
    """テーブルに新規レコードを作成するAPI"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'リクエストデータがありません'
            }), 400

        # データベースへの直接挿入
        result = db_manager.insert_record(table_name, data)

        if result:
            return jsonify({
                'success': True,
                'message': f'{table_name}テーブルにレコードが追加されました',
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'レコードの作成に失敗しました'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'レコード作成中にエラーが発生: {str(e)}'
        }), 500

@app.route('/api/member/create', methods=['POST'])
def create_member():
    """新規メンバー作成API
    
    フォームデータからYAMLファイルを生成し、ストレージにアップロードします。
    """
    try:
        from yaml_generator import YAMLGenerator
        from storage_client import StorageClient
        
        # リクエストデータの取得
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'リクエストデータがありません'
            }), 400
        
        # メンバータイプの取得
        member_type = data.get('member_type')
        if member_type not in ['human', 'virtual']:
            return jsonify({
                'success': False,
                'message': '無効なメンバータイプです'
            }), 400
        
        # フォームデータのバリデーション
        form_data = data.get('form_data', {})
        validation_errors = YAMLGenerator.validate_form_data(form_data, member_type)
        
        if validation_errors:
            return jsonify({
                'success': False,
                'message': 'バリデーションエラーがあります',
                'errors': validation_errors
            }), 400
        
        # YAMLファイルの生成
        if member_type == 'human':
            yaml_content = YAMLGenerator.generate_human_member_yaml(form_data)
        else:  # virtual
            yaml_content = YAMLGenerator.generate_virtual_member_yaml(form_data)
        
        # ストレージパスの生成
        member_name = form_data['member_name'].strip()
        storage_path = YAMLGenerator.generate_storage_path(member_name, member_type)
        
        # ストレージクライアントの初期化
        storage_client = StorageClient()
        
        # ストレージパスの検証
        if not storage_client.validate_storage_path(storage_path):
            return jsonify({
                'success': False,
                'message': '無効なストレージパスです'
            }), 400
        
        # YAMLファイルのアップロード（Webhookが自動的にDB更新を実行）
        upload_result = storage_client.upload_yaml_file(yaml_content, storage_path)

        return jsonify({
            'success': True,
            'message': f'{member_type}メンバー「{member_name}」のYAMLファイルを作成し、ストレージにアップロードしました。データベース登録は自動的に実行されます。',
            'data': {
                'member_name': member_name,
                'member_type': member_type,
                'storage_path': storage_path,
                'upload_result': upload_result,
                'webhook_note': 'データベースの登録はWebhookにより自動的に実行されます'
            }
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'データエラー: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Member creation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'メンバー作成中にエラーが発生: {str(e)}'
        }), 500

@app.route('/api/storage/info', methods=['GET'])
def get_storage_info():
    """ストレージサービスの情報を取得"""
    try:
        from storage_client import StorageClient
        
        storage_client = StorageClient()
        storage_info = storage_client.get_storage_info()
        
        return jsonify({
            'success': True,
            'data': storage_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'ストレージ情報取得中にエラーが発生: {str(e)}'
        }), 500

if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    
    # 環境変数を読み込み
    load_dotenv()
    
    host = os.getenv('MEMBER_MANAGER_HOST', '0.0.0.0')
    port = int(os.getenv('MEMBER_MANAGER_PORT', '8000'))
    debug = os.getenv('DEBUG', '0').lower() == '1'
    
    app.run(host=host, port=port, debug=debug)