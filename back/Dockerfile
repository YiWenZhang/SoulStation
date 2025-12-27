# 使用官方 Python 轻量镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量 (防止生成 .pyc 文件，设置 stdout 无缓冲)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 复制依赖文件
COPY requirements.txt .

# 安装依赖 (使用清华源加速)
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令 (使用 gunicorn 生产级服务器)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]