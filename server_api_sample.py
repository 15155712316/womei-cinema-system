#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐影系统API服务器示例
提供用户认证、机器码管理等API功能

注意：这是一个示例代码，展示如何为您的API服务器 (http://43.142.19.28:5000) 添加机器码更新功能
您需要将这些端点集成到您现有的Flask服务器中
"""

from flask import Flask, request, jsonify, render_template_string
import json
import time
import hashlib
from datetime import datetime

app = Flask(__name__)

# 模拟数据库（实际应该使用真实数据库）
users_db = {
    "15155712316": {
        "id": "user001",
        "phone": "15155712316",
        "machineCode": "7DA491096E7B6854",
        "status": 1,  # 1=启用, 0=禁用
        "points": 800,
        "createTime": "2025-05-28 23:02"
    }
}

# 管理后台HTML模板（增强版）
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>账号积分管理系统 v1.1</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .add-user { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .add-user input, .add-user select { margin: 5px; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 2px; }
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .btn-danger { background: #dc3545; color: white; }
        .btn:hover { opacity: 0.8; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: center; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .status-enabled { color: #28a745; font-weight: bold; }
        .status-disabled { color: #dc3545; font-weight: bold; }
        .machine-code { font-family: 'Courier New', monospace; font-size: 12px; }
        .machine-code-input { font-family: 'Courier New', monospace; width: 150px; }
        .loading { display: none; color: #007bff; }
        .message { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 账号积分管理系统 v1.1</h1>
        
        <div id="message"></div>
        
        <div class="add-user">
            <h3>➕ 添加新用户</h3>
            <input type="text" id="new-phone" placeholder="手机号" maxlength="11">
            <input type="text" id="new-machine-code" placeholder="机器码" maxlength="16" class="machine-code-input">
            <input type="number" id="new-points" placeholder="积分" min="0" value="0">
            <select id="new-status">
                <option value="1">启用</option>
                <option value="0">禁用</option>
            </select>
            <button class="btn btn-primary" onclick="addUser()">添加用户</button>
        </div>
        
        <h3>👥 用户列表 (共 <span id="user-count">{{ users|length }}</span> 个用户)</h3>
        
        <table id="users-table">
            <thead>
                <tr>
                    <th>手机号</th>
                    <th>积分</th>
                    <th>状态</th>
                    <th>机器码</th>
                    <th>创建时间</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                {% for phone, user in users.items() %}
                <tr id="user-{{ phone }}">
                    <td>{{ phone }}</td>
                    <td>
                        <input type="number" value="{{ user.points }}" min="0" 
                               onchange="updatePoints('{{ phone }}', this.value)" 
                               style="width: 80px; text-align: center;">
                    </td>
                    <td>
                        <span class="{% if user.status == 1 %}status-enabled{% else %}status-disabled{% endif %}">
                            {% if user.status == 1 %}启用{% else %}禁用{% endif %}
                        </span>
                    </td>
                    <td>
                        <input type="text" value="{{ user.machineCode }}" 
                               class="machine-code-input" maxlength="16"
                               onchange="updateMachineCode('{{ phone }}', this.value)">
                    </td>
                    <td>{{ user.createTime }}</td>
                    <td>
                        <button class="btn btn-warning" onclick="toggleStatus('{{ phone }}')">
                            {% if user.status == 1 %}禁用{% else %}启用{% endif %}
                        </button>
                        <button class="btn btn-danger" onclick="deleteUser('{{ phone }}')">删除</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="loading" id="loading">正在处理请求...</div>
    </div>

    <script>
        function showMessage(text, type = 'success') {
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = `<div class="message ${type}">${text}</div>`;
            setTimeout(() => messageDiv.innerHTML = '', 3000);
        }
        
        function showLoading(show = true) {
            document.getElementById('loading').style.display = show ? 'block' : 'none';
        }
        
        async function updateMachineCode(phone, newMachineCode) {
            if (newMachineCode.length !== 16) {
                showMessage('机器码长度必须为16位', 'error');
                location.reload();
                return;
            }
            
            showLoading(true);
            try {
                const response = await fetch('/update_machine_code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: phone,
                        machineCode: newMachineCode,
                        timestamp: Math.floor(Date.now() / 1000)
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(`用户 ${phone} 的机器码已更新为: ${newMachineCode}`);
                } else {
                    showMessage(result.message, 'error');
                    location.reload();
                }
            } catch (error) {
                showMessage('更新机器码失败: ' + error.message, 'error');
                location.reload();
            } finally {
                showLoading(false);
            }
        }
        
        async function updatePoints(phone, newPoints) {
            showLoading(true);
            try {
                const response = await fetch('/update_user_points', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: phone,
                        points: parseInt(newPoints),
                        timestamp: Math.floor(Date.now() / 1000)
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(`用户 ${phone} 的积分已更新为: ${newPoints}`);
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('更新积分失败: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }
        
        async function toggleStatus(phone) {
            if (!confirm(`确定要切换用户 ${phone} 的状态吗？`)) return;
            
            showLoading(true);
            try {
                const response = await fetch('/toggle_user_status', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: phone,
                        timestamp: Math.floor(Date.now() / 1000)
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(result.message);
                    location.reload();
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('更新状态失败: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }
        
        async function deleteUser(phone) {
            if (!confirm(`确定要删除用户 ${phone} 吗？此操作不可恢复！`)) return;
            
            showLoading(true);
            try {
                const response = await fetch('/delete_user', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: phone,
                        timestamp: Math.floor(Date.now() / 1000)
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(result.message);
                    document.getElementById(`user-${phone}`).remove();
                    updateUserCount();
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('删除用户失败: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }
        
        async function addUser() {
            const phone = document.getElementById('new-phone').value.trim();
            const machineCode = document.getElementById('new-machine-code').value.trim();
            const points = parseInt(document.getElementById('new-points').value) || 0;
            const status = parseInt(document.getElementById('new-status').value);
            
            if (!phone || phone.length !== 11) {
                showMessage('请输入11位手机号', 'error');
                return;
            }
            
            if (!machineCode || machineCode.length !== 16) {
                showMessage('请输入16位机器码', 'error');
                return;
            }
            
            showLoading(true);
            try {
                const response = await fetch('/add_user', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: phone,
                        machineCode: machineCode,
                        points: points,
                        status: status,
                        timestamp: Math.floor(Date.now() / 1000)
                    })
                });
                
                const result = await response.json();
                if (result.success) {
                    showMessage(`用户 ${phone} 添加成功`);
                    location.reload();
                } else {
                    showMessage(result.message, 'error');
                }
            } catch (error) {
                showMessage('添加用户失败: ' + error.message, 'error');
            } finally {
                showLoading(false);
            }
        }
        
        function updateUserCount() {
            const count = document.querySelectorAll('#users-table tbody tr').length;
            document.getElementById('user-count').textContent = count;
        }
    </script>
</body>
</html>
"""

@app.route('/admin')
def admin_panel():
    """管理后台界面"""
    return render_template_string(ADMIN_TEMPLATE, users=users_db)

@app.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        machine_code = data.get('machineCode')
        
        print(f"[登录请求] 手机号: {phone}, 机器码: {machine_code}")
        
        # 查找用户
        user = users_db.get(phone)
        if not user:
            return jsonify({
                "success": False,
                "message": "手机号未注册，请联系管理员"
            })
        
        # 验证机器码
        if user["machineCode"] != machine_code:
            return jsonify({
                "success": False,
                "message": "设备未授权，请联系管理员绑定设备"
            })
        
        # 验证账号状态
        if user["status"] != 1:
            return jsonify({
                "success": False,
                "message": "账号已被禁用，请联系管理员"
            })
        
        # 生成token
        token = hashlib.md5(f"{phone}{machine_code}{time.time()}".encode()).hexdigest()
        
        return jsonify({
            "success": True,
            "message": "登录成功",
            "data": {
                "id": user["id"],
                "phone": user["phone"],
                "status": user["status"],
                "points": user["points"],
                "token": token
            }
        })
        
    except Exception as e:
        print(f"[登录错误] {e}")
        return jsonify({
            "success": False,
            "message": f"登录异常: {str(e)}"
        })

@app.route('/update_machine_code', methods=['POST'])
def update_machine_code():
    """更新用户机器码"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        new_machine_code = data.get('machineCode')
        
        print(f"[机器码更新] 手机号: {phone}, 新机器码: {new_machine_code}")
        
        # 验证参数
        if not phone or not new_machine_code:
            return jsonify({
                "success": False,
                "message": "手机号和机器码不能为空"
            })
        
        if len(new_machine_code) != 16:
            return jsonify({
                "success": False,
                "message": "机器码长度必须为16位"
            })
        
        # 查找用户
        if phone not in users_db:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            })
        
        # 更新机器码
        users_db[phone]["machineCode"] = new_machine_code
        
        print(f"[机器码更新] 用户 {phone} 的机器码已更新为: {new_machine_code}")
        
        return jsonify({
            "success": True,
            "message": f"机器码更新成功",
            "data": {
                "phone": phone,
                "machineCode": new_machine_code
            }
        })
        
    except Exception as e:
        print(f"[机器码更新错误] {e}")
        return jsonify({
            "success": False,
            "message": f"更新异常: {str(e)}"
        })

@app.route('/update_user_points', methods=['POST'])
def update_user_points():
    """更新用户积分"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        new_points = data.get('points')
        
        print(f"[积分更新] 手机号: {phone}, 新积分: {new_points}")
        
        # 验证参数
        if not phone or new_points is None:
            return jsonify({
                "success": False,
                "message": "手机号和积分不能为空"
            })
        
        if new_points < 0:
            return jsonify({
                "success": False,
                "message": "积分不能为负数"
            })
        
        # 查找用户
        if phone not in users_db:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            })
        
        # 更新积分
        users_db[phone]["points"] = new_points
        
        print(f"[积分更新] 用户 {phone} 的积分已更新为: {new_points}")
        
        return jsonify({
            "success": True,
            "message": f"积分更新成功",
            "data": {
                "phone": phone,
                "points": new_points
            }
        })
        
    except Exception as e:
        print(f"[积分更新错误] {e}")
        return jsonify({
            "success": False,
            "message": f"更新异常: {str(e)}"
        })

@app.route('/toggle_user_status', methods=['POST'])
def toggle_user_status():
    """切换用户状态"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        print(f"[状态切换] 手机号: {phone}")
        
        # 查找用户
        if phone not in users_db:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            })
        
        # 切换状态
        current_status = users_db[phone]["status"]
        new_status = 0 if current_status == 1 else 1
        users_db[phone]["status"] = new_status
        
        status_text = "启用" if new_status == 1 else "禁用"
        print(f"[状态切换] 用户 {phone} 的状态已更新为: {status_text}")
        
        return jsonify({
            "success": True,
            "message": f"用户状态已切换为{status_text}",
            "data": {
                "phone": phone,
                "status": new_status
            }
        })
        
    except Exception as e:
        print(f"[状态切换错误] {e}")
        return jsonify({
            "success": False,
            "message": f"切换异常: {str(e)}"
        })

@app.route('/add_user', methods=['POST'])
def add_user():
    """添加新用户"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        machine_code = data.get('machineCode')
        points = data.get('points', 0)
        status = data.get('status', 1)
        
        print(f"[添加用户] 手机号: {phone}, 机器码: {machine_code}")
        
        # 验证参数
        if not phone or not machine_code:
            return jsonify({
                "success": False,
                "message": "手机号和机器码不能为空"
            })
        
        if len(phone) != 11:
            return jsonify({
                "success": False,
                "message": "手机号长度必须为11位"
            })
        
        if len(machine_code) != 16:
            return jsonify({
                "success": False,
                "message": "机器码长度必须为16位"
            })
        
        # 检查是否已存在
        if phone in users_db:
            return jsonify({
                "success": False,
                "message": "用户已存在"
            })
        
        # 添加用户
        users_db[phone] = {
            "id": f"user{len(users_db) + 1:03d}",
            "phone": phone,
            "machineCode": machine_code,
            "status": status,
            "points": points,
            "createTime": datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        print(f"[添加用户] 用户 {phone} 添加成功")
        
        return jsonify({
            "success": True,
            "message": f"用户添加成功",
            "data": {
                "phone": phone,
                "machineCode": machine_code,
                "points": points,
                "status": status
            }
        })
        
    except Exception as e:
        print(f"[添加用户错误] {e}")
        return jsonify({
            "success": False,
            "message": f"添加异常: {str(e)}"
        })

@app.route('/delete_user', methods=['POST'])
def delete_user():
    """删除用户"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        print(f"[删除用户] 手机号: {phone}")
        
        # 查找用户
        if phone not in users_db:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            })
        
        # 删除用户
        del users_db[phone]
        
        print(f"[删除用户] 用户 {phone} 删除成功")
        
        return jsonify({
            "success": True,
            "message": f"用户删除成功",
            "data": {
                "phone": phone
            }
        })
        
    except Exception as e:
        print(f"[删除用户错误] {e}")
        return jsonify({
            "success": False,
            "message": f"删除异常: {str(e)}"
        })

@app.route('/')
def index():
    """首页重定向到管理界面"""
    return f'<h1>乐影系统API服务器</h1><p><a href="/admin">进入管理后台</a></p>'

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 乐影系统API服务器启动")
    print("📱 管理后台: http://127.0.0.1:5000/admin")
    print("🔐 API端点:")
    print("   - POST /login - 用户登录")
    print("   - POST /update_machine_code - 更新机器码")
    print("   - POST /update_user_points - 更新积分")
    print("   - POST /toggle_user_status - 切换状态")
    print("   - POST /add_user - 添加用户")
    print("   - POST /delete_user - 删除用户")
    print("=" * 60)
    
    # 开发模式启动（生产环境请使用gunicorn等WSGI服务器）
    app.run(host='0.0.0.0', port=5000, debug=True) 