from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from backend-db-registration!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)