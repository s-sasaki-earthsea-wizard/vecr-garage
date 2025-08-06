#!/usr/bin/env python3
"""
Member Manager Mock Application
将来的にはJinjaテンプレートを使用してデータベースから動的にデータを取得する予定
現在はモックアップとしてハードコードされたデータを使用
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

@app.route('/')
def index():
    """
    メインページ
    将来的にはJinjaテンプレートでデータベースの内容を動的に表示
    """
    return render_template('index.html', tables=list(MOCK_DATA.keys()))

@app.route('/api/tables')
def get_tables():
    """テーブル一覧を取得"""
    return jsonify(list(MOCK_DATA.keys()))

@app.route('/api/table/<table_name>')
def get_table_data(table_name):
    """
    指定されたテーブルのデータを取得
    TODO: 実際のデータベースクエリに置き換え
    """
    if table_name not in MOCK_DATA:
        return jsonify({'error': 'Table not found'}), 404
    
    return jsonify({
        'columns': TABLE_SCHEMAS.get(table_name, []),
        'data': MOCK_DATA[table_name]
    })

@app.route('/api/table/<table_name>/record', methods=['POST'])
def add_record(table_name):
    """
    レコードを追加（モック）
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
def update_record(table_name, record_id):
    """
    レコードを更新（モック）
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
def delete_record(table_name, record_id):
    """
    レコードを削除（モック）
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)