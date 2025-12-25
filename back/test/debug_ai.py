# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

api_key = os.getenv('AI_API_KEY')
base_url = os.getenv('AI_BASE_URL', 'https://api.deepseek.com')

print(f"--- 调试信息 ---")
print(f"读取到的 Key 长度: {len(api_key) if api_key else 0}")
print(f"API 地址: {base_url}")

client = OpenAI(api_key=api_key, base_url=base_url)

try:
    print("正在发送请求到 DeepSeek...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "Hi"}], # 先用英文测试，排除中文干扰
        temperature=0.7
    )
    print("✅ 连接成功！")
    print(f"AI 回复: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ 连接失败")
    # 使用 repr 避免打印异常描述时的编码错误
    print(f"错误详情: {repr(e)}")