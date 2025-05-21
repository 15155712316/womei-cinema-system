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
        phone = self.phone_entry.get().strip()
        ck = self.ck_entry.get().strip()
        openid = self.openid_entry.get().strip()
        cinemaid = self.get_cinemaid_func() if self.get_cinemaid_func else None
        if not cinemaid:
            self.show_centered_popup("提示", "请选择登录影院", 1200)
            return
        try:
            result = login_and_check_card(phone, ck, openid, cinemaid)
            print("API返回：", result)
        except Exception as e:
            self.show_centered_popup("网络错误", f"请求失败: {e}", 2000)
            return
        self.handle_login_response(result, {
            "userid": phone,
            "openid": openid,
            "token": ck,
            "cinemaid": cinemaid,
            "balance": 0,
            "points": 0
        })

    def handle_login_response(self, resp_json, account_info):
        # 只要resultCode为0都写入账号数据
        cardno = ''
        balance = 0
        score = 0
        members = resp_json.get('resultData', {}).get('members')
        if members and isinstance(members, list) and len(members) > 0:
            card = members[0]
            cardno = card.get('CARDNO', '')
            balance = card.get('BALANCE', card.get('balance', 0))
            score = card.get('SCORE', 0)
            self.show_centered_popup("登录成功", "登录成功，已获取会员卡！", duration=1500)
        else:
            self.show_centered_popup("登录成功", "登录成功，但未查到会员卡。", duration=1500)
        # 更新账号信息
        account_info['cardno'] = cardno
        account_info['balance'] = balance
        account_info['score'] = score
        self.save_account_info(account_info)
        if self.refresh_account_list_func:
            self.refresh_account_list_func()

    def save_account_info(self, account_info):
        import os, json
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'accounts.json')
        if not os.path.exists(os.path.dirname(data_path)):
            os.makedirs(os.path.dirname(data_path))
        accounts = []
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
            except Exception:
                accounts = []
        # 检查是否已存在该账号（cinemaid+userid唯一）
        found = False
        for acc in accounts:
            if acc.get('cinemaid') == account_info['cinemaid'] and acc.get('userid') == account_info['userid']:
                acc.update(account_info)
                found = True
                break
        if not found:
            accounts.append(account_info)
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2) 