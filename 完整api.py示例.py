from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_admin import Admin
from flask_admin.contrib.pymongo import ModelView

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Flask-Admin需要

# MongoDB连接
client = MongoClient("mongodb://testuser:testpass@127.0.0.1:27017/userdb")
db = client["userdb"]
users = db["users"]

# API接口
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    phone = data.get("phone")
    machine_code = data.get("machineCode")
    user = users.find_one({"phone": phone})
    if not user:
        return jsonify({"success": False, "message": "Not registered"}), 403
    if "machineCode" not in user:
        users.update_one({"phone": phone}, {"$set": {"machineCode": machine_code}})
    elif user["machineCode"] != machine_code:
        return jsonify({"success": False, "message": "Device not authorized"}), 403
    if user.get("status", 1) != 1:
        return jsonify({"success": False, "message": "Account disabled"}), 403
    return jsonify({"success": True, "message": "Login success", "data": user})

@app.route("/set_points", methods=["POST"])
def set_points():
    data = request.json
    phone = data.get("phone")
    points = data.get("points")
    users.update_one({"phone": phone}, {"$set": {"points": points}})
    return jsonify({"success": True, "points": points})

@app.route("/set_status", methods=["POST"])
def set_status():
    data = request.json
    phone = data.get("phone")
    status = data.get("status")
    users.update_one({"phone": phone}, {"$set": {"status": status}})
    return jsonify({"success": True, "status": status})

# 管理后台
admin = Admin(app, name='UserAdmin', template_mode='bootstrap3')
admin.add_view(ModelView(users, 'Users'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 