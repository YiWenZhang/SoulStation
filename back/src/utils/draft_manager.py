import os
import json
from flask import current_app

class DraftManager:
    """
    负责管理影子分析的临时文件 (替代数据库存储)
    文件路径: /back/instance/drafts/draft_{id}.json
    """

    @staticmethod
    def _get_file_path(consultation_id):
        # 确保目录存在
        # 使用 instance_path 是 Flask 的标准做法，适合放运行时产生的文件
        base_dir = os.path.join(current_app.instance_path, 'drafts')
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        return os.path.join(base_dir, f"draft_{consultation_id}.json")

    @staticmethod
    def load_draft(consultation_id):
        """读取草稿，如果不存在返回空字典"""
        path = DraftManager._get_file_path(consultation_id)
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading draft: {e}")
            return {}

    @staticmethod
    def save_draft(consultation_id, data):
        """保存草稿 (覆盖写入)"""
        path = DraftManager._get_file_path(consultation_id)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving draft: {e}")
            return False

    @staticmethod
    def delete_draft(consultation_id):
        """生成完报告后删除临时文件"""
        path = DraftManager._get_file_path(consultation_id)
        if os.path.exists(path):
            os.remove(path)