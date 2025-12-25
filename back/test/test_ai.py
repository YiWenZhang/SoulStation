from flask import Flask
from src.utils.ai_client import call_llm
from config import config_map

app = Flask(__name__)
app.config.from_object(config_map['default'])

with app.app_context():
    test_msg = [{"role": "user", "content": "你好，请问你是谁？"}]
    print("正在连接 AI...")
    reply = call_llm(test_msg)
    print(f"AI 回复: {reply}")