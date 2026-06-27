# 车辆调度系统 - PythonAnywhere 部署指南

## 📦 打包内容

```
vehicle-scheduling-pa/
├── flask_app.py          # Flask 主程序
├── database.py           # 数据库模块
├── scheduler.py          # 智能调度算法
├── wsgi_config.py        # WSGI 启动配置
├── requirements.txt      # Python 依赖
├── templates/            # HTML 模板
│   ├── index.html        # 首页（仪表盘）
│   ├── login.html        # 登录页
│   ├── register.html     # 注册页
│   ├── vehicles.html     # 车辆管理
│   ├── requests.html     # 用车申请
│   ├── schedule.html     # 智能调度
│   └── users.html        # 用户管理（管理员）
└── static/               # 静态资源
    ├── style.css
    └── script.js
```

---

## 🚀 部署步骤（约 10 分钟）

### 第1步：注册账号（2分钟）
打开 https://www.pythonanywhere.com
点 **"Start running Python online"**
- 用 **邮箱** 注册
- 牢记 **用户名**（会成为您的网址前缀）

### 第2步：上传代码（3分钟）
1. 登录后点顶部 **"Files"** 标签
2. 在左侧目录中点 **"mysite"** 进入（PythonAnywhere 默认目录）
   - 如果没有 `mysite` 目录，先 **"Create directory"** 创建
3. 进入 mysite 目录
4. 点击 **"Upload a file"** 上传以下文件：
   - `flask_app.py`
   - `database.py`
   - `scheduler.py`
   - `wsgi_config.py`
   - `requirements.txt`
5. 上传文件夹（点 **"Upload a file"** 一个一个上传也行）：
   - `templates` 文件夹
   - `static` 文件夹
6. **或者** 您可以先在本地打包成 zip，然后上传 zip，再在 Files 页面解压（需要 Bash）

### 第3步：打开 Bash 安装依赖（1分钟）
1. 点顶部 **"Consoles"** 标签
2. 点击 **"Bash"** 打开命令行
3. 输入以下命令：
```bash
cd ~/mysite
pip3 install --user -r requirements.txt
```

### 第4步：创建 Web App（3分钟）
1. 点顶部 **"Web"** 标签
2. 点 **"Add a new web app"**
3. 域名选 **"yourusername.pythonanywhere.com"**（默认）
4. 框架选 **"Flask"**
5. Python 版本选 **"3.11"**（或最新）
6. 直接点 Next 完成

### 第5步：配置 WSGI（1分钟）
1. 在 Web 页面找到 **"Code"** 区域
2. 点击 WSGI configuration file 链接（会打开编辑器）
3. **删掉全部内容**
4. 粘贴以下内容（注意：把 `yourusername` 改成您的真实用户名）：
```python
import sys
import os

project_home = '/home/yourusername/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from flask_app import app as application
```
5. **保存**（Ctrl+S 或右上角 Save 按钮）

### 第6步：配置静态文件（1分钟）
回到 **Web** 页面，找到 **"Static files"** 区域：
- **URL:** `/static/`
- **Directory:** `/home/yourusername/mysite/static/`
点 **"Add"** 添加

### 第7步：启动！
回到 **Web** 页面顶部，点 **绿色 "Reload" 按钮**

### 第8步：访问！
打开浏览器：
```
https://yourusername.pythonanywhere.com
```

---

## 🔐 默认登录账号

| 账号 | 密码 | 权限 |
|------|------|------|
| `admin` | `admin123` | 管理员（全部权限） |

⚠️ **第一次登录后请立即修改密码！**

---

## ❓ 遇到问题？

### 问题1：打开页面显示 500 错误
- 查看 **Web** 标签页的 **"Log files"** → 点击 **"Error log"**
- 常见原因：模块没安装好、文件路径错

### 问题2：模块找不到
- 在 Bash 控制台运行：
```bash
cd ~/mysite
ls -la
pip3 install --user -r requirements.txt
```

### 问题3：数据库错误
- 第一次启动会自动创建数据库文件 `~/vehicle_scheduling.db`
- 如果有问题，删除该文件后重启

### 问题4：静态文件 404
- 确认第6步的 `/static/` 路径正确

---

## 📞 获取帮助

如果有任何问题，把错误日志截图发给我，我帮您分析！
