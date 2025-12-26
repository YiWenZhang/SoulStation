from openai import OpenAI
from flask import current_app


class AIClient:
    """
    AI 客户端封装类
    负责与大模型服务（如 DeepSeek, ChatGPT）进行通信
    """

    def _get_client(self):
        """
        内部方法：根据当前 app 配置初始化 OpenAI 客户端
        """
        api_key = current_app.config.get("AI_API_KEY")
        base_url = current_app.config.get("AI_BASE_URL")

        if not api_key:
            current_app.logger.error("未配置 AI_API_KEY")
            raise ValueError("未配置 AI_API_KEY，请在 config.py 或环境变量中设置。")

        # 初始化 OpenAI 客户端 (支持兼容 OpenAI 协议的其他模型，如 DeepSeek)
        return OpenAI(api_key=api_key, base_url=base_url)

    def get_response(self, messages, **kwargs):
        """
        普通对话 (用于生成报告)
        支持传入 temperature, response_format 等参数
        """
        client = self._get_client()
        model = current_app.config.get("AI_MODEL_NAME", "deepseek-chat")

        # 提取参数，设置默认值
        temperature = kwargs.get('temperature', 0.7)
        response_format = kwargs.get('response_format', None)  # 新增：支持 JSON 模式

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format=response_format,  # 关键：传给大模型
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            current_app.logger.error(f"AI Service Error: {str(e)}")
            raise e

    # 2. 流式方法也同步升级
    def get_stream_response(self, messages, **kwargs):
        """
        流式对话 (用于问诊聊天)
        """
        client = self._get_client()
        model = current_app.config.get("AI_MODEL_NAME", "deepseek-chat")

        temperature = kwargs.get('temperature', 0.7)

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            current_app.logger.error(f"AI Stream Error: {str(e)}")
            raise e