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

# 根路径 - 显示API状态
@app.route("/")
def home():
    return jsonify({
        "service": "账号积分管理系统API",
        "status": "运行中",
        "version": "1.2",
        "endpoints": ["/login", "/set_points", "/set_status", "/update_machine_code", "/update_user_points", "/toggle_user_status", "/admin"]
    })

# 健康检查接口
@app.route("/health")
def health():
    try:
        users.count_documents({})
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        print(f"健康检查错误: {e}")
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        print(f"收到登录请求")
        
        # 检查请求数据
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
                user["machineCode"] = machine_code  # 更新本地数据
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
# 新增：机器码管理功能
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

# 增强的管理页面
@app.route("/admin")
def admin_page():
    try:
        all_users = list(users.find({}))
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>账号积分管理系统</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #2c3e50; color: white; }
        .btn { padding: 6px 12px; margin: 2px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }
        .btn-primary { background-color: #3498db; color: white; }
        .btn-success { background-color: #27ae60; color: white; }
        .btn-warning { background-color: #f39c12; color: white; }
        .btn-danger { background-color: #e74c3c; color: white; }
        .btn:hover { opacity: 0.8; }
        .add-form { margin: 20px 0; padding: 20px; background: #ecf0f1; border-radius: 6px; }
        .add-form input, .add-form select { padding: 8px; margin: 5px; border: 1px solid #bdc3c7; border-radius: 4px; }
        .status-enabled { color: #27ae60; font-weight: bold; }
        .status-disabled { color: #e74c3c; font-weight: bold; }
        .machine-code { font-family: monospace; font-size: 11px; max-width: 120px; overflow: hidden; text-overflow: ellipsis; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat-card { background: #3498db; color: white; padding: 15px; border-radius: 6px; text-align: center; flex: 1; }
        .update-machine-code { margin: 20px 0; padding: 20px; background: #e8f5e8; border-radius: 6px; border-left: 4px solid #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 账号积分管理系统 v1.2</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{{ total_users }}</h3>
                <p>总用户数</p>
            </div>
            <div class="stat-card" style="background: #27ae60;">
                <h3>{{ enabled_users }}</h3>
                <p>启用用户</p>
            </div>
            <div class="stat-card" style="background: #e74c3c;">
                <h3>{{ disabled_users }}</h3>
                <p>禁用用户</p>
            </div>
            <div class="stat-card" style="background: #f39c12;">
                <h3>{{ bound_machines }}</h3>
                <p>已绑定设备</p>
            </div>
        </div>
        
        <div class="update-machine-code">
            <h3>🔧 更新用户机器码</h3>
            <form onsubmit="updateMachineCode(event)">
                <input type="text" id="machinePhone" placeholder="手机号" required>
                <input type="text" id="newMachineCode" placeholder="新机器码" required>
                <button type="submit" class="btn btn-success">更新机器码</button>
            </form>
            <p style="margin-top: 10px; color: #666; font-size: 14px;">
                💡 提示：当前设备真实机器码为 <code>9DC6B72833DBFDA6</code>
            </p>
        </div>
        
        <div class="add-form">
            <h3>➕ 添加新用户</h3>
            <form onsubmit="addUser(event)">
                <input type="text" id="phone" placeholder="手机号" required>
                <input type="number" id="points" placeholder="初始积分" value="0">
                <select id="status">
                    <option value="1">启用</option>
                    <option value="0">禁用</option>
                </select>
                <button type="submit" class="btn btn-primary">添加用户</button>
            </form>
        </div>
        
        <h3>👥 用户列表</h3>
        <table>
            <tr>
                <th>手机号</th>
                <th>积分</th>
                <th>状态</th>
                <th>机器码</th>
                <th>创建时间</th>
                <th>操作</th>
            </tr>
            {% for user in users %}
            <tr>
                <td><strong>{{ user.phone }}</strong></td>
                <td>{{ user.points or 0 }}</td>
                <td class="{{ 'status-enabled' if user.status == 1 else 'status-disabled' }}">
                    {{ '✅ 启用' if user.status == 1 else '❌ 禁用' }}
                </td>
                <td class="machine-code" title="{{ user.machineCode or '未绑定' }}">
                    {{ user.machineCode or '未绑定' }}
                </td>
                <td>{{ user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A' }}</td>
                <td>
                    <button onclick="editPoints('{{ user.phone }}')" class="btn btn-primary">改积分</button>
                    <button onclick="editMachineCode('{{ user.phone }}')" class="btn btn-warning">改机器码</button>
                    <button onclick="toggleStatus('{{ user.phone }}', {{ user.status or 1 }})" class="btn btn-success">
                        {{ '禁用' if user.status == 1 else '启用' }}
                    </button>
                    <button onclick="deleteUser('{{ user.phone }}')" class="btn btn-danger">删除</button>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <script>
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
                if (data.success) {
                    alert('机器码更新成功！');
                    location.reload();
                } else {
                    alert('更新失败：' + data.message);
                }
            })
            .catch(error => alert('请求失败：' + error));
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
            }).then(() => location.reload());
        }
        
        function editPoints(phone) {
            const points = prompt('请输入新积分:');
            if (points !== null) {
                fetch('/set_points', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, points: parseInt(points)})
                }).then(() => location.reload());
            }
        }
        
        function editMachineCode(phone) {
            const machineCode = prompt('请输入新机器码:');
            if (machineCode !== null && machineCode.trim() !== '') {
                fetch('/update_machine_code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, machineCode: machineCode.trim()})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('机器码更新成功！');
                        location.reload();
                    } else {
                        alert('更新失败：' + data.message);
                    }
                });
            }
        }
        
        function toggleStatus(phone, currentStatus) {
            const newStatus = currentStatus === 1 ? 0 : 1;
            fetch('/set_status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({phone, status: newStatus})
            }).then(() => location.reload());
        }
        
        function deleteUser(phone) {
            if (confirm('确认删除用户 ' + phone + '?')) {
                fetch('/admin/delete_user', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone})
                }).then(() => location.reload());
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

if __name__ == "__main__":
    print("🚀 启动账号积分管理系统API v1.2")
    print("新增功能：")
    print("  - /update_machine_code - 更新用户机器码")
    print("  - /update_user_points - 更新用户积分")
    print("  - /toggle_user_status - 切换用户状态")
    print("  - 增强的管理后台界面")
    app.run(host="0.0.0.0", port=5000, debug=False) 