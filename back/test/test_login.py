import requests
import json
import random

# 配置
BASE_URL = "http://127.0.0.1:5000/api/auth"
# 必须与后端 config.py 中的 ADMIN_SECRET_KEY 一致
ADMIN_KEY_CORRECT = "SoulStation2025_Admin"
ADMIN_KEY_WRONG = "Im_A_Hacker"


def generate_phone():
    """随机生成手机号，避免重复"""
    return f"139{random.randint(10000000, 99999999)}"


def print_separator(title):
    print(f"\n{'=' * 50}")
    print(f"   {title}")
    print(f"{'=' * 50}")


# ==========================================
# 1. 测试普通用户流程
# ==========================================
def test_user_flow():
    print_separator("测试场景 A: 普通用户")
    phone = generate_phone()

    # --- 1.1 注册 ---
    url_reg = f"{BASE_URL}/register"
    payload_reg = {
        "phone": phone,
        "password": "user123",
        "nickname": "普通用户01"
        # 不传 role，默认就是 user
    }
    print(f"[1. 注册] 尝试注册普通用户: {phone}")
    resp = requests.post(url_reg, json=payload_reg)
    print(f"   -> 状态码: {resp.status_code}, 消息: {resp.json().get('msg')}")

    # --- 1.2 登录 ---
    url_login = f"{BASE_URL}/login"
    payload_login = {
        "phone": phone,
        "password": "user123"
    }
    print(f"[2. 登录] 尝试登录...")
    resp = requests.post(url_login, json=payload_login)
    data = resp.json()

    if data['code'] == 200:
        role = data['data'].get('role')
        uid = data['data'].get('uid')
        print(f"   >>> [通过] 登录成功! UID: {uid}, 角色: {role}")
        if role != 'user':
            print(f"   !!! [警告] 预期角色是 user，但实际是 {role}")
    else:
        print(f"   >>> [失败] {data.get('msg')}")


# ==========================================
# 2. 测试管理员流程
# ==========================================
def test_admin_flow():
    print_separator("测试场景 B: 管理员 (含密钥验证)")
    phone = generate_phone()
    url_reg = f"{BASE_URL}/register"

    # --- 2.1 注册失败测试 (密钥错误) ---
    print(f"[1. 负面测试] 尝试用错误密钥注册管理员: {phone}")
    payload_wrong = {
        "phone": phone,
        "password": "admin123",
        "role": "admin",
        "admin_key": ADMIN_KEY_WRONG  # <--- 错误的
    }
    resp = requests.post(url_reg, json=payload_wrong)
    print(f"   -> 状态码: {resp.status_code} (预期 403)")
    print(f"   -> 消息: {resp.json().get('msg')}")

    if resp.status_code != 403:
        print("   !!! [严重错误] 后端没有拦截错误的管理员注册请求！")
        return

    # --- 2.2 注册成功测试 (密钥正确) ---
    print(f"\n[2. 正面测试] 尝试用正确密钥注册管理员...")
    payload_correct = {
        "phone": phone,  # 复用同一个手机号，因为上一步注册应该失败了，手机号未被占用
        "password": "admin123",
        "role": "admin",
        "admin_key": ADMIN_KEY_CORRECT,  # <--- 正确的
        "nickname": "超级管理员"
    }
    resp = requests.post(url_reg, json=payload_correct)
    print(f"   -> 状态码: {resp.status_code}, 消息: {resp.json().get('msg')}")

    # --- 2.3 登录验证角色 ---
    print(f"\n[3. 登录] 管理员登录检查角色...")
    url_login = f"{BASE_URL}/login"
    payload_login = {
        "phone": phone,
        "password": "admin123"
    }
    resp = requests.post(url_login, json=payload_login)
    data = resp.json()

    if data['code'] == 200:
        role = data['data'].get('role')
        print(f"   >>> [通过] 登录成功! 角色: {role}")
        if role == 'admin':
            print("   >>> [完美] 前端识别到 admin，应跳转至后台管理页。")
        else:
            print(f"   !!! [失败] 期望 admin，实际是 {role}")
    else:
        print(f"   >>> [失败] {data.get('msg')}")


if __name__ == "__main__":
    try:
        # 先测普通用户
        test_user_flow()
        # 再测管理员
        test_admin_flow()
    except requests.exceptions.ConnectionError:
        print("\n[错误] 连接被拒绝。请确保后端服务 (run.py) 正在运行！")
    except Exception as e:
        print(f"\n[错误] 测试脚本发生未知异常: {e}")