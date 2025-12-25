## 环境配置
确保.env存在于back目录下，格式如下
```
# 1. 告诉 Flask 启动入口在哪里 (必须写，否则 flask db 命令会报错)
FLASK_APP=run.py

# 2. 设置环境模式 (默认为 development，开启调试模式)
FLASK_CONFIG=development

# 3. 安全密钥 (Session加密用)
SECRET_KEY=你的密钥

# 4.ai配置
AI_API_KEY=你的密码
AI_BASE_URL=https://api.deepseek.com
AI_MODEL_NAME=deepseek-chat
```

## 1.MySQL数据库的创建
```
CREATE DATABASE soulstation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2.数据库迁移脚本（建表）
```
cd back
# 1. 初始化（第一次执行，后面迁移不用）
flask --app run db init

# 2. 生成迁移脚本
flask --app run db migrate -m "init mysql"

# 3. 写入数据库
flask --app run db upgrade
```

## 3.导入数据指令
```
flask --app run init-data
```

## 4.测试专用数据库建立
```
CREATE DATABASE soulstation_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 5.deepseekAPI获取
```
flask init-ai-config
```