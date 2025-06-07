#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐影系统 - 完整的线上API服务器代码
包含所有机器码管理功能
版本: 1.2
"""

from flask import Flask, request, jsonify, render_template_string
from pymongo import MongoClient
from datetime import datetime
import traceback

app = Flask(__name__)
client = MongoClient("mongodb://userdb:userdb@127.0.0.1:27017/userdb")
db = client["userdb"]
users = db["users"]

# 测试数据库连接
try:
    count = users.count_documents({})
    print(f"✅ 数据库连接成功! 当前用户数: {count}")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")

# ==========================================
# 基础路由
# ==========================================

@app.route("/")
def home():
    return jsonify({
        "service": "乐影系统API服务器",
        "status": "运行中",
        "version": "1.2",
        "features": "完整机器码管理功能",
        "endpoints": [
            "/login",
            "/set_points", 
            "/set_status",
            "/update_machine_code",
            "/update_user_points", 
            "/toggle_user_status",
            "/admin"
        ]
    })

@app.route("/health")
def health():
    try:
        users.count_documents({})
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        print(f"健康检查错误: {e}")
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500

# ==========================================
# 用户认证和登录
# ==========================================

@app.route("/login", methods=["POST"])
def login():
    try:
        print(f"收到登录请求")
        
        if not request.json:
            return jsonify({"success": False, "message": "Invalid JSON data"}), 400
        
        data = request.json
        phone = data.get("phone")
        machine_code = data.get("machineCode")
        
        print(f"登录参数: phone={phone}, machineCode={machine_code}")
        
        if not phone or not machine_code:
            return jsonify({"success": False, "message": "Missing phone or machineCode"}), 400
        
        # 查找用户
        try:
            user = users.find_one({"phone": phone})
            print(f"数据库查询结果: {user}")
        except Exception as e:
            print(f"数据库查询错误: {e}")
            return jsonify({"success": False, "message": "Database query error"}), 500
        
        if not user:
            return jsonify({"success": False, "message": "Not registered"}), 403
        
        # 检查机器码
        user_machine_code = user.get("machineCode")
        print(f"用户机器码: {user_machine_code}")
        
        if not user_machine_code:
            # 用户没有绑定机器码，进行绑定
            try:
                result = users.update_one(
                    {"phone": phone}, 
                    {"$set": {"machineCode": machine_code}}
                )
                print(f"机器码绑定结果: {result.modified_count}")
                user["machineCode"] = machine_code
            except Exception as e:
                print(f"机器码绑定错误: {e}")
                return jsonify({"success": False, "message": "Failed to bind device"}), 500
        elif user_machine_code != machine_code:
            return jsonify({"success": False, "message": "Device not authorized"}), 403
        
        # 检查账号状态
        if user.get("status", 1) != 1:
            return jsonify({"success": False, "message": "Account disabled"}), 403
        
        # 登录成功
        result_data = {
            "phone": user.get("phone"),
            "points": user.get("points", 0),
            "status": user.get("status", 1),
            "machineCode": user.get("machineCode"),
            "created_at": user.get("created_at")
        }
        
        print(f"登录成功: {result_data}")
        return jsonify({"success": True, "message": "Login success", "data": result_data})
        
    except Exception as e:
        print(f"登录接口异常: {e}")
        print(f"异常详情: {traceback.format_exc()}")
        return jsonify({"success": False, "message": "Internal server error", "error": str(e)}), 500

# ==========================================
# ⭐ 新增：机器码管理功能（测试失败的功能）
# ==========================================

@app.route('/update_machine_code', methods=['POST'])
def update_machine_code():
    """更新用户机器码"""
    try:
        print("收到更新机器码请求")
        
        data = request.get_json()
        phone = data.get('phone')
        new_machine_code = data.get('machineCode')
        
        print(f"更新机器码参数: phone={phone}, machineCode={new_machine_code}")
        
        if not phone or not new_machine_code:
            return jsonify({
                "success": False,
                "message": "手机号和机器码不能为空"
            }), 400
        
        # 查找用户是否存在
        user = users.find_one({"phone": phone})
        if not user:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404
        
        # 更新机器码
        result = users.update_one(
            {"phone": phone}, 
            {"$set": {"machineCode": new_machine_code, "updated_at": datetime.now()}}
        )
        
        if result.modified_count > 0:
            print(f"机器码更新成功: {phone} -> {new_machine_code}")
            return jsonify({
                "success": True,
                "message": "机器码更新成功",
                "data": {
                    "phone": phone,
                    "machineCode": new_machine_code,
                    "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "机器码更新失败"
            }), 500
        
    except Exception as e:
        print(f"更新机器码错误: {e}")
        print(f"异常详情: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500

@app.route('/update_user_points', methods=['POST'])
def update_user_points():
    """更新用户积分（新接口，与set_points功能相同但返回格式统一）"""
    try:
        print("收到更新积分请求")
        
        data = request.get_json()
        phone = data.get('phone')
        new_points = data.get('points')
        
        print(f"更新积分参数: phone={phone}, points={new_points}")
        
        if not phone or new_points is None:
            return jsonify({
                "success": False,
                "message": "手机号和积分不能为空"
            }), 400
        
        # 查找用户是否存在
        user = users.find_one({"phone": phone})
        if not user:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404
        
        # 更新积分
        result = users.update_one(
            {"phone": phone}, 
            {"$set": {"points": int(new_points), "updated_at": datetime.now()}}
        )
        
        if result.modified_count > 0:
            print(f"积分更新成功: {phone} -> {new_points}")
            return jsonify({
                "success": True,
                "message": "积分更新成功",
                "data": {
                    "phone": phone,
                    "points": int(new_points),
                    "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "积分更新失败"
            }), 500
        
    except Exception as e:
        print(f"更新积分错误: {e}")
        print(f"异常详情: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500

@app.route('/toggle_user_status', methods=['POST'])
def toggle_user_status():
    """切换用户状态（启用/禁用）"""
    try:
        print("收到切换状态请求")
        
        data = request.get_json()
        phone = data.get('phone')
        
        print(f"切换状态参数: phone={phone}")
        
        if not phone:
            return jsonify({
                "success": False,
                "message": "手机号不能为空"
            }), 400
        
        # 查找用户
        user = users.find_one({"phone": phone})
        if not user:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404
        
        # 切换状态
        current_status = user.get("status", 1)
        new_status = 0 if current_status == 1 else 1
        
        result = users.update_one(
            {"phone": phone}, 
            {"$set": {"status": new_status, "updated_at": datetime.now()}}
        )
        
        if result.modified_count > 0:
            status_text = "启用" if new_status == 1 else "禁用"
            print(f"状态切换成功: {phone} -> {status_text}")
            
            return jsonify({
                "success": True,
                "message": f"用户状态已{status_text}",
                "data": {
                    "phone": phone,
                    "status": new_status,
                    "statusText": status_text,
                    "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "状态切换失败"
            }), 500
        
    except Exception as e:
        print(f"切换状态错误: {e}")
        print(f"异常详情: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"状态切换失败: {str(e)}"
        }), 500

# ==========================================
# 原有功能保持不变
# ==========================================

@app.route("/set_points", methods=["POST"])
def set_points():
    try:
        data = request.json
        phone = data.get("phone")
        points = data.get("points")
        
        result = users.update_one({"phone": phone}, {"$set": {"points": points}})
        if result.matched_count > 0:
            return jsonify({"success": True, "points": points})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        print(f"设置积分错误: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

@app.route("/set_status", methods=["POST"])
def set_status():
    try:
        data = request.json
        phone = data.get("phone")
        status = data.get("status")
        
        result = users.update_one({"phone": phone}, {"$set": {"status": status}})
        if result.matched_count > 0:
            return jsonify({"success": True, "status": status})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        print(f"设置状态错误: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

# ==========================================
# 增强的管理后台
# ==========================================

@app.route("/admin")
def admin_page():
    try:
        all_users = list(users.find({}))
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>乐影系统 - 管理后台</title>
    <meta charset="utf-8">
    <style>
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 1.2em; margin: 10px 0; opacity: 0.9; }
        .main-content { background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 30px; background: #f8f9fa; }
        .stat-card { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .stat-card h3 { font-size: 2.5em; margin: 0; font-weight: bold; }
        .stat-card p { margin: 10px 0 0; font-size: 1.1em; opacity: 0.9; }
        .feature-section { padding: 30px; border-bottom: 1px solid #eee; }
        .feature-section h3 { color: #333; margin-bottom: 20px; font-size: 1.4em; }
        .form-row { display: flex; gap: 15px; align-items: end; flex-wrap: wrap; }
        .form-group { flex: 1; min-width: 150px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #555; }
        .form-group input, .form-group select { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 14px; transition: border-color 0.3s; }
        .form-group input:focus, .form-group select:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s; text-decoration: none; display: inline-block; }
        .btn-primary { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
        .btn-success { background: linear-gradient(135deg, #56ab2f, #a8e6cf); color: white; }
        .btn-warning { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
        .btn-danger { background: linear-gradient(135deg, #fc466b, #3f5efb); color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .machine-code-section { background: linear-gradient(135deg, #a8edea, #fed6e3); }
        .machine-code-section .current-code { background: rgba(0,0,0,0.1); padding: 15px; border-radius: 8px; margin-top: 15px; font-family: 'Courier New', monospace; }
        .table-container { padding: 30px; }
        table { width: 100%; border-collapse: collapse; border-radius: 8px; overflow: hidden; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        th { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px; text-align: left; font-weight: 600; }
        td { padding: 15px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f8f9fa; }
        .status-enabled { color: #28a745; font-weight: bold; }
        .status-disabled { color: #dc3545; font-weight: bold; }
        .machine-code { font-family: 'Courier New', monospace; font-size: 12px; background: #f1f3f4; padding: 4px 8px; border-radius: 4px; }
        .btn-group { display: flex; gap: 5px; flex-wrap: wrap; }
        .btn-sm { padding: 6px 12px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 乐影系统管理后台</h1>
            <p>版本 1.2 | 完整机器码管理功能</p>
        </div>
        
        <div class="main-content">
            <div class="stats">
                <div class="stat-card">
                    <h3>{{ total_users }}</h3>
                    <p>总用户数</p>
                </div>
                <div class="stat-card">
                    <h3>{{ enabled_users }}</h3>
                    <p>启用用户</p>
                </div>
                <div class="stat-card">
                    <h3>{{ disabled_users }}</h3>
                    <p>禁用用户</p>
                </div>
                <div class="stat-card">
                    <h3>{{ bound_machines }}</h3>
                    <p>已绑定设备</p>
                </div>
            </div>
            
            <div class="feature-section machine-code-section">
                <h3>🔧 机器码管理</h3>
                <form onsubmit="updateMachineCode(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>手机号</label>
                            <input type="text" id="machinePhone" placeholder="输入手机号" required>
                        </div>
                        <div class="form-group">
                            <label>新机器码</label>
                            <input type="text" id="newMachineCode" placeholder="输入新机器码" required>
                        </div>
                        <div class="form-group">
                            <button type="submit" class="btn btn-success">更新机器码</button>
                        </div>
                    </div>
                </form>
                <div class="current-code">
                    <strong>💡 当前设备真实机器码：</strong><br>
                    <code>9DC6B72833DBFDA6</code><br>
                    <small>点击右侧按钮可快速填入当前机器码</small>
                    <button onclick="fillCurrentMachineCode()" class="btn btn-warning btn-sm" style="margin-left: 10px;">使用当前机器码</button>
                </div>
            </div>
            
            <div class="feature-section">
                <h3>➕ 添加新用户</h3>
                <form onsubmit="addUser(event)">
                    <div class="form-row">
                        <div class="form-group">
                            <label>手机号</label>
                            <input type="text" id="phone" placeholder="输入手机号" required>
                        </div>
                        <div class="form-group">
                            <label>初始积分</label>
                            <input type="number" id="points" placeholder="0" value="0">
                        </div>
                        <div class="form-group">
                            <label>账号状态</label>
                            <select id="status">
                                <option value="1">启用</option>
                                <option value="0">禁用</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <button type="submit" class="btn btn-primary">添加用户</button>
                        </div>
                    </div>
                </form>
            </div>
            
            <div class="table-container">
                <h3>👥 用户管理</h3>
                <table>
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
                        {% for user in users %}
                        <tr>
                            <td><strong>{{ user.phone }}</strong></td>
                            <td>{{ user.points or 0 }}</td>
                            <td class="{{ 'status-enabled' if user.status == 1 else 'status-disabled' }}">
                                {{ '✅ 启用' if user.status == 1 else '❌ 禁用' }}
                            </td>
                            <td>
                                {% if user.machineCode %}
                                    <span class="machine-code" title="{{ user.machineCode }}">{{ user.machineCode }}</span>
                                {% else %}
                                    <span style="color: #999;">未绑定</span>
                                {% endif %}
                            </td>
                            <td>{{ user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A' }}</td>
                            <td>
                                <div class="btn-group">
                                    <button onclick="editPoints('{{ user.phone }}')" class="btn btn-primary btn-sm">改积分</button>
                                    <button onclick="editMachineCode('{{ user.phone }}')" class="btn btn-warning btn-sm">改机器码</button>
                                    <button onclick="toggleStatus('{{ user.phone }}', {{ user.status or 1 }})" class="btn btn-success btn-sm">
                                        {{ '禁用' if user.status == 1 else '启用' }}
                                    </button>
                                    <button onclick="deleteUser('{{ user.phone }}')" class="btn btn-danger btn-sm">删除</button>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        function showMessage(message, isSuccess = true) {
            const alertType = isSuccess ? 'success' : 'error';
            alert(`${isSuccess ? '✅' : '❌'} ${message}`);
        }
        
        function fillCurrentMachineCode() {
            document.getElementById('newMachineCode').value = '9DC6B72833DBFDA6';
        }
        
        function updateMachineCode(event) {
            event.preventDefault();
            const phone = document.getElementById('machinePhone').value;
            const machineCode = document.getElementById('newMachineCode').value;
            
            fetch('/update_machine_code', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, machineCode})
            })
            .then(response => response.json())
            .then(data => {
                showMessage(data.message, data.success);
                if (data.success) {
                    setTimeout(() => location.reload(), 1000);
                }
            })
            .catch(error => showMessage('请求失败: ' + error, false));
        }
        
        function addUser(event) {
            event.preventDefault();
            const phone = document.getElementById('phone').value;
            const points = document.getElementById('points').value;
            const status = document.getElementById('status').value;
            
            fetch('/admin/add_user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, points: parseInt(points), status: parseInt(status)})
            })
            .then(response => response.json())
            .then(data => {
                showMessage(data.message, data.success);
                if (data.success) {
                    setTimeout(() => location.reload(), 1000);
                }
            })
            .catch(error => showMessage('请求失败: ' + error, false));
        }
        
        function editPoints(phone) {
            const points = prompt('请输入新积分:');
            if (points !== null && !isNaN(points)) {
                fetch('/set_points', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, points: parseInt(points)})
                })
                .then(response => response.json())
                .then(data => {
                    showMessage(data.success ? '积分更新成功' : data.message, data.success);
                    if (data.success) setTimeout(() => location.reload(), 1000);
                });
            }
        }
        
        function editMachineCode(phone) {
            const machineCode = prompt('请输入新机器码\\n\\n提示：当前设备机器码为 9DC6B72833DBFDA6');
            if (machineCode !== null && machineCode.trim() !== '') {
                fetch('/update_machine_code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, machineCode: machineCode.trim()})
                })
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message, data.success);
                    if (data.success) setTimeout(() => location.reload(), 1000);
                });
            }
        }
        
        function toggleStatus(phone, currentStatus) {
            const newStatus = currentStatus === 1 ? 0 : 1;
            const action = newStatus === 1 ? '启用' : '禁用';
            
            if (confirm(`确认${action}用户 ${phone}?`)) {
                fetch('/set_status', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, status: newStatus})
                })
                .then(response => response.json())
                .then(data => {
                    showMessage(data.success ? `用户已${action}` : data.message, data.success);
                    if (data.success) setTimeout(() => location.reload(), 1000);
                });
            }
        }
        
        function deleteUser(phone) {
            if (confirm('确认删除用户 ' + phone + '?\\n\\n⚠️ 此操作不可恢复！')) {
                fetch('/admin/delete_user', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone})
                })
                .then(response => response.json())
                .then(data => {
                    showMessage(data.message, data.success);
                    if (data.success) setTimeout(() => location.reload(), 1000);
                });
            }
        }
    </script>
</body>
</html>
        """
        
        # 计算统计数据
        enabled_users = len([u for u in all_users if u.get('status', 1) == 1])
        disabled_users = len(all_users) - enabled_users
        bound_machines = len([u for u in all_users if u.get('machineCode')])
        
        return render_template_string(
            html_template, 
            users=all_users, 
            total_users=len(all_users),
            enabled_users=enabled_users,
            disabled_users=disabled_users,
            bound_machines=bound_machines
        )
    except Exception as e:
        print(f"管理页面错误: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/admin/add_user", methods=["POST"])
def admin_add_user():
    try:
        data = request.json
        phone = data.get("phone")
        points = data.get("points", 0)
        status = data.get("status", 1)
        
        # 检查用户是否已存在
        if users.find_one({"phone": phone}):
            return jsonify({"success": False, "message": "用户已存在"}), 400
        
        user_doc = {
            "phone": phone,
            "points": points,
            "status": status,
            "created_at": datetime.now()
        }
        
        users.insert_one(user_doc)
        return jsonify({"success": True, "message": "用户添加成功"})
    except Exception as e:
        print(f"添加用户错误: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

@app.route("/admin/delete_user", methods=["POST"])
def admin_delete_user():
    try:
        data = request.json
        phone = data.get("phone")
        
        result = users.delete_one({"phone": phone})
        if result.deleted_count > 0:
            return jsonify({"success": True, "message": "用户删除成功"})
        else:
            return jsonify({"success": False, "message": "用户不存在"}), 404
    except Exception as e:
        print(f"删除用户错误: {e}")
        return jsonify({"success": False, "message": "Internal server error"}), 500

# ==========================================
# 启动服务器
# ==========================================

if __name__ == "__main__":
    print("🚀 启动乐影系统API服务器 v1.2")
    print("=" * 50)
    print("✅ 新增功能:")
    print("  - /update_machine_code - 更新用户机器码")
    print("  - /update_user_points - 更新用户积分")
    print("  - /toggle_user_status - 切换用户状态")
    print("  - 美化的管理后台界面")
    print("=" * 50)
    print("🌐 API端点:")
    print("  - GET  /          - 服务状态")
    print("  - GET  /health    - 健康检查")
    print("  - POST /login     - 用户登录")
    print("  - POST /set_points - 设置积分")
    print("  - POST /set_status - 设置状态")
    print("  - POST /update_machine_code - 更新机器码")
    print("  - POST /update_user_points - 更新积分")
    print("  - POST /toggle_user_status - 切换状态")
    print("  - GET  /admin     - 管理后台")
    print("=" * 50)
    print("📱 当前设备机器码: 9DC6B72833DBFDA6")
    print("🎯 访问管理后台: http://your-server:5000/admin")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False) 