# 使用 Python 3.13 作为基础镜像
FROM --platform=linux/amd64 python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖（如果需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml ./
COPY main.py ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir markdown>=3.5.0 fastapi>=0.104.0 uvicorn>=0.24.0

# 暴露端口
EXPOSE 8000

# 启动命令（作为 API 服务器运行）
CMD ["python", "main.py", "api"]

