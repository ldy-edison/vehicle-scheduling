# Zeabur 部署指南

## 准备工作

1. 访问 https://zeabur.com
2. 点击右上角 "Sign Up" 注册账号
   - 可以用 GitHub 登录（推荐）
   - 或者用邮箱注册

## 部署步骤

### 方法一：GitHub 导入（推荐）

1. 在 GitHub 上创建一个新仓库（Public）
2. 把 zip 包里的文件上传到 GitHub 仓库
3. 在 Zeabur 点击 "New Project" → "Deploy from GitHub"
4. 选择刚才创建的仓库
5. Zeabur 会自动检测为 Python 项目
6. 在 "Settings" → "Build & Deploy" 中确认 Start Command 为：
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```
7. 等待部署完成（约 1-2 分钟）
8. 在 "Domains" 中获取公网地址

### 方法二：CLI 部署

1. 安装 CLI：`npm install -g @zeabur/cli`
2. 登录：`zeabur login`
3. 解压 zip 到文件夹，进入该文件夹
4. 部署：`zeabur deploy`

## 配置说明

### 数据库

Zeabur 部署后，SQLite 数据库每次重新部署会丢失。
如需持久化存储，需要添加 MySQL 或 PostgreSQL 数据库插件。

### 环境变量

如需设置环境变量，在 Zeabur 项目 Settings → Environment Variables 中添加。

### 域名

Zeabur 会自动分配一个 `.zeabur.app` 域名。
可以在 Domains 中绑定自定义域名。

## 友情提示

- 免费版有 5 美元/月额度，这个小应用完全够用
- 首次部署后，ZIP 包里的代码自动上传并部署
