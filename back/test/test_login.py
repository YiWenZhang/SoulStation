import requests
import json
import random

# 后端地址
BASE_URL = "http://127.0.0.1:5000/api/auth"

# 为了防止"手机号已存在"报错，我们每次随机生成一个手机号
random_phone = f"138{random.randint(10000000, 99999999)}"
print(f"--- 正在测试手机号: {random_phone} ---")


def test_register():
    url = f"{BASE_URL}/register"
    payload = {
        "phone": random_phone,
        "password": "password123",
        "nickname": "测试用户001"
    }

    # 发送 POST 请求
    print(f"\n1. [注册] 请求: {url}")
    response = requests.post(url, json=payload)

    # 打印结果
    print(f"   状态码: {response.status_code}")
    print(f"   返回体: {response.json()}")


def test_login():
    url = f"{BASE_URL}/login"
    payload = {
        "phone": random_phone,
        "password": "password123"
    }

    print(f"\n2. [登录] 请求: {url}")
    response = requests.post(url, json=payload)

    res_json = response.json()
    print(f"   状态码: {response.status_code}")
    print(f"   返回体: {res_json}")

    # 模拟前端：检查有没有拿到 token
    if response.status_code == 200 and res_json['code'] == 200:
        token = res_json['data']['token']
        uid = res_json['data']['uid']
        print(f"\n>>> 测试通过！前端应保存 -> UID: {uid}, Token: {token[:10]}...")
    else:
        print("\n>>> 测试失败！请检查后端日志。")


if __name__ == "__main__":
    try:
        test_register()
        test_login()
    except Exception as e:
        print(f"请求发送失败，请检查后端是否启动: {e}")