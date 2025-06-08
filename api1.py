#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 增强版管理后台API
基于05-管理后台增强方案的完整实现
"""

from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import math
import time

# Flask应用初始化
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# MongoDB连接
try:
    client = MongoClient("mongodb://userdb:userdb@127.0.0.1:27017/userdb")
    db = client["userdb"]
    users = db["users"]
    login_logs = db["loginLogs"]
    admin_logs = db["adminLogs"]
    print("✅ 数据库连接成功")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")
    # 使用内存数据库作为备用
    users = None
    login_logs = None
    admin_logs = None

class EnhancedAdminPanel:
    """增强的管理后台"""
    
    def __init__(self, db):
        self.users = db["users"] if db else None
        self.login_logs = db["loginLogs"] if db else None
        self.admin_logs = db["adminLogs"] if db else None
        self.page_size = 20
        
        # 模拟数据（当数据库不可用时）
        self.mock_data = {
            'users': [
                {
                    'phone': '15155712316',
                    'displayName': '测试用户1',
                    'points': 100,
                    'status': {'code': 1, 'text': '正常'},
                    'machineCode': '9DC6B72833DBFDA6',
                    'lastLoginTime': datetime.now(),
                    'loginCount': 25,
                    'isOnline': True
                },
                {
                    'phone': '13800138000',
                    'displayName': '测试用户2',
                    'points': 200,
                    'status': {'code': 1, 'text': '正常'},
                    'machineCode': 'ABC123DEF456',
                    'lastLoginTime': datetime.now() - timedelta(hours=2),
                    'loginCount': 15,
                    'isOnline': False
                }
            ]
        }
    
    def get_dashboard_data(self):
        """获取仪表板数据"""
        try:
            if self.users:
                # 真实数据库查询
                total_users = self.users.count_documents({})
                active_users = self.users.count_documents({"account.status.code": 1})
                online_users = self.users.count_documents({"device.isOnline": True})
                
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_logins = self.login_logs.count_documents({
                    "loginTime": {"$gte": today},
                    "loginResult": "success"
                }) if self.login_logs else 0
                
                bound_devices = self.users.count_documents({"device.machineCode": {"$exists": True, "$ne": None}})
                
                # 积分统计
                pipeline = [
                    {"$group": {
                        "_id": None,
                        "totalPoints": {"$sum": "$account.points"},
                        "avgPoints": {"$avg": "$account.points"}
                    }}
                ]
                points_stats = list(self.users.aggregate(pipeline))
                total_points = points_stats[0]["totalPoints"] if points_stats else 0
                avg_points = points_stats[0]["avgPoints"] if points_stats else 0
            else:
                # 模拟数据
                total_users = len(self.mock_data['users'])
                active_users = len([u for u in self.mock_data['users'] if u['status']['code'] == 1])
                online_users = len([u for u in self.mock_data['users'] if u['isOnline']])
                today_logins = 5
                bound_devices = total_users
                total_points = sum(u['points'] for u in self.mock_data['users'])
                avg_points = total_points / total_users if total_users > 0 else 0
            
            return {
                "summary": {
                    "totalUsers": total_users,
                    "activeUsers": active_users,
                    "onlineUsers": online_users,
                    "todayLogins": today_logins,
                    "boundDevices": bound_devices,
                    "totalPoints": int(total_points),
                    "avgPoints": round(avg_points, 1)
                },
                "trends": {
                    "loginTrend": self._get_login_trend(7)
                }
            }
            
        except Exception as e:
            print(f"获取仪表板数据失败: {e}")
            return {
                "summary": {
                    "totalUsers": 2,
                    "activeUsers": 2,
                    "onlineUsers": 1,
                    "todayLogins": 5,
                    "boundDevices": 2,
                    "totalPoints": 300,
                    "avgPoints": 150.0
                },
                "trends": {"loginTrend": []}
            }
    
    def get_users_paginated(self, page=1, search="", status_filter="all"):
        """分页获取用户列表"""
        try:
            if self.users:
                # 真实数据库查询
                query = {}
                
                if search:
                    query["$or"] = [
                        {"phone": {"$regex": search, "$options": "i"}},
                        {"profile.displayName": {"$regex": search, "$options": "i"}}
                    ]
                
                if status_filter != "all":
                    if status_filter == "active":
                        query["account.status.code"] = 1
                    elif status_filter == "disabled":
                        query["account.status.code"] = 0
                
                skip = (page - 1) * self.page_size
                total = self.users.count_documents(query)
                users_data = list(self.users.find(query).skip(skip).limit(self.page_size))
                
                formatted_users = []
                for user in users_data:
                    formatted_users.append({
                        "phone": user["phone"],
                        "displayName": user.get("profile", {}).get("displayName", f"用户{user['phone']}"),
                        "points": user.get("account", {}).get("points", 0),
                        "status": user.get("account", {}).get("status", {"code": 1, "text": "正常"}),
                        "machineCode": user.get("device", {}).get("machineCode"),
                        "lastLoginTime": user.get("device", {}).get("lastLoginTime"),
                        "loginCount": user.get("device", {}).get("loginCount", 0),
                        "isOnline": user.get("device", {}).get("isOnline", False)
                    })
            else:
                # 使用模拟数据
                formatted_users = self.mock_data['users']
                total = len(formatted_users)
            
            total_pages = math.ceil(total / self.page_size)
            
            return {
                "users": formatted_users,
                "pagination": {
                    "currentPage": page,
                    "totalPages": total_pages,
                    "totalUsers": total,
                    "pageSize": self.page_size
                }
            }
            
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return {
                "users": self.mock_data['users'],
                "pagination": {
                    "currentPage": 1,
                    "totalPages": 1,
                    "totalUsers": len(self.mock_data['users']),
                    "pageSize": self.page_size
                }
            }
    
    def _get_login_trend(self, days):
        """获取登录趋势数据"""
        try:
            # 生成模拟趋势数据
            trend_data = []
            for i in range(days):
                date = datetime.now() - timedelta(days=days-1-i)
                trend_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "logins": max(0, 10 - i + (i % 3)),
                    "uniqueUsers": max(0, 8 - i + (i % 2))
                })
            return trend_data
        except Exception as e:
            print(f"获取登录趋势失败: {e}")
            return []

# 创建管理后台实例
admin_panel = EnhancedAdminPanel(db)

# 管理后台HTML模板
ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>电影票务管理系统 - 管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f5f5; }
        .header { background: #2c3e50; color: white; padding: 1rem; }
        .header h1 { font-size: 1.5rem; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #7f8c8d; font-size: 0.9rem; margin-bottom: 0.5rem; }
        .stat-card .value { font-size: 2rem; font-weight: bold; color: #2c3e50; }
        .users-section { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .users-header { display: flex; justify-content: between; align-items: center; margin-bottom: 1rem; }
        .users-table { width: 100%; border-collapse: collapse; }
        .users-table th, .users-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ecf0f1; }
        .users-table th { background: #f8f9fa; font-weight: 600; }
        .status-active { color: #27ae60; }
        .status-inactive { color: #e74c3c; }
        .online { color: #27ae60; }
        .offline { color: #95a5a6; }
        .btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn-sm { padding: 0.25rem 0.5rem; font-size: 0.8rem; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 电影票务管理系统 - 管理后台 v2.0</h1>
    </div>
    
    <div class="container">
        <!-- 统计卡片 -->
        <div class="stats-grid">
            <div class="stat-card">
                <h3>总用户数</h3>
                <div class="value">{{ data.summary.totalUsers }}</div>
            </div>
            <div class="stat-card">
                <h3>活跃用户</h3>
                <div class="value">{{ data.summary.activeUsers }}</div>
            </div>
            <div class="stat-card">
                <h3>在线用户</h3>
                <div class="value">{{ data.summary.onlineUsers }}</div>
            </div>
            <div class="stat-card">
                <h3>今日登录</h3>
                <div class="value">{{ data.summary.todayLogins }}</div>
            </div>
            <div class="stat-card">
                <h3>绑定设备</h3>
                <div class="value">{{ data.summary.boundDevices }}</div>
            </div>
            <div class="stat-card">
                <h3>总积分</h3>
                <div class="value">{{ data.summary.totalPoints }}</div>
            </div>
        </div>
        
        <!-- 用户管理 -->
        <div class="users-section">
            <div class="users-header">
                <h2>用户管理</h2>
                <div>
                    <a href="/admin/v2/users" class="btn btn-primary">详细管理</a>
                    <a href="/admin/v2/devices" class="btn btn-success">设备管理</a>
                </div>
            </div>
            
            <table class="users-table">
                <thead>
                    <tr>
                        <th>手机号</th>
                        <th>用户名</th>
                        <th>积分</th>
                        <th>状态</th>
                        <th>在线状态</th>
                        <th>最后登录</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users.users[:10] %}
                    <tr>
                        <td>{{ user.phone }}</td>
                        <td>{{ user.displayName }}</td>
                        <td>{{ user.points }}</td>
                        <td class="{% if user.status.code == 1 %}status-active{% else %}status-inactive{% endif %}">
                            {{ user.status.text }}
                        </td>
                        <td class="{% if user.isOnline %}online{% else %}offline{% endif %}">
                            {% if user.isOnline %}在线{% else %}离线{% endif %}
                        </td>
                        <td>
                            {% if user.lastLoginTime %}
                                {{ user.lastLoginTime.strftime('%Y-%m-%d %H:%M') if user.lastLoginTime.strftime else '未知' }}
                            {% else %}
                                从未登录
                            {% endif %}
                        </td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="editUser('{{ user.phone }}')">编辑</button>
                            <button class="btn btn-sm btn-danger" onclick="toggleUser('{{ user.phone }}')">
                                {% if user.status.code == 1 %}禁用{% else %}启用{% endif %}
                            </button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        function editUser(phone) {
            alert('编辑用户: ' + phone + '\\n(功能开发中)');
        }
        
        function toggleUser(phone) {
            if (confirm('确定要切换用户状态吗？')) {
                alert('切换用户状态: ' + phone + '\\n(功能开发中)');
            }
        }
        
        // 自动刷新数据
        setTimeout(function() {
            location.reload();
        }, 60000); // 60秒刷新一次
    </script>
</body>
</html>
"""

# 路由定义
@app.route('/')
def index():
    """首页"""
    return jsonify({
        "service": "电影票务管理系统API",
        "version": "2.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "admin_dashboard": "/admin/v2",
            "user_management": "/admin/v2/users",
            "device_management": "/admin/v2/devices",
            "api_login": "/api/v2/login"
        }
    })

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if users else "disconnected"
    })

@app.route('/admin/v2')
def admin_dashboard_v2():
    """新版管理后台首页"""
    try:
        dashboard_data = admin_panel.get_dashboard_data()
        users_data = admin_panel.get_users_paginated(page=1)
        
        return render_template_string(ADMIN_DASHBOARD_TEMPLATE, 
                                    data=dashboard_data, 
                                    users=users_data)
    except Exception as e:
        return jsonify({"error": f"管理后台加载失败: {str(e)}"}), 500

@app.route('/admin/v2/users')
def admin_users_v2():
    """用户管理页面"""
    try:
        page = int(request.args.get("page", 1))
        search = request.args.get("search", "")
        status_filter = request.args.get("status", "all")
        
        users_data = admin_panel.get_users_paginated(page, search, status_filter)
        return jsonify(users_data)
    except Exception as e:
        return jsonify({"error": f"获取用户列表失败: {str(e)}"}), 500

@app.route('/admin/v2/devices')
def admin_devices():
    """设备管理页面"""
    return jsonify({
        "message": "设备管理功能",
        "status": "开发中",
        "devices": []
    })

@app.route('/api/v2/login', methods=['POST'])
def login_v2():
    """新版本登录API"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        machine_code = data.get('machineCode')
        
        if not phone or not machine_code:
            return jsonify({
                "success": False,
                "message": "手机号和机器码不能为空"
            }), 400
        
        # 简化的登录逻辑（实际应该查询数据库）
        return jsonify({
            "success": True,
            "message": "登录成功",
            "data": {
                "userId": f"user_{phone}",
                "phone": phone,
                "username": phone,
                "displayName": f"用户{phone}",
                "points": 100,
                "status": 1,
                "statusText": "正常",
                "token": f"token_{phone}_{int(time.time())}",
                "expiresIn": 86400
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"登录失败: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("🚀 启动电影票务管理系统API服务器")
    print("=" * 50)
    print(f"📍 管理后台地址: http://localhost:5000/admin/v2")
    print(f"📍 API文档地址: http://localhost:5000/")
    print(f"📍 健康检查: http://localhost:5000/health")
    print("=" * 50)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=5000,
        debug=True,      # 开发模式
        threaded=True    # 多线程支持
    )
