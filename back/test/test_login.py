import unittest
import json
# === 修改这里的导入路径 ===
from src import create_app         # 从 src/__init__.py 导入工厂函数
from src.extensions import db      # 从 src/extensions.py 导入 db 对象
from src.models import User        # 从 src/models.py 导入 User 模型
# 例如：如果你的 app 在 back/src/__init__.py 创建，可能需要 from back.src import create_app 等

class SoulStationAPITestCase(unittest.TestCase):
    def setUp(self):
        """测试前置操作：配置测试环境"""
        # 1. 使用工厂函数创建一个 app 实例
        # 【修改点】：将 'testing' 改为 'default'
        self.app = create_app('default')

        # 2. 强制修改配置用于测试
        # 这里会覆盖 default 中的配置，确保测试使用内存数据库
        self.app.config.update({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "ADMIN_SECRET_KEY": "SoulStation2025_Admin"
        })

        # 3. 初始化客户端和上下文
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # 4. 创建表结构
        db.create_all()

    def tearDown(self):
        """测试后置操作：清理环境"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==========================================================
    # 1. 注册接口测试 (Register Tests)
    # ==========================================================

    def test_register_normal_user_success(self):
        """测试：普通用户注册成功 (200)"""
        payload = {
            "phone": "13800000001",
            "password": "password123",  # 长度合法
            "role": "user"
        }
        response = self.client.post('/api/auth/register', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['code'], 200)
        self.assertIn("用户注册成功", data['msg'])

        # 验证数据库
        user = User.query.filter_by(phone="13800000001").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'user')

    def test_register_admin_success(self):
        """测试：管理员注册成功 - 密钥正确 (200)"""
        payload = {
            "phone": "13900000001",
            "password": "adminpass",
            "role": "admin",
            "admin_key": "SoulStation2025_Admin"  # 正确密钥
        }
        response = self.client.post('/api/auth/register', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertIn("管理员注册成功", data['msg'])

        # 验证角色
        user = User.query.filter_by(phone="13900000001").first()
        self.assertEqual(user.role, 'admin')

    def test_register_admin_wrong_key(self):
        """测试：管理员注册失败 - 密钥错误 (403)"""
        payload = {
            "phone": "13900000002",
            "password": "adminpass",
            "role": "admin",
            "admin_key": "WrongKey_123"
        }
        response = self.client.post('/api/auth/register', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['code'], 403)
        self.assertEqual(data['msg'], "管理员密钥错误，无法注册")

    # --- 新增校验逻辑测试 ---

    def test_register_password_too_short(self):
        """测试：密码长度过短 (400)"""
        payload = {
            "phone": "13800000001",
            "password": "123",  # < 6位
            "role": "user"
        }
        response = self.client.post('/api/auth/register', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['msg'], "密码长度不能少于6位")

    def test_register_password_too_long(self):
        """测试：密码长度过长 (400)"""
        payload = {
            "phone": "13800000001",
            "password": "a" * 21,  # > 20位
            "role": "user"
        }
        response = self.client.post('/api/auth/register', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['msg'], "密码长度不能超过20位")

    def test_register_invalid_phone_format(self):
        """测试：手机号格式错误 (400)"""
        # 情况1: 长度不对
        res1 = self.client.post('/api/auth/register', json={
            "phone": "138", "password": "password123"
        })
        self.assertEqual(res1.status_code, 400)
        self.assertEqual(res1.get_json()['msg'], "请输入有效的11位手机号码")

        # 情况2: 包含非数字
        res2 = self.client.post('/api/auth/register', json={
            "phone": "1380000000a", "password": "password123"
        })
        self.assertEqual(res2.status_code, 400)
        self.assertEqual(res2.get_json()['msg'], "请输入有效的11位手机号码")

    # -----------------------

    def test_register_duplicate_phone(self):
        """测试：手机号已存在 (400)"""
        # 先注册一个
        self.client.post('/api/auth/register', json={
            "phone": "13800000001", "password": "password123"
        })

        # 再次注册
        response = self.client.post('/api/auth/register', json={
            "phone": "13800000001", "password": "newpassword"
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['msg'], "该手机号已注册，请直接登录")

    # ==========================================================
    # 2. 登录接口测试 (Login Tests)
    # ==========================================================

    def test_login_success_return_role(self):
        """测试：登录成功并返回 Role (200)"""
        # 注册管理员
        self.client.post('/api/auth/register', json={
            "phone": "15000000000",
            "password": "password123",
            "role": "admin",
            "admin_key": "SoulStation2025_Admin"
        })

        # 登录
        response = self.client.post('/api/auth/login', json={
            "phone": "15000000000",
            "password": "password123"
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['code'], 200)

        # 关键验证
        self.assertIn('data', data)
        self.assertEqual(data['data']['role'], 'admin')  # 确保返回了 role
        self.assertIn('token', data['data'])

    def test_login_fail_wrong_password(self):
        """测试：登录密码错误 (401)"""
        self.client.post('/api/auth/register', json={
            "phone": "15000000001", "password": "rightpassword"
        })

        response = self.client.post('/api/auth/login', json={
            "phone": "15000000001",
            "password": "wrongpassword"
        })
        data = response.get_json()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 401)
        self.assertEqual(data['msg'], "账号或密码错误")

    def test_login_fail_user_not_found(self):
        """测试：用户不存在 (401)"""
        response = self.client.post('/api/auth/login', json={
            "phone": "19999999999",
            "password": "any"
        })
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()['msg'], "账号或密码错误")


if __name__ == '__main__':
    unittest.main()