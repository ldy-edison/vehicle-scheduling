#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化示例数据
"""

import database
import time

def init_sample_data():
    """创建示例车辆和申请"""
    
    print("开始初始化示例数据...")
    print("="*50)
    
    # ===== 1. 添加示例车辆 =====
    print("\n[1/2] 添加示例车辆...")
    
    vehicles = [
        ('粤A00001', '轿车', 5),
        ('粤A00002', 'SUV', 7),
        ('粤A00003', '商务车', 12),
        ('粤A00004', '大巴', 45),
        ('粤A00005', '货车', 2),
    ]
    
    for vid, vtype, cap in vehicles:
        result = database.add_vehicle(vid, vtype, cap, '可用')
        if result['success']:
            print(f"  ✓ {vid} ({vtype}, {cap}座)")
        else:
            print(f"  - {vid} 已存在，跳过")
    
    print(f"\n✓ 车辆添加完成！")
    
    # 等待一下，避免数据库锁定
    time.sleep(0.5)
    
    # ===== 2. 添加示例申请 =====
    print("\n[2/2] 添加示例用车申请...")
    
    requests = [
        ('张三', '公司总部', '白云机场T1', 3, '2026-06-28 09:00', '需要提前到达'),
        ('李四', '公司总部', '广州南站', 2, '2026-06-28 10:30', ''),
        ('王五', '公司总部', '客户公司A', 8, '2026-06-28 14:00', '带样品'),
        ('赵六', '公司总部', '广州东站', 12, '2026-06-28 08:00', '团队出行'),
        ('孙七', '公司总部', '琶洲会展中心', 4, '2026-06-28 09:30', ''),
        ('周八', '公司总部', '白云机场T2', 2, '2026-06-28 15:00', '国际航班'),
        ('吴九', '公司总部', '大学城', 35, '2026-06-28 13:00', '校园招聘'),
        ('郑十', '公司总部', '天河体育中心', 6, '2026-06-28 18:00', '参加活动'),
        ('钱一一', '公司总部', '南沙港', 1, '2026-06-28 07:30', '紧急货物'),
        ('陈十二', '公司总部', '佛山分公司', 10, '2026-06-28 11:00', '会议'),
    ]
    
    for req in requests:
        result = database.add_request(
            requester=req[0],
            start_location=req[1],
            end_location=req[2],
            passengers=req[3],
            request_time=req[4],
            notes=req[5]
        )
        if result['success']:
            print(f"  ✓ {req[0]}: {req[1]} → {req[2]} ({req[3]}人)")
        else:
            print(f"  ✗ {req[0]}: 添加失败")
    
    print(f"\n✓ 用车申请添加完成！")
    
    # ===== 3. 显示统计 =====
    print("\n" + "="*50)
    print("示例数据初始化完成！")
    print("="*50)
    
    vehicles = database.get_all_vehicles()
    requests = database.get_all_requests()
    
    print(f"\n📊 当前数据：")
    print(f"  - 车辆总数：{len(vehicles)} 辆")
    print(f"  - 用车申请：{len(requests)} 个")
    print(f"  - 待分配：{len([r for r in requests if r['status']=='待分配'])} 个")
    
    print(f"\n=> 下一步：")
    print(f"  1. 刷新浏览器页面（或访问 http://127.0.0.1:5000）")
    print(f"  2. 进入'智能调度'页面")
    print(f"  3. 点击'开始自动调度'按钮")
    print(f"  4. 查看调度结果！")

if __name__ == '__main__':
    # 先初始化数据库
    database.init_db()
    
    # 添加示例数据
    init_sample_data()
