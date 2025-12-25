## 1.MySQL数据库的创建
```
CREATE DATABASE soulstation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2.数据库迁移脚本（建表）
```
cd back
# 1. 初始化
flask --app run db init

# 2. 生成迁移脚本
flask --app run db migrate -m "init mysql"

# 3. 写入数据库
flask --app run db upgrade
```

## 3.导入数据指令
```
flask init-data
```

## 4.测试专用数据库建立
```
CREATE DATABASE soulstation_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```