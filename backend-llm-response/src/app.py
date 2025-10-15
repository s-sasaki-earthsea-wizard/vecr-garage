from flask import Flask, jsonify, request
import os
import logging
from services.member_service import MemberService
from services.discord_notifier import DiscordNotifier

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello from backend-llm-response!'}

@app.route('/api/members/response')
def get_member_response():
    member_service = MemberService()

    try:
        response = member_service.get_member_responses()
        return jsonify(response)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/discord/webhooks', methods=['GET'])
def list_discord_webhooks():
    """
    登録されているDiscord Webhookの一覧を取得
    """
    try:
        notifier = DiscordNotifier()
        webhooks = notifier.list_webhooks()
        return jsonify({
            'success': True,
            'webhooks': webhooks,
            'count': len(webhooks)
        })
    except Exception as e:
        logger.error(f"Webhook一覧取得エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/discord/test/<webhook_name>', methods=['POST'])
def send_discord_test(webhook_name: str):
    """
    指定されたWebhookにテストメッセージを送信

    Args:
        webhook_name: 送信先Webhook名
    """
    try:
        notifier = DiscordNotifier()
        result = notifier.send_test_message(webhook_name)

        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"テストメッセージ送信エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/discord/send/<webhook_name>', methods=['POST'])
def send_discord_message(webhook_name: str):
    """
    指定されたWebhookにカスタムメッセージを送信

    Request Body:
        {
            "content": "メッセージ内容",
            "username": "表示名（オプション）",
            "avatar_url": "アバターURL（オプション）"
        }
    """
    try:
        data = request.get_json()

        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'contentフィールドが必要です'
            }), 400

        notifier = DiscordNotifier()
        result = notifier.send_message(
            webhook_name=webhook_name,
            content=data['content'],
            username=data.get('username'),
            avatar_url=data.get('avatar_url')
        )

        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"メッセージ送信エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/discord/broadcast', methods=['POST'])
def broadcast_discord_message():
    """
    複数のWebhookに同時配信

    Request Body:
        {
            "content": "メッセージ内容",
            "username": "表示名（オプション）",
            "avatar_url": "アバターURL（オプション）",
            "webhook_names": ["webhook1", "webhook2"] (オプション、未指定時は全Webhook)
        }
    """
    try:
        data = request.get_json()

        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'contentフィールドが必要です'
            }), 400

        notifier = DiscordNotifier()
        result = notifier.broadcast_message(
            content=data['content'],
            username=data.get('username'),
            avatar_url=data.get('avatar_url'),
            webhook_names=data.get('webhook_names')
        )

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"ブロードキャスト送信エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host=os.getenv("LLM_HOST", "0.0.0.0"),
        port=int(os.getenv("LLM_PORT", "3001"))
    )
