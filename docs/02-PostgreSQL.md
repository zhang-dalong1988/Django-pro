# PostgreSQL

## 准备

```bash
$ cd code
$ mkdir ch2-postgresql
$ cd ch2-postgresql
```

## Django

创建 Django 项目

```bash
$ django-admin startproject django_project .
$ python manage.py migrate
$ python manage.py runserver
$ pip freeze > requirements.txt
```

修改 `requirements.txt` 文件

```
asgiref==3.9.1
Django==5.2.4
psycopg-binary==3.2.9
sqlparse==0.5.3
tzdata==2025.2
```

修改 `django_project/settings.py` 文件

```python
DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': BASE_DIR / 'db.sqlite3',
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "db",   # 在docker-compose.yml 中设置
        "PORT": 5432,   # 默认postgres端口
    }
}
```

## Django 数据库支持说明

Django 的 ORM 会自动为我们处理从 Python 代码到为每个数据库配置的 SQL 的转换。

[Django 官方数据库支持说明](https://docs.djangoproject.com/zh-hans/5.2/ref/databases/)

Django 5 最低支持 PostgreSQL 12 +([说明](https://docs.djangoproject.com/zh-hans/5.0/ref/databases/))

所需适配器版本：推荐使用最新版本，最新版本适配 PostgreSQL 14+

- psycopg2 >= 2.9.6
  - 二进制版本：psycopg2-binary
- psycopg >= 3.1.8
  - 二进制版本：psycopg-binary

## Docker

分别创建 `Dockerfile`、`docker-compose.yml` 以及 `.dockerignore` 文件

**Dockerfile** 使用与第一章内容相同的 Dockerfile 文件

```dockerfile
FROM python:3.13.5-slim-bullseye

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**.dockerignore**

```dockerignore
.venv
.git
.gitignore
```

**docker-compose.yml**

```yaml
# 指定 Docker Compose 项目名称
name: ch2-postgresql

# 定义服务列表
services:
  # Web 服务 - Django 应用
  web:
    # 使用当前目录的 Dockerfile 构建镜像
    build: .
    # 启动容器时执行的命令 - 运行 Django 开发服务器
    command: python /code/manage.py runserver 0.0.0.0:8000
    # 挂载卷 - 将当前目录映射到容器内的 /code 目录，实现代码热更新
    volumes:
      - .:/code
    # 端口映射 - 将主机的 8000 端口映射到容器的 8000 端口
    ports:
      - 8000:8000
    # 依赖关系 - 确保 db 服务先启动
    depends_on:
      - db

  # 数据库服务 - PostgreSQL
  db:
    # 使用官方 PostgreSQL 13 镜像
    image: postgres:14
    # 挂载卷 - 将 postgres_data 卷挂载到容器的数据目录，确保数据持久化
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    # 环境变量设置
    environment:
      # 设置身份验证方法为 trust，允许无密码连接（仅适用于开发环境）
      - "POSTGRES_HOST_AUTH_METHOD=trust"

# 定义卷 - 用于持久化存储数据
volumes:
  # postgres_data 卷用于存储 PostgreSQL 数据，确保容器重启后数据不丢失
  postgres_data:
```

**测试服务状态**

```bash
$ docker-compose up -d --build
```

> 刷新 `http://127.0.0.1:8000/` 的 Django 欢迎页面，它应该能正常工作，这意味着 Django 已成功通过 Docker 连接到 PostgreSQL。

**测试新数据库**

```bash
# 迁移数据库
$ docker-compose exec web python manage.py migrate
# 创建超级用户
# 用户名：postgresqladmin
# 密码：testpass123
# 邮箱：postgresqladmin@email.com
$ docker-compose exec web python manage.py createsuperuser
```

> 访问 `http://127.0.0.1:8000/admin/` 的 Django 管理页面，登录并验证。

## Git

```bash
$ git add .
$ git commit -m "ch2-数据库配置基础"
$ git push
```
