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

    def get_response(self, messages, temperature=0.7):
        """
        发送消息给大模型并获取回复

        :param messages: 对话历史列表, e.g. [{"role": "user", "content": "..."}]
        :param temperature: 随机度 (0-1)，默认 0.7
        :return: AI 的回复文本 (str)
        """
        client = self._get_client()
        model = current_app.config.get("AI_MODEL_NAME", "deepseek-chat")  # 默认值兜底

        try:
            # 发起请求
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )

            # 获取内容
            content = response.choices[0].message.content

            # (可选) 可以在这里打印日志方便调试
            # print(f">>> AI Response: {content[:50]}...")

            return content

        except Exception as e:
            # 记录错误日志
            current_app.logger.error(f"AI Service Error: {str(e)}")
            # 这里的异常建议抛出，交给 API 层去捕获并返回 500 错误给前端
            raise e

    def get_stream_response(self, messages, temperature=0.7):
        """
        流式生成回复 (Generator)
        """
        client = self._get_client()
        model = current_app.config.get("AI_MODEL_NAME", "deepseek-chat")

        try:
            # stream=True 是关键
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            for chunk in response:
                content = chunk.choices[0].delta.content
                # 过滤掉 None 或空字符串
                if content:
                    yield content

        except Exception as e:
            current_app.logger.error(f"AI Stream Error: {str(e)}")
            # 在流式中抛出异常比较特殊，通常前端会断开
            raise e