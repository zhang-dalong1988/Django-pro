# 拉取基础镜像
FROM python:3.13.6-slim-bullseye

# 设置环境变量
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /code

# 安装依赖项
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# 复制项目
COPY . .