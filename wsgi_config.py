#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PythonAnywhere WSGI 配置文件
在 PythonAnywhere Web tab 的 "Code:" → "WSGI configuration file" 中粘贴此文件内容，
或把此文件路径指向 /home/你的用户名/mysite/wsgi_config.py
"""
import sys
import os

# 把项目目录加入 Python 路径
# 把下面路径改成您实际的目录，比如 /home/yourusername/mysite
project_home = os.path.dirname(os.path.abspath(__file__))
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 导入 Flask 应用
from flask_app import app as application
