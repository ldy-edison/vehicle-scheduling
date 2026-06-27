#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能调度算法 - 优化版本
支持：成本优化、时间窗口、车型匹配、多目标优化
"""

import sqlite3
from datetime import datetime
import math

def calculate_distance(loc1, loc2):
    """
    计算两地之间的距离（简化版）
    实际使用时可以接入 Google Maps API 或高德地图 API
    """
    # 这里使用模拟距离（实际应调用地图API）
    # 返回距离（公里）
    return 10  # 默认10公里

def optimize_schedule():
    """
    智能调度优化算法
    考虑因素：
    1. 成本优化（最少车辆、最短总路程）
    2. 时间窗口（用车时间的先后顺序）
    3. 车型匹配（优先使用最合适的车型）
    4. 多目标优化（平衡成本、时间、用户满意度）
    """
    conn = sqlite3.connect('vehicle_scheduling.db')
    cursor = conn.cursor()
    
    try:
        # 获取所有待分配申请（按优先级和时间排序）
        cursor.execute('''
            SELECT * FROM requests 
            WHERE status = 'pending' 
            ORDER BY 
                priority DESC,  -- 优先级高的先安排
                request_time ASC  -- 时间早的先安排
        ''')
        requests = cursor.fetchall()
        
        # 获取所有可用车辆（按容量排序）
        cursor.execute('''
            SELECT * FROM vehicles 
            WHERE status = 'available' 
            ORDER BY capacity ASC  -- 优先使用小车（节省大车）
        ''')
        vehicles = cursor.fetchall()
        
        if not requests or not vehicles:
            return {
                'success': False,
                'message': 'No pending requests or available vehicles'
            }
        
        # 调度结果
        schedule_result = []
        used_vehicles = set()
        
        # 第一阶段：精确匹配（容量刚好满足）
        for req in requests:
            if req[9] != 'pending':  # status
                continue
            
            req_id = req[0]
            passengers = req[5]
            start_loc = req[3]
            end_loc = req[4]
            request_time = req[6]
            
            # 寻找最合适的车辆
            best_vehicle = None
            best_score = float('inf')
            
            for veh in vehicles:
                veh_id = veh[0]
                veh_capacity = veh[2]
                veh_status = veh[3]
                
                if veh_status != 'available' or veh_id in used_vehicles:
                    continue
                
                # 容量必须 >= 乘客数
                if veh_capacity < passengers:
                    continue
                
                # 计算匹配分数（越低越好）
                # 分数 = 容量浪费率 + 距离成本 + 时间窗口惩罚
                capacity_waste = (veh_capacity - passengers) / veh_capacity
                
                # 这里可以加入实际距离计算
                # distance = calculate_distance(veh_last_location, start_loc)
                distance = 0  # 简化版
                
                # 时间窗口检查（如果有严格要求）
                time_penalty = 0
                # 这里可以加入时间窗口逻辑
                
                # 总分（权重可调整）
                score = capacity_waste * 0.5 + distance * 0.3 + time_penalty * 0.2
                
                if score < best_score:
                    best_score = score
                    best_vehicle = veh
            
            # 找到最优车辆
            if best_vehicle:
                schedule_result.append({
                    'vehicle_id': best_vehicle[0],
                    'request_id': req_id,
                    'score': best_score
                })
                used_vehicles.add(best_vehicle[0])
        
        # 第二阶段：优化调整（减少车辆使用数量）
        # 尝试合并同方向的申请
        optimized_result = optimize_merge_trips(schedule_result, requests, vehicles)
        
        # 保存调度结果
        cursor.execute('DELETE FROM schedules')
        
        for item in optimized_result:
            cursor.execute('''
                INSERT INTO schedules (vehicle_id, request_id, status, priority, cost_estimate)
                VALUES (?, ?, 'assigned', 1, ?)
            ''', (item['vehicle_id'], item['request_id'], item.get('cost', 0)))
            
            # 更新申请状态
            cursor.execute('''
                UPDATE requests 
                SET status = 'assigned' 
                WHERE id = ?
            ''', (item['request_id'],))
            
            # 更新车辆状态
            cursor.execute('''
                UPDATE vehicles 
                SET status = 'in_use' 
                WHERE id = ?
            ''', (item['vehicle_id'],))
        
        conn.commit()
        
        return {
            'success': True,
            'message': f'Schedule completed! Assigned {len(optimized_result)} requests to {len(set([r["vehicle_id"] for r in optimized_result]))} vehicles'
        }
        
    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'message': str(e)
        }
    finally:
        conn.close()

def optimize_merge_trips(schedule_result, requests, vehicles):
    """
    优化合并行程（减少车辆使用）
    尝试将同方向的申请合并到同一辆车
    """
    # 按车辆分组
    vehicle_tasks = {}
    for item in schedule_result:
        veh_id = item['vehicle_id']
        if veh_id not in vehicle_tasks:
            vehicle_tasks[veh_id] = []
        vehicle_tasks[veh_id].append(item)
    
    # 尝试合并
    optimized = []
    merged_vehicles = set()
    
    for veh_id, tasks in vehicle_tasks.items():
        if veh_id in merged_vehicles:
            continue
        
        # 检查是否可以合并其他车辆的行程
        total_passengers = sum([
            next((r[5] for r in requests if r[0] == t['request_id']), 0)
            for t in tasks
        ])
        
        # 获取车辆容量
        veh_capacity = next((v[2] for v in vehicles if v[0] == veh_id), 0)
        
        # 如果还有容量，尝试合并其他行程
        if total_passengers < veh_capacity:
            for other_veh_id, other_tasks in vehicle_tasks.items():
                if other_veh_id == veh_id or other_veh_id in merged_vehicles:
                    continue
                
                # 检查是否可以合并
                other_passengers = sum([
                    next((r[5] for r in requests if r[0] == t['request_id']), 0)
                    for t in other_tasks
                ])
                
                if total_passengers + other_passengers <= veh_capacity:
                    # 可以合并
                    tasks.extend(other_tasks)
                    merged_vehicles.add(other_veh_id)
                    total_passengers += other_passengers
        
        optimized.extend(tasks)
    
    return optimized

def calculate_cost(vehicle_id, request_ids):
    """
    计算总成本（燃料、司机、维护等）
    """
    # 简化版：按距离计算
    total_cost = 0
    
    conn = sqlite3.connect('vehicle_scheduling.db')
    cursor = conn.cursor()
    
    for req_id in request_ids:
        cursor.execute('SELECT start_location, end_location FROM requests WHERE id = ?', (req_id,))
        row = cursor.fetchone()
        if row:
            # 这里应该调用地图API计算实际距离
            distance = 10  # 默认10公里
            cost_per_km = 2  # 每公里成本（燃料+司机+维护）
            total_cost += distance * cost_per_km
    
    conn.close()
    
    return total_cost

def check_time_window(request_time, vehicle_id):
    """
    检查时间窗口（车辆是否能在指定时间到达）
    """
    # 简化版：假设车辆随时可用
    return True

if __name__ == '__main__':
    result = optimize_schedule()
    print(result)
