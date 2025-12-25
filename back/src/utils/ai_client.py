from openai import OpenAI
from flask import current_app


def get_ai_client():
    """
    根据当前 app 的配置初始化 OpenAI 客户端
    """
    api_key = current_app.config.get("AI_API_KEY")
    base_url = current_app.config.get("AI_BASE_URL")

    if not api_key:
        raise ValueError("未配置 AI_API_KEY，请在 config.py 或环境变量中设置。")

    return OpenAI(api_key=api_key, base_url=base_url)


def call_llm(messages, temperature=0.7):
    """
    发送消息给大模型
    :param messages: 格式为 [{"role": "user", "content": "..."}]
    :return: AI 的回复文本
    """
    client = get_ai_client()
    model = current_app.config.get("AI_MODEL_NAME")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        # 打印错误到控制台方便调试
        print(f"--- AI 调用异常 ---")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {str(e)}")
        return "（医生正在整理思绪...）抱歉，连接有点不稳定，您可以再说一次吗？"