# Django 企业级应用最佳实践

- Python 官方文档：<https://docs.python.org/zh-cn/3/contents.html>
- Django 官方文档：<https://docs.djangoproject.com/zh-hans/5.2/#django-documentation>

本机使用 python 3.13.5 版本，所以部分代码与原文不符，请参考代码

## 说明

- code 文件夹用于存放示例代码，docs 文件夹用于存放笔记

## 环境说明

Django 5 需要以下环境：

- Python 3.8+ -- 本地 3.13.5
- Django 5.2.4 -- 本地 5.2.4
- PostgreSQL 12+ -- 本地 14
  - psycopg2 >= 2.9.6 -- 本地 3.2.9
  - psycopg >= 3.1.8 -- 本地 3.2.9

## 概要

- 01 -- Django 项目开发环境搭建
- 02 -- PostgreSQL 数据库配置
- 03 -- 在线书店项目：涵盖 app 创建、自定义 User 模型、自定义表单、模板系统的使用、单元测试及测试用例的编写
- 04 -- 在线书店项目：实现了完整的用户注册流程，包括创建表单、视图和模板。

## Docker 命令速查

```bash
# 构建镜像
docker build -t <镜像名>:<标签> .

# 运行容器
docker run -d -p <主机端口>:<容器端口> --name <容器名> <镜像名>

# 查看运行中的容器
docker ps

# 查看所有容器（包括停止的）
docker ps -a

# 停止容器
docker stop <容器名或ID>

# 启动容器
docker start <容器名或ID>

# 重启容器
docker restart <容器名或ID>

# 删除容器
docker rm <容器名或ID>

# 查看镜像列表
docker images

# 删除镜像
docker rmi <镜像名或ID>

# 进入运行中的容器
docker exec -it <容器名或ID> /bin/bash

# 查看容器日志
docker logs <容器名或ID>

# 使用 docker-compose 启动服务
docker-compose up -d

# 使用 docker-compose 停止服务
docker-compose down

# 重新构建并启动服务
docker-compose up --build

# 查看 docker-compose 服务状态
docker-compose ps

# 查看 docker-compose 服务日志
docker-compose logs

# 启动容器 bash
docker exec -it <容器名或ID> /bin/bash

```
