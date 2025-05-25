import ttkbootstrap as tb
import requests
import json
import tkinter as tk
from tkinter import messagebox
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.account_api import login_and_check_card

class LoginPanel(tb.Frame):
    def __init__(self, master, get_cinemaid_func=None, refresh_account_list_func=None):
        super().__init__(master)
        self.pack_propagate(False)
        self.get_cinemaid_func = get_cinemaid_func  # 主窗口传入的获取当前cinemaid的方法
        self.refresh_account_list_func = refresh_account_list_func  # 主窗口传入的刷新账号列表方法

        entry_style = {
            'font': ("微软雅黑", 9),
            'bootstyle': 'secondary',
            'width': 18
        }
        label_style = {
            'font': ("微软雅黑", 8),
            'bootstyle': 'secondary',
            'anchor': 'w',
            'padding': (2, 0, 0, 0)
        }
        entry_pad = {'ipadx': 2, 'ipady': 1}

        # 第一行：手机号输入框
        row1 = tb.Frame(self)
        row1.pack(fill="x", padx=8, pady=(8, 2))
        tb.Label(row1, text="手机号", **label_style).pack(fill="x")
        self.phone_entry = tb.Entry(row1, **entry_style)
        self.phone_entry.pack(fill="x", expand=True, **entry_pad)

        # 第二行：ck输入框
        row2 = tb.Frame(self)
        row2.pack(fill="x", padx=8, pady=2)
        tb.Label(row2, text="ck (Cookie/凭证)", **label_style).pack(fill="x")
        self.ck_entry = tb.Entry(row2, **entry_style)
        self.ck_entry.pack(fill="x", expand=True, **entry_pad)

        # 第三行：openid输入框
        row3 = tb.Frame(self)
        row3.pack(fill="x", padx=8, pady=2)
        tb.Label(row3, text="openid (微信唯一标识，可选)", **label_style).pack(fill="x")
        self.openid_entry = tb.Entry(row3, **entry_style)
        self.openid_entry.pack(fill="x", expand=True, **entry_pad)

        # 第四行：登录按钮
        row4 = tb.Frame(self)
        row4.pack(fill="x", padx=8, pady=(6, 8))
        login_btn = tb.Button(
            row4,
            text="登录",
            bootstyle="secondary,outline",
            width=10,
            command=self.on_login
        )
        login_btn.pack(fill="x", ipadx=2, ipady=2)

        # 美化：按钮背景白色，字体黑色
        style = tb.Style()
        style.configure("TButton", background="#fff", foreground="#000", font=("微软雅黑", 9))
        style.map("TButton", background=[("active", "#f0f0f0")])
        # ttkbootstrap输入框已较圆润，如需极致圆角需更高级UI库

    def show_centered_popup(self, title, msg, duration=1500):
        parent = self.winfo_toplevel()
        popup = tk.Toplevel(parent)
        popup.title(title)
        popup.transient(parent)
        popup.grab_set()
        popup.update_idletasks()
        w, h = 260, 100
        x = parent.winfo_x() + (parent.winfo_width() - w) // 2
        y = parent.winfo_y() + (parent.winfo_height() - h) // 2
        popup.geometry(f"{w}x{h}+{x}+{y}")
        popup.resizable(False, False)
        tk.Label(popup, text=msg, font=("微软雅黑", 11)).pack(expand=True, fill="both", padx=10, pady=10)
        popup.after(duration, popup.destroy)

    def on_login(self):
        """登录按钮点击事件 - 添加详细日志"""
        phone = self.phone_entry.get().strip()
        ck = self.ck_entry.get().strip()
        openid = self.openid_entry.get().strip()
        
        print(f"[登录流程] 开始登录流程")
        print(f"[登录流程] 输入信息 - 手机号: {phone}")
        print(f"[登录流程] 输入信息 - CK长度: {len(ck)}")
        print(f"[登录流程] 输入信息 - OpenID: {openid}")
        
        # 验证必填字段
        if not phone:
            print(f"[登录流程] 验证失败 - 手机号为空")
            self.show_centered_popup("输入错误", "请输入手机号", 1500)
            return
            
        if not ck:
            print(f"[登录流程] 验证失败 - CK为空")
            self.show_centered_popup("输入错误", "请输入CK凭证", 1500)
            return
        
        # 获取影院ID
        cinemaid = self.get_cinemaid_func() if self.get_cinemaid_func else None
        print(f"[登录流程] 当前影院ID: {cinemaid}")
        
        if not cinemaid:
            print(f"[登录流程] 验证失败 - 未选择影院")
            self.show_centered_popup("提示", "请先在影院/券tab中选择登录影院", 2000)
            return
            
        # 显示登录中提示
        print(f"[登录流程] 开始调用登录API")
        self.show_centered_popup("登录中", "正在验证账号信息...", 500)
        
        try:
            # 调用登录API
            result = login_and_check_card(phone, ck, openid, cinemaid)
            print(f"[登录流程] API调用成功")
            print(f"[登录流程] API返回结果: {result}")
            
        except Exception as e:
            print(f"[登录流程] API调用异常: {e}")
            self.show_centered_popup("网络错误", f"请求失败: {e}", 3000)
            return
            
        # 处理登录响应
        account_info = {
            "userid": phone,
            "openid": openid,
            "token": ck,
            "cinemaid": cinemaid,
            "balance": 0,
            "points": 0
        }
        
        print(f"[登录流程] 开始处理登录响应")
        self.handle_login_response(result, account_info)

    def handle_login_response(self, resp_json, account_info):
        """处理登录响应 - 添加详细日志和优化逻辑"""
        print(f"[登录响应] 开始处理登录响应")
        print(f"[登录响应] 响应数据: {resp_json}")
        
        # 检查响应状态
        result_code = resp_json.get('resultCode', '')
        result_desc = resp_json.get('resultDesc', '未知错误')
        
        print(f"[登录响应] 响应状态码: {result_code}")
        print(f"[登录响应] 响应描述: {result_desc}")
        
        # 只要resultCode为0都认为登录成功
        if result_code != '0':
            print(f"[登录响应] 登录失败 - {result_desc}")
            self.show_centered_popup("登录失败", f"登录失败: {result_desc}", 3000)
            return
            
        print(f"[登录响应] 登录成功，开始处理会员卡信息")
        
        # 处理会员卡信息
        cardno = ''
        balance = 0
        score = 0
        
        result_data = resp_json.get('resultData', {})
        print(f"[登录响应] resultData: {result_data}")
        
        # 修复：如果resultData为None，则设为空字典
        if result_data is None:
            result_data = {}
            print(f"[登录响应] resultData为None，设为空字典")
        
        members = result_data.get('members', [])
        print(f"[登录响应] 会员卡列表: {members}")
        
        if members and isinstance(members, list) and len(members) > 0:
            card = members[0]
            cardno = card.get('CARDNO', '') or card.get('cardno', '')
            balance = float(card.get('BALANCE', card.get('balance', 0)))
            score = int(card.get('SCORE', card.get('score', 0)))
            
            print(f"[登录响应] 会员卡信息 - 卡号: {cardno}")
            print(f"[登录响应] 会员卡信息 - 余额: {balance}")
            print(f"[登录响应] 会员卡信息 - 积分: {score}")
            
            self.show_centered_popup("登录成功", f"登录成功！\n会员余额: ¥{balance}", duration=2000)
        else:
            print(f"[登录响应] 未查到会员卡信息")
            self.show_centered_popup("登录成功", "登录成功！\n未查到会员卡", duration=2000)
        
        # 更新账号信息
        account_info['cardno'] = cardno
        account_info['balance'] = balance
        account_info['score'] = score
        
        print(f"[登录响应] 最终账号信息: {account_info}")
        
        # 保存账号信息
        print(f"[登录响应] 开始保存账号信息")
        self.save_account_info(account_info)
        
        # 刷新账号列表
        print(f"[登录响应] 开始刷新账号列表")
        if self.refresh_account_list_func:
            self.refresh_account_list_func()
            print(f"[登录响应] 账号列表刷新完成")
        else:
            print(f"[登录响应] 警告: 未设置刷新账号列表回调函数")
            
        print(f"[登录响应] 登录流程完成")

    def save_account_info(self, account_info):
        """保存账号信息到文件 - 添加详细日志"""
        import os, json
        
        print(f"[账号保存] 开始保存账号信息")
        print(f"[账号保存] 账号信息: {account_info}")
        
        # 确定账号文件路径
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'accounts.json')
        print(f"[账号保存] 账号文件路径: {data_path}")
        
        # 确保数据目录存在
        data_dir = os.path.dirname(data_path)
        if not os.path.exists(data_dir):
            print(f"[账号保存] 创建数据目录: {data_dir}")
            os.makedirs(data_dir)
        
        # 读取现有账号列表
        accounts = []
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                print(f"[账号保存] 读取到现有账号数量: {len(accounts)}")
            except Exception as e:
                print(f"[账号保存] 读取现有账号文件失败: {e}")
                accounts = []
        else:
            print(f"[账号保存] 账号文件不存在，将创建新文件")
        
        # 检查是否已存在该账号（cinemaid+userid唯一）
        found = False
        for i, acc in enumerate(accounts):
            if acc.get('cinemaid') == account_info['cinemaid'] and acc.get('userid') == account_info['userid']:
                print(f"[账号保存] 发现重复账号，更新第{i+1}个账号")
                accounts[i].update(account_info)
                found = True
                break
        
        if not found:
            print(f"[账号保存] 新增账号到列表")
            accounts.append(account_info)
        
        # 保存账号列表
        try:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
            print(f"[账号保存] 账号信息保存成功，总账号数量: {len(accounts)}")
        except Exception as e:
            print(f"[账号保存] 保存账号文件失败: {e}")
            raise e 