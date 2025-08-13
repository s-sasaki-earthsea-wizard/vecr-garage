from flask import Flask, jsonify
import os
from services.member_service import MemberService

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

if __name__ == '__main__':
    app.run(
        host=os.getenv("LLM_HOST", "0.0.0.0"), 
        port=int(os.getenv("LLM_PORT", "3001"))
    )
