import os
from flask import current_app
# 引入 LangChain 组件
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage


class AIClient:
    def __init__(self):
        # 构造函数留空，避免在 import 阶段触发 current_app 上下文错误
        pass

    def _get_llm(self, temperature=0.7):
        """
        内部辅助方法：动态获取配置并创建 LangChain 对象
        """
        api_key = current_app.config.get('AI_API_KEY')
        base_url = current_app.config.get('AI_BASE_URL', 'https://api.deepseek.com')
        model_name = current_app.config.get('AI_MODEL_NAME', 'deepseek-chat')

        return ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature,
            streaming=True,
            max_tokens=2000
        )

    def _convert_history_to_langchain(self, messages_list):
        """
        将原生字典列表转换为 LangChain 的 Message 对象列表
        """
        lc_messages = []
        for msg in messages_list:
            role = msg.get('role')
            content = msg.get('content')
            if role == 'system':
                lc_messages.append(SystemMessage(content=content))
            elif role == 'user':
                lc_messages.append(HumanMessage(content=content))
            elif role == 'assistant':
                lc_messages.append(AIMessage(content=content))
        return lc_messages

    def get_response(self, messages, temperature=0.7, **kwargs):
        """
        非流式调用 (用于生成报告、影子分析)
        【修复】增加了 **kwargs 以接收 response_format 等额外参数
        """
        try:
            llm = self._get_llm(temperature)

            # 【关键修复】如果传入了 response_format (如强制 JSON)，需要绑定到模型
            if 'response_format' in kwargs:
                llm = llm.bind(response_format=kwargs['response_format'])

            lc_messages = self._convert_history_to_langchain(messages)

            # 调用 LangChain
            response = llm.invoke(lc_messages)
            return response.content

        except Exception as e:
            if current_app:
                current_app.logger.error(f"LangChain Invoke Error: {e}")
            return "{}"  # 返回空 JSON 字符串防止解析炸裂

    def get_stream_response(self, messages, temperature=0.7, **kwargs):
        """
        流式调用 (用于对话)
        【修复】同样增加了 **kwargs 保持接口一致性
        """
        try:
            llm = self._get_llm(temperature)

            lc_messages = self._convert_history_to_langchain(messages)

            for chunk in llm.stream(lc_messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            if current_app:
                current_app.logger.error(f"LangChain Stream Error: {e}")
            yield f"[AI连接错误: {str(e)}]"