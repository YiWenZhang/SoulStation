import requests
import random
import json

# 配置 (请确保后端已启动)
BASE_URL = "http://127.0.0.1:5000/api"


def generate_phone():
    """随机生成手机号，避免重复注册"""
    return f"136{random.randint(10000000, 99999999)}"


def print_separator(title):
    print(f"\n{'=' * 60}")
    print(f"   {title}")
    print(f"{'=' * 60}")


# ==========================================
# 1. 辅助：注册并登录 (获取 UID)
# ==========================================
def create_user_get_uid():
    phone = generate_phone()
    password = "password123"
    nickname = f"测试用户_{phone[-4:]}"

    # 1. 注册
    requests.post(f"{BASE_URL}/auth/register", json={
        "phone": phone, "password": password, "nickname": nickname
    })

    # 2. 登录
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "phone": phone, "password": password
    })

    data = resp.json()
    if data['code'] == 200:
        print(f"   [准备] 用户已创建: {nickname} (UID: {data['data']['uid']})")
        return data['data']['uid'], nickname
    else:
        raise Exception(f"登录失败: {data['msg']}")


# ==========================================
# 2. 测试用例：未登录拦截
# ==========================================
def test_unauthorized_access():
    print_separator("测试场景 1: 未登录访问 (无 UID)")

    try:
        url = f"{BASE_URL}/home/index"
        resp = requests.get(url)  # 不传 uid

        print(f"   请求: GET {url}")
        print(f"   状态码: {resp.status_code}")

        if resp.status_code == 401:
            print("   >>> [通过] 成功拦截未登录请求 (返回 401)")
        else:
            print(f"   !!! [失败] 预期 401，实际返回 {resp.status_code}")

    except Exception as e:
        print(f"   !!! [异常] {e}")


# ==========================================
# 3. 测试用例：已登录获取首页数据
# ==========================================
def test_home_data_structure():
    print_separator("测试场景 2: 获取首页数据 (验证字段结构)")

    try:
        # 1. 获取有效 UID
        uid, nickname = create_user_get_uid()

        # 2. 发起请求
        url = f"{BASE_URL}/home/index"
        resp = requests.get(url, params={'uid': uid})

        print(f"   请求: GET {url}?uid={uid}")

        if resp.status_code != 200:
            print(f"   !!! [失败] 接口报错: {resp.status_code}")
            return

        res_json = resp.json()
        data = res_json.get('data')

        # 3. 打印返回结果 (方便调试)
        print(f"   返回数据:\n{json.dumps(data, ensure_ascii=False, indent=2)}")

        # 4. 验证核心字段 (PRD 3.1.2)
        # ------------------------------------------------

        # (1) 验证 user_info
        if data.get('user_info') and data['user_info'].get('nickname') == nickname:
            print("   >>> [通过] user_info 字段正常")
        else:
            print("   !!! [失败] user_info 缺失或昵称不匹配")

        # (2) 验证 tracking_reminder (改善追踪)
        tr = data.get('tracking_reminder')
        if tr and 'show' in tr and 'message' in tr:
            if tr['show'] is False:
                print("   >>> [通过] tracking_reminder 结构正常 (新用户 show=False)")
            else:
                print("   !!! [警告] 新用户不应显示复测提醒")
        else:
            print("   !!! [失败] tracking_reminder 字段缺失")

        # (3) 验证 history_records (历史记录)
        hr = data.get('history_records')
        if isinstance(hr, list):
            print(f"   >>> [通过] history_records 列表存在 (当前长度: {len(hr)})")
        else:
            print("   !!! [失败] history_records 字段缺失或不是列表")

    except Exception as e:
        print(f"   !!! [异常] {e}")


if __name__ == "__main__":
    try:
        test_unauthorized_access()
        test_home_data_structure()
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接后端，请确保 run.py 正在运行！")