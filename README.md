创建数据库
CREATE DATABASE `app` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

pywe_django/settings.py 内设置库名和账号密码, wego 的初始化信息

注意新创建的 app __init__.py 内要加入
import pymysql
pymysql.install_as_MySQLdb()
