# === 获取基础镜像 ===
FROM python:3.13.5-slim-bullseye

# === 设置环境变量 ===
# 禁用 pip 版本检查
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# 禁用 Python 字节码缓存
ENV PYTHONDONTWRITEBYTECODE=1
# 禁用 Python 缓冲
ENV PYTHONUNBUFFERED=1

# === 设置工作目录 ===
# 设置根目录下的 code 为工作目录，后续所有命令都将在该目录下执行
# 例如：COPY ./requirements.txt . 将把 requirements.txt 文件复制到 /code 目录下
WORKDIR /code

# === 执行命令 ===
# 安装依赖
COPY ./requirements.txt .
# 使用清华大学镜像源安装依赖
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# 复制项目代码
COPY . .