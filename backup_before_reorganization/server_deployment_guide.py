#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
线上API服务器部署指南
需要在 http://43.142.19.28:5000 服务器上添加的功能
"""

# 需要在您的Flask应用中添加以下路由：

from flask import Flask, request, jsonify
import json
import time

app = Flask(__name__)

# 假设您有用户数据存储（可能是数据库或文件）
# 这里用字典模拟，实际部署时请替换为您的数据存储方式
users_data = {
    "15155712316": {
        "phone": "15155712316",
        "machineCode": "7DA491096E7B6854",  # 当前绑定的机器码
        "points": 800,
        "status": 1,
        "created_at": "Wed, 28 May 2025 23:02:15 GMT"
    }
    # 其他用户...
}

@app.route('/update_machine_code', methods=['POST'])
def update_machine_code():
    """更新用户机器码"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        new_machine_code = data.get('machineCode')
        
        if not phone or not new_machine_code:
            return jsonify({
                "success": False,
                "message": "手机号和机器码不能为空"
            }), 400
        
        # 查找用户
        if phone not in users_data:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404
        
        # 更新机器码
        users_data[phone]['machineCode'] = new_machine_code
        
        # 这里需要保存到您的数据存储（数据库/文件等）
        # save_users_data(users_data)
        
        return jsonify({
            "success": True,
            "message": "机器码更新成功",
            "data": {
                "phone": phone,
                "machineCode": new_machine_code,
                "updateTime": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500

@app.route('/update_user_points', methods=['POST'])
def update_user_points():
    """更新用户积分"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        new_points = data.get('points')
        
        if not phone or new_points is None:
            return jsonify({
                "success": False,
                "message": "手机号和积分不能为空"
            }), 400
        
        # 查找用户
        if phone not in users_data:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404
        
        # 更新积分
        users_data[phone]['points'] = int(new_points)
        
        # 保存数据
        # save_users_data(users_data)
        
        return jsonify({
            "success": True,
            "message": "积分更新成功",
            "data": {
                "phone": phone,
                "points": int(new_points),
                "updateTime": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"更新失败: {str(e)}"
        }), 500

@app.route('/toggle_user_status', methods=['POST'])
def toggle_user_status():
    """切换用户状态（启用/禁用）"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        
        if not phone:
            return jsonify({
                "success": False,
                "message": "手机号不能为空"
            }), 400
        
        # 查找用户
        if phone not in users_data:
            return jsonify({
                "success": False,
                "message": "用户不存在"
            }), 404
        
        # 切换状态
        current_status = users_data[phone]['status']
        new_status = 0 if current_status == 1 else 1
        users_data[phone]['status'] = new_status
        
        # 保存数据
        # save_users_data(users_data)
        
        status_text = "启用" if new_status == 1 else "禁用"
        
        return jsonify({
            "success": True,
            "message": f"用户状态已{status_text}",
            "data": {
                "phone": phone,
                "status": new_status,
                "statusText": status_text,
                "updateTime": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"状态切换失败: {str(e)}"
        }), 500

@app.route('/admin')
def admin_panel():
    """管理后台界面"""
    # 返回管理后台HTML页面
    # 可以参考 server_api_sample.py 中的 admin_panel_html 内容
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>用户管理后台</title>
        <meta charset="utf-8">
        <!-- 这里放置管理界面的HTML代码 -->
    </head>
    <body>
        <h1>用户管理后台</h1>
        <!-- 管理界面内容 -->
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 