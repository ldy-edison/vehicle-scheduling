#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化（支持用户认证、车辆归还流程）
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'vehicle_scheduling.db'

def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 用户表（添加语言和邮箱）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',  -- 'admin' or 'user'
                language TEXT DEFAULT 'en',   -- 'zh', 'en', 'ar'
                email TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 车辆表（适配阿联酋车型，添加更多字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT DEFAULT 'available',  -- 'available', 'in_use', 'maintenance'
                current_location TEXT,
                last_return_time TEXT,
                purchase_date TEXT,
                license_plate TEXT,
                insurance_expiry TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 用车申请表（添加时间窗口和更多字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                requester_name TEXT NOT NULL,
                start_location TEXT NOT NULL,
                end_location TEXT NOT NULL,
                passengers INTEGER NOT NULL,
                request_time TEXT NOT NULL,
                start_time TEXT NOT NULL,  -- 用车开始时间
                end_time TEXT,              -- 预计归还时间
                actual_end_time TEXT,        -- 实际归还时间
                status TEXT DEFAULT 'pending',  -- 'pending', 'assigned', 'completed', 'cancelled'
                priority INTEGER DEFAULT 1,   -- 1=normal, 2=high, 3=urgent
                notes TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # 调度结果表（添加验收流程）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT NOT NULL,
                request_id INTEGER NOT NULL,
                scheduled_time TEXT DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'assigned',
                verified_by INTEGER,
                verified_time TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
                FOREIGN KEY (request_id) REFERENCES requests(id),
                FOREIGN KEY (verified_by) REFERENCES users(id)
            )
        ''')
        
        # 创建默认管理员账号 (admin/admin123)
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'admin')
        ''')
        
        conn.commit()
        print("✓ 数据库初始化完成")
        print("✓ 默认管理员账号：admin / admin123")
        
    except Exception as e:
        print(f"✗ 数据库初始化失败：{e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
