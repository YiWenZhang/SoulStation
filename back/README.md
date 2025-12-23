## 1.MySQL数据库的创建
```
CREATE DATABASE soulstation_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2.数据库初始化
```
cd back
# 1. 初始化
flask --app run db init

# 2. 生成迁移脚本
flask --app run db migrate -m "init mysql"

# 3. 写入数据库
flask --app run db upgrade
```

## 3.数据库迁移-创建问卷
```
cd back
flask --app run db migrate -m "add question tables"
flask --app run db upgrade
flask --app run init-data

flask init-data
```