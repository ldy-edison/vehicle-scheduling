#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vehicle Scheduling System - Main Application
Supports: User authentication, detailed statistics, multi-language (EN/ZH/AR), UAE localization
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from datetime import datetime
import os
import sys

# Add current directory to path for importing scheduler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'vehicle_scheduling_secret_key_2026'
CORS(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role, language='en'):
        self.id = id
        self.username = username
        self.role = role
        self.language = language

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, language FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return User(row[0], row[1], row[2], row[3])
    return None

# ==================== Multi-language Support ====================

LANGUAGES = {
    'en': {
        'login': 'Login',
        'register': 'Register',
        'username': 'Username',
        'password': 'Password',
        'submit': 'Submit',
        'cancel': 'Cancel',
        'dashboard': 'Dashboard',
        'vehicles': 'Vehicles',
        'requests': 'Requests',
        'schedule': 'Schedule',
        'logout': 'Logout',
        'today_requests': "Today's Requests",
        'completion_rate': 'Completion Rate',
        'vehicle_utilization': 'Vehicle Utilization',
        'available_vehicles': 'Available Vehicles',
        'vehicle_return_times': 'Vehicle Return Times',
        'quick_actions': 'Quick Actions',
        'add_vehicle': 'Add Vehicle',
        'vehicle_id': 'Vehicle ID',
        'vehicle_type': 'Vehicle Type',
        'capacity': 'Capacity',
        'status': 'Status',
        'actions': 'Actions',
        'delete': 'Delete',
        'edit': 'Edit',
        'confirm_return': 'Confirm Return',
        'submit_request': 'Submit Request',
        'requester_name': 'Requester Name',
        'start_location': 'Start Location',
        'end_location': 'End Location',
        'passengers': 'Passengers',
        'request_time': 'Request Time',
        'notes': 'Notes',
        'run_schedule': 'Run Schedule',
        'reset_schedule': 'Reset Schedule',
        'success': 'Success',
        'error': 'Error',
        'loading': 'Loading...',
        'no_data': 'No data available',
        'confirm': 'Confirm',
        'available': 'Available',
        'in_use': 'In Use',
        'maintenance': 'Maintenance',
        'pending': 'Pending',
        'assigned': 'Assigned',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'select_vehicle_type': 'Select Vehicle Type',
        'add': 'Add',
        'vehicle_list': 'Vehicle List',
        'return_time': 'Return Time',
        'no_vehicles': 'No vehicles yet, please add some',
        'confirm_delete': 'Confirm Delete',
        'are_you_sure': 'Are you sure?',
        'yes': 'Yes',
        'no': 'No',
        'select': 'Select',
        'all': 'All',
        'filter': 'Filter',
        'search': 'Search',
        'save': 'Save',
        'request_list': 'Request List',
        'schedule_result': 'Schedule Result',
        'user_management': 'User Management',
        'set_admin': 'Set Admin',
        'remove_admin': 'Remove Admin',
        'users': 'Users',
        'confirm_set_role': 'Confirm Set Role',
        'confirm_delete_user': 'Confirm Delete User',
        'welcome_message': 'Welcome back',
        'fleet_overview': "Here is your fleet overview",
        'vehicle_type_distribution': 'Vehicle Type Distribution',
        'request_status_distribution': 'Request Status Distribution',
        'vehicle_status_distribution': 'Vehicle Status Distribution',
        'daily_request_trend': 'Daily Request Trend (Last 7 Days)',
        'expected_return': 'Expected Return'
    },
    'zh': {
        'login': '登录',
        'register': '注册',
        'username': '用户名',
        'password': '密码',
        'submit': '提交',
        'cancel': '取消',
        'dashboard': '仪表盘',
        'vehicles': '车辆管理',
        'requests': '用车申请',
        'schedule': '智能调度',
        'logout': '退出',
        'today_requests': '今日申请',
        'completion_rate': '完成率',
        'vehicle_utilization': '车辆利用率',
        'available_vehicles': '可用车辆',
        'vehicle_return_times': '车辆归还时间',
        'quick_actions': '快速操作',
        'add_vehicle': '添加车辆',
        'vehicle_id': '车辆编号',
        'vehicle_type': '车型',
        'capacity': '容量',
        'status': '状态',
        'actions': '操作',
        'delete': '删除',
        'edit': '编辑',
        'confirm_return': '确认归还',
        'submit_request': '提交申请',
        'requester_name': '申请人',
        'start_location': '出发地',
        'end_location': '目的地',
        'passengers': '乘客人数',
        'request_time': '用车时间',
        'notes': '备注',
        'run_schedule': '执行调度',
        'reset_schedule': '重置调度',
        'success': '成功',
        'error': '错误',
        'loading': '加载中...',
        'no_data': '暂无数据',
        'confirm': '确认',
        'available': '可用',
        'in_use': '使用中',
        'maintenance': '维修中',
        'pending': '待分配',
        'assigned': '已分配',
        'completed': '已完成',
        'cancelled': '已取消',
        'select_vehicle_type': '选择车型',
        'add': '添加',
        'vehicle_list': '车辆列表',
        'return_time': '归还时间',
        'no_vehicles': '暂无车辆，请先添加',
        'confirm_delete': '确认删除',
        'are_you_sure': '确定要删除吗？',
        'yes': '是',
        'no': '否',
        'select': '请选择',
        'all': '全部',
        'filter': '筛选',
        'search': '搜索',
        'save': '保存',
        'request_list': '申请列表',
        'schedule_result': '调度结果',
        'user_management': '用户管理',
        'set_admin': '设为管理员',
        'remove_admin': '取消管理员',
        'users': '用户',
        'confirm_set_role': '确认设置角色',
        'confirm_delete_user': '确认删除用户',
        'welcome_message': '欢迎回来',
        'fleet_overview': '这是您的车队概览',
        'vehicle_type_distribution': '车辆类型分布',
        'request_status_distribution': '申请状态分布',
        'vehicle_status_distribution': '车辆状态分布',
        'daily_request_trend': '每日申请趋势（最近7天）',
        'expected_return': '预计归还时间'
    },
    'ar': {
        'login': 'تسجيل الدخول',
        'register': 'تسجيل',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'submit': 'إرسال',
        'cancel': 'إلغاء',
        'dashboard': 'لوحة التحكم',
        'vehicles': 'المركبات',
        'requests': 'طلبات السيارات',
        'schedule': 'الجدولة الذكية',
        'logout': 'تسجيل خروج',
        'today_requests': 'طلبات اليوم',
        'completion_rate': 'معدل الإنجاز',
        'vehicle_utilization': 'معدل استخدام المركبات',
        'available_vehicles': 'المركبات المتاحة',
        'vehicle_return_times': 'أوقات إرجاع المركبات',
        'quick_actions': 'إجراءات سريعة',
        'add_vehicle': 'إضافة مركبة',
        'vehicle_id': 'رقم المركبة',
        'vehicle_type': 'نوع المركبة',
        'capacity': 'السعة',
        'status': 'الحالة',
        'actions': 'الإجراءات',
        'delete': 'حذف',
        'edit': 'تعديل',
        'confirm_return': 'تأكيد الإرجاع',
        'submit_request': 'إرسال الطلب',
        'requester_name': 'اسم الطالب',
        'start_location': 'نقطة الانطلاق',
        'end_location': 'نقطة الوصول',
        'passengers': 'عدد الركاب',
        'request_time': 'وقت الطلب',
        'notes': 'ملاحظات',
        'run_schedule': 'تنفيذ الجدولة',
        'reset_schedule': 'إعادة تعيين الجدولة',
        'success': 'نجاح',
        'error': 'خطأ',
        'loading': 'جاري التحميل...',
        'no_data': 'لا توجد بيانات',
        'confirm': 'تأكيد',
        'available': 'متاح',
        'in_use': 'قيد الاستخدام',
        'maintenance': 'قيد الصيانة',
        'pending': 'قيد الانتظار',
        'assigned': 'تم التعيين',
        'completed': 'تم الإنجاز',
        'cancelled': 'تم الإلغاء',
        'select_vehicle_type': 'اختر نوع المركبة',
        'add': 'إضافة',
        'vehicle_list': 'قائمة المركبات',
        'return_time': 'وقت الإرجاع',
        'no_vehicles': 'لا توجد مركبات بعد، يرجى الإضافة',
        'confirm_delete': 'تأكيد الحذف',
        'are_you_sure': 'هل أنت متأكد؟',
        'yes': 'نعم',
        'no': 'لأ',
        'select': 'اختر',
        'all': 'الكل',
        'filter': 'تصفية',
        'search': 'بحث',
        'save': 'حفظ',
        'request_list': 'قائمة الطلبات',
        'schedule_result': 'نتيجة الجدولة',
        'user_management': 'إدارة المستخدمين',
        'set_admin': 'تعيين كمدير',
        'remove_admin': 'إلغاء صلاحية المدير',
        'users': 'المستخدمين',
        'confirm_set_role': 'تأكيد تعيين الدور',
        'confirm_delete_user': 'تأكيد حذف المستخدم',
        'welcome_message': 'مرحبا بعودتك',
        'fleet_overview': 'هذه هي نظرة عامة على أسطولك',
        'vehicle_type_distribution': 'توزيع أنواع المركبات',
        'request_status_distribution': 'توزيع حالة الطلبات',
        'vehicle_status_distribution': 'توزيع حالة المركبات',
        'daily_request_trend': 'اتجاه الطلبات اليومية (آخر 7 أيام)',
        'expected_return': 'وقت الإرجاع المتوقع'
    }
}

def get_text(key, lang=None):
    """Get translated text"""
    if lang is None:
        if current_user.is_authenticated:
            lang = current_user.language
        else:
            lang = session.get('language', 'en')
    
    return LANGUAGES.get(lang, {}).get(key, key)

# Inject translation function into all templates
@app.context_processor
def inject_get_text():
    return dict(t=get_text, current_lang=session.get('language', 'en'))

# ==================== Routes ====================

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user, t=get_text)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, role, language FROM users WHERE username = ? AND password = ?', 
                     (username, password))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            user = User(row[0], row[1], row[2], row[3])
            login_user(user)
            session['language'] = row[3]
            return redirect(url_for('index'))
        else:
            flash(get_text('error') + ': ' + get_text('username') + ' / ' + get_text('password'), 'error')
    
    return render_template('login.html', t=get_text)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('language', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        language = request.form.get('language', 'en')
        
        conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO users (username, password, role, language) VALUES (?, ?, ?, ?)',
                         (username, password, 'user', language))
            conn.commit()
            flash(get_text('success') + '! ' + get_text('login'), 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash(get_text('username') + ' ' + get_text('error'), 'error')
        finally:
            conn.close()
    
    return render_template('register.html', t=get_text)

@app.route('/set-language/<lang>')
def set_language(lang):
    """Set language"""
    if lang in LANGUAGES:
        session['language'] = lang
        if current_user.is_authenticated:
            conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET language = ? WHERE id = ?', (lang, current_user.id))
            conn.commit()
            conn.close()
    return redirect(request.referrer or url_for('index'))

# ==================== Page Routes ====================

@app.route('/vehicles')
@login_required
def vehicles_page():
    return render_template('vehicles.html', user=current_user, t=get_text)

@app.route('/requests')
@login_required
def requests_page():
    return render_template('requests.html', user=current_user, t=get_text)

@app.route('/schedule')
@login_required
def schedule_page():
    return render_template('schedule.html', user=current_user, t=get_text)

@app.route('/users')
@login_required
def users_page():
    """User management page (admin only)"""
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    return render_template('users.html', user=current_user, t=get_text)

# ==================== API Endpoints (Basic Statistics) ====================

@app.route('/api/stats')
@login_required
def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    
    try:
        # Today's requests
        cursor.execute('''
            SELECT COUNT(*) FROM requests 
            WHERE DATE(created_time) = DATE('now')
        ''')
        today_requests = cursor.fetchone()[0]
        
        # Completion rate
        cursor.execute('SELECT COUNT(*) FROM requests')
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM requests WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        completion_rate = round(completed / total * 100, 1) if total > 0 else 0
        
        # Vehicle utilization
        cursor.execute('SELECT COUNT(*) FROM vehicles')
        total_vehicles = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'in_use'")
        in_use = cursor.fetchone()[0]
        utilization_rate = round(in_use / total_vehicles * 100, 1) if total_vehicles > 0 else 0
        
        # Available vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'available'")
        available = cursor.fetchone()[0]
        
        return jsonify({
            'today_requests': today_requests,
            'completion_rate': completion_rate,
            'utilization_rate': utilization_rate,
            'available_vehicles': available
        })
    finally:
        conn.close()

@app.route('/api/stats/detailed')
@login_required
def get_detailed_stats():
    """Get detailed statistics (for charts)"""
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    
    try:
        # Vehicle type distribution
        cursor.execute('''
            SELECT type, COUNT(*) as count 
            FROM vehicles 
            GROUP BY type
        ''')
        vehicle_types = [{'type': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Request status distribution
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM requests 
            GROUP BY status
        ''')
        request_status = [{'status': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Vehicle status distribution
        cursor.execute('''
            SELECT status, COUNT(*) as count 
            FROM vehicles 
            GROUP BY status
        ''')
        vehicle_status = [{'status': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # Daily request trend (last 7 days)
        cursor.execute('''
            SELECT 
                DATE(created_time) as date,
                COUNT(*) as count
            FROM requests
            WHERE created_time >= DATE('now', '-7 days')
            GROUP BY DATE(created_time)
            ORDER BY date
        ''')
        daily_requests = [{'date': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        return jsonify({
            'vehicle_types': vehicle_types,
            'request_status': request_status,
            'vehicle_status': vehicle_status,
            'daily_requests': daily_requests
        })
    finally:
        conn.close()

@app.route('/api/vehicles', methods=['GET', 'POST'])
@login_required
def vehicles_api():
    if request.method == 'POST':
        data = request.get_json()
        conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO vehicles (id, type, capacity) VALUES (?, ?, ?)',
                         (data['id'], data['type'], data['capacity']))
            conn.commit()
            return jsonify({'success': True, 'message': get_text('success')})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Vehicle ID already exists'})
        finally:
            conn.close()
    
    # GET request
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vehicles ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    
    vehicles = []
    for row in rows:
        vehicles.append({
            'id': row[0],
            'type': row[1],
            'capacity': row[2],
            'status': row[3],
            'last_return_time': row[4]
        })
    
    return jsonify(vehicles)

@app.route('/api/vehicles/<vehicle_id>', methods=['DELETE'])
@login_required
def delete_vehicle(vehicle_id):
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': get_text('success')})

@app.route('/api/requests', methods=['GET', 'POST'])
@login_required
def requests_api():
    if request.method == 'POST':
        data = request.get_json()
        conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO requests (user_id, requester_name, start_location, end_location, passengers, request_time, start_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (current_user.id, data['requester_name'], data['start_location'], data['end_location'], 
             data['passengers'], data['request_time'], data.get('start_time', data['request_time'])))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': get_text('success')})
    
    # GET request
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    
    if current_user.role == 'admin':
        cursor.execute('SELECT * FROM requests ORDER BY created_time DESC')
    else:
        cursor.execute('SELECT * FROM requests WHERE user_id = ? ORDER BY created_time DESC', (current_user.id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    requests = []
    for row in rows:
        requests.append({
            'id': row[0],
            'user_id': row[1],
            'requester_name': row[2],
            'start_location': row[3],
            'end_location': row[4],
            'passengers': row[5],
            'request_time': row[6],
            'start_time': row[7],
            'end_time': row[8],
            'status': row[9]
        })
    
    return jsonify(requests)

@app.route('/api/requests/<request_id>', methods=['DELETE'])
@login_required
def delete_request(request_id):
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': get_text('success')})

# ==================== Vehicle Return API ====================

@app.route('/api/vehicles/<vehicle_id>/return', methods=['POST'])
@login_required
def verify_return(vehicle_id):
    """Confirm vehicle return"""
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    
    try:
        # Update vehicle status
        cursor.execute('''
            UPDATE vehicles 
            SET status = 'available', last_return_time = ?
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), vehicle_id))
        
        conn.commit()
        return jsonify({'success': True, 'message': get_text('success')})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

# ==================== Schedule API ====================

@app.route('/api/schedule', methods=['POST'])
@login_required
def run_schedule():
    """Run intelligent scheduling (optimized algorithm)"""
    try:
        from scheduler import optimize_schedule
        result = optimize_schedule()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/schedule/result')
@login_required
def get_schedule_result():
    """Get schedule result"""
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            s.vehicle_id,
            s.request_id,
            v.type as vehicle_type,
            v.capacity as vehicle_capacity,
            r.requester_name,
            r.start_location,
            r.end_location,
            r.passengers,
            r.request_time
        FROM schedules s
        JOIN vehicles v ON s.vehicle_id = v.id
        JOIN requests r ON s.request_id = r.id
        ORDER BY s.vehicle_id, s.request_id
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by vehicle
    result = {}
    for row in rows:
        vehicle_id = row[0]
        if vehicle_id not in result:
            result[vehicle_id] = {
                'vehicle_id': vehicle_id,
                'vehicle_type': row[2],
                'vehicle_capacity': row[3],
                'tasks': []
            }
        result[vehicle_id]['tasks'].append({
            'request_id': row[1],
            'requester': row[4],
            'start_location': row[5],
            'end_location': row[6],
            'passengers': row[7],
            'request_time': row[8]
        })
    
    return jsonify(list(result.values()))

@app.route('/api/schedule/reset', methods=['POST'])
@login_required
def reset_schedule():
    """Reset schedule"""
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    
    try:
        # Reset vehicle status
        cursor.execute("UPDATE vehicles SET status = 'available' WHERE status = 'in_use'")
        
        # Reset request status
        cursor.execute("UPDATE requests SET status = 'pending' WHERE status = 'assigned'")
        
        # Clear schedule
        cursor.execute('DELETE FROM schedules')
        
        conn.commit()
        return jsonify({'success': True, 'message': get_text('success')})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()

# ==================== User Management API ====================

@app.route('/api/users')
@login_required
def get_users():
    """Get all users (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, language FROM users ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'username': row[1],
            'role': row[2],
            'language': row[3]
        })
    
    return jsonify(users)

@app.route('/api/users/<int:user_id>/role', methods=['POST'])
@login_required
def update_user_role(user_id):
    """Update user role (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_role = data.get('role', 'user')
    
    if new_role not in ['admin', 'user']:
        return jsonify({'success': False, 'message': 'Invalid role'})
    
    # Cannot change own role
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot change own role'})
    
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': get_text('success')})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Cannot delete self
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Cannot delete yourself'})
    
    conn = sqlite3.connect(os.environ.get('DB_PATH', '/tmp/vehicle_scheduling.db'))
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': get_text('success')})

# ==================== Main Program ====================

if __name__ == '__main__':
    # Initialize database
    if not os.path.exists('vehicle_scheduling.db'):
        print("Database not found, please run: python database.py")
        exit(1)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
