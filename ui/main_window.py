import tkinter as tk  # 导入tkinter库，tk是Python自带的GUI库
from tkinter import ttk, messagebox  # 导入ttk（美化控件）和messagebox（弹窗）
from ui.account_list_panel import AccountListPanel
from ui.cinema_select_panel import CinemaSelectPanel
from ui.seat_map_panel import SeatMapPanel
# 添加用户认证相关导入
from services.auth_service import auth_service
# 添加UI工具类导入
from services.ui_utils import MessageManager, CouponManager, UIConstants
import json
from services.order_api import create_order, get_unpaid_order_detail, get_coupons_by_order, bind_coupon, get_order_list, get_order_detail, get_order_qrcode_api, cancel_all_unpaid_orders, get_coupon_prepay_info, pay_order
import tkinter.messagebox as mb
from PIL import Image, ImageDraw, ImageFont, ImageTk
import io
import os
import re
import datetime
import time
import traceback

class CinemaOrderSimulatorUI(tk.Tk):  # 定义主窗口类，继承自tk.Tk
    def __init__(self):  # 初始化方法
        super().__init__()  # 调用父类初始化
        
        # 添加用户认证检查
        self.current_user = None
        self.auth_check_timer = None
        
        self.title("柴犬影院下单系统")  # 设置窗口标题
        self.geometry("1250x750")  # 设置窗口大小
        self.configure(bg="#f8f8f8")  # 设置窗口背景色
        self.last_priceinfo = {}

        # 初始化时隐藏主窗口，等待用户登录
        self.withdraw()
        
        # 启动用户认证检查
        self._start_auth_check()

        # 计算各栏宽度
        total_width = 1250
        total_height = 750
        left_w = int(total_width * 0.2)   # 1/5
        center_w = int(total_width * 0.6) # 3/5
        right_w = total_width - left_w - center_w  # 1/5

        # ========== 左栏 ==========
        left_frame = tk.Frame(self, bg="#f0f0f0")
        left_frame.place(x=0, y=0, width=left_w, height=total_height)

        # 左栏上下分区
        login_h = int(total_height * 0.33)
        account_h = total_height - login_h
        self.login_frame = tk.LabelFrame(left_frame, text="账号登录区", fg="red")
        self.login_frame.place(x=0, y=0, width=left_w, height=login_h)
        self.account_list_frame = tk.LabelFrame(left_frame, text="账号列表区", fg="red")
        self.account_list_frame.place(x=0, y=login_h, width=left_w, height=account_h)

        # 集成账号列表面板
        self.account_list_panel = AccountListPanel(
            self.account_list_frame,
            on_account_selected=self.set_current_account,
            on_set_main=self.set_main_account,
            on_clear_coupons=self.clear_coupons,
            on_refresh_coupons=self.refresh_coupons
        )
        self.account_list_panel.pack(fill=tk.BOTH, expand=True)

        # ========== 中栏 ==========
        center_frame = tk.Frame(self, bg="#fff")
        center_frame.place(x=left_w, y=0, width=center_w, height=total_height)
        center_top_h = int(total_height * 0.38)
        center_bottom_h = total_height - center_top_h
        # 上部tab栏
        center_top_frame = tk.Frame(center_frame)
        center_top_frame.place(x=0, y=0, width=center_w, height=center_top_h)
        self.center_notebook = ttk.Notebook(center_top_frame)
        self.center_notebook.place(x=0, y=0, width=center_w, height=center_top_h)
        # tab1: 左右分区
        tab1 = tk.Frame(self.center_notebook)
        tab1_left = tk.LabelFrame(tab1, text="影院选择区", fg="red")
        tab1_right = tk.LabelFrame(tab1, text="券列表区", fg="red")
        tab1_left.place(x=0, y=0, width=center_w//2, height=center_top_h)
        tab1_right.place(x=center_w//2, y=0, width=center_w//2, height=center_top_h)
        self.cinema_panel = CinemaSelectPanel(tab1_left, on_cinema_changed=self.on_cinema_changed)
        self.cinema_panel.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 设置主窗口引用，便于CinemaSelectPanel访问当前账号信息
        self.cinema_panel.set_main_window(self)

        # 券列表Listbox直接放到tab1_right，支持多选
        self.coupon_listbox = tk.Listbox(tab1_right, selectmode="multiple", font=("微软雅黑", 10), activestyle="dotbox")
        self.coupon_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        self.coupons_data = []
        self.selected_coupons = []
        self.max_coupon_select = 1  # 默认最多可选1张券，后续由订单详情接口ticketcount动态赋值
        self.coupon_listbox.bind('<<ListboxSelect>>', self.on_coupon_select)
        self.center_notebook.add(tab1, text="出票")
        # 其余tab: 全宽
        for i, name in enumerate(["绑券", "兑换券", "订单", "影院"]):
            tab = tk.Frame(self.center_notebook)
            if name == "绑券":
                self.build_bind_coupon_tab(tab)
            if name == "兑换券":
                self.build_coupon_exchange_tab(tab)
            if name == "订单":
                self.build_order_list_tab(tab)
            if name == "影院":
                self.build_cinema_management_tab(tab)
            self.center_notebook.add(tab, text=name)
        # 下部座位区
        center_bottom_frame = tk.LabelFrame(center_frame, text="座位区域", fg="red")
        center_bottom_frame.place(x=0, y=center_top_h, width=center_w, height=center_bottom_h)
        # 优化：使用pack并设置fill/expand，保证座位区和按钮不会被挤压
        self.seat_panel = SeatMapPanel(center_bottom_frame, seat_data=[])
        self.seat_panel.pack(fill="both", expand=True, padx=10, pady=10)
        self.seat_panel.set_account_getter(lambda: getattr(self, 'current_account', {}))
        self.seat_panel.set_on_submit_order(self.on_submit_order)
        # 绑定场次选择事件
        self.cinema_panel.set_seat_panel(self.seat_panel)

        # ========== 右栏 ==========
        right_frame = tk.Frame(self, bg="#f0f0f0")
        right_frame.place(x=left_w+center_w, y=0, width=right_w, height=total_height)
        # 右侧上下分布 - 取票码区在上，订单详情区在下
        qrcode_height = int(total_height * 0.45)  # 取票码区占45%
        orderinfo_height = total_height - qrcode_height  # 订单详情区占55%
        
        right_top = tk.Frame(right_frame, bg="#f0f0f0")
        right_top.place(x=0, y=0, width=right_w, height=qrcode_height)
        right_bottom = tk.Frame(right_frame, bg="#f0f0f0")
        right_bottom.place(x=0, y=qrcode_height, width=right_w, height=orderinfo_height)
        
        # 取票码区在上
        self.qrcode_frame = tk.LabelFrame(right_top, text="取票码区", fg="red")
        self.qrcode_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        # 订单详情区在下
        self.orderinfo_frame = tk.LabelFrame(right_bottom, text="订单详情区", fg="red")
        self.orderinfo_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 取票码区预留
        self.qrcode_label = tk.Label(self.qrcode_frame, text="(二维码/取票码展示区)", font=("微软雅黑", 12))
        self.qrcode_label.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # 订单详情区控件
        self.orderinfo_mobile = tk.Label(self.orderinfo_frame, text="", fg="red", font=("微软雅黑", 12, "bold"))
        self.orderinfo_mobile.pack(anchor="w", padx=4, pady=(4,0))
        self.orderinfo_text = tk.Text(self.orderinfo_frame, height=12, wrap="word", font=("微软雅黑", 10), state="disabled")
        self.orderinfo_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        
        # 订单失效时间（放在一键支付按钮上面）
        self.orderinfo_countdown = tk.Label(self.orderinfo_frame, text="", fg="#0077ff", font=("微软雅黑", 10, "bold"))
        self.orderinfo_countdown.pack(anchor="w", padx=4, pady=(2,0))
        
        # 一键支付按钮
        self.pay_btn = tk.Button(self.orderinfo_frame, text="一键支付", bg="#ff9800", fg="#fff", font=("微软雅黑", 11, "bold"), command=self.on_one_click_pay)
        self.pay_btn.pack(fill=tk.X, padx=4, pady=(2,4))
        
        # 初始化状态变量
        self.current_order = None
        self.member_info = None
        self.selected_coupons_info = None
        self.current_coupon_info = None
        
        # 添加UI状态跟踪
        self.ui_state = "initial"  # initial, order_submitted, payment_success
        self.show_debug = False  # 控制调试信息显示
    
    def _start_auth_check(self):
        """启动用户认证检查"""
        # 延迟导入PyQt5登录窗口，避免与Tkinter冲突
        import sys
        from PyQt5.QtWidgets import QApplication
        
        # 检查是否已有QApplication实例
        if not QApplication.instance():
            # 创建QApplication实例
            self.qt_app = QApplication(sys.argv)
        else:
            self.qt_app = QApplication.instance()
        
        from ui.login_window import LoginWindow
        
        # 创建并显示登录窗口
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_user_login_success)
        
        # 在主窗口中心显示登录窗口
        self.center_login_window()
        self.login_window.show()
    
    def center_login_window(self):
        """居中显示登录窗口"""
        # 确保主窗口已完全创建
        self.update_idletasks()
        
        # 获取主窗口位置和大小
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        # 计算登录窗口居中位置
        login_width = 400
        login_height = 500
        x = main_x + (main_width - login_width) // 2
        y = main_y + (main_height - login_height) // 2
        
        self.login_window.move(x, y)
    
    def _on_user_login_success(self, user_info):
        """用户登录成功回调"""
        print(f"[认证] 用户登录成功: {user_info.get('username', '未知用户')}")
        
        # 保存用户信息
        self.current_user = user_info
        
        # 关闭登录窗口
        if hasattr(self, 'login_window'):
            self.login_window.close()
        
        # 退出Qt事件循环
        if hasattr(self, 'qt_app'):
            self.qt_app.quit()
        
        # 显示主窗口
        self.deiconify()
        
        # 启动定期认证检查
        self._start_periodic_auth_check()
        
        # 自动加载初始状态
        self._auto_load_initial_state()
    
    def _start_periodic_auth_check(self):
        """启动定期权限检查"""
        def check_auth():
            try:
                is_valid, message, user_info = auth_service.check_auth()
                
                if not is_valid:
                    # 认证失效，强制重新登录
                    print(f"[权限检查] 认证失效: {message}")
                    messagebox.showerror("权限验证失败", f"{message}\n\n请重新登录")
                    self.logout_and_restart()
                    return
                
                # 更新用户信息
                if user_info:
                    self.current_user = user_info
                    username = user_info.get('username', '用户')
                    points = user_info.get('points', 0)
                    self.title(f"柴犬影院下单系统 - {username} (积分: {points})")
                
                # 继续定期检查
                self.auth_check_timer = self.after(30000, check_auth)  # 30秒检查一次
                
            except Exception as e:
                print(f"[权限检查] 检查异常: {e}")
                # 出现异常也继续检查
                self.auth_check_timer = self.after(60000, check_auth)  # 1分钟后再检查
        
        # 首次检查延迟5秒
        self.auth_check_timer = self.after(5000, check_auth)
    
    def logout_and_restart(self):
        """登出并重启认证"""
        # 停止定期检查
        if self.auth_check_timer:
            self.after_cancel(self.auth_check_timer)
            self.auth_check_timer = None
        
        # 清除用户信息
        auth_service.logout()
        self.current_user = None
        
        # 隐藏主窗口
        self.withdraw()
        
        # 重新显示登录窗口
        self._start_auth_check()
    
    def check_permission_before_action(self, action_name: str, points_cost: int = 0) -> bool:
        """
        在执行重要操作前检查权限
        :param action_name: 操作名称
        :param points_cost: 积分消耗
        :return: 是否允许执行
        """
        if not self.current_user:
            messagebox.showerror("权限错误", "用户未登录")
            return False
        
        # 检查认证状态
        is_valid, message, user_info = auth_service.check_auth()
        if not is_valid:
            messagebox.showerror("权限验证失败", f"{message}\n\n请重新登录")
            self.logout_and_restart()
            return False
        
        # 检查积分（如果需要）
        if points_cost > 0:
            current_points = user_info.get('points', 0)
            if current_points < points_cost:
                messagebox.showerror("积分不足", f"操作\"{action_name}\"需要 {points_cost} 积分\n当前积分: {current_points}")
                return False
        
        return True
    
    def use_points_for_action(self, action_name: str, points_cost: int) -> bool:
        """
        为操作扣除积分
        :param action_name: 操作名称
        :param points_cost: 积分消耗
        :return: 是否扣除成功
        """
        if points_cost <= 0:
            return True
        
        success, message = auth_service.use_points(action_name, points_cost)
        if success:
            # 更新本地用户信息
            if self.current_user:
                new_points = self.current_user.get('points', 0) - points_cost
                self.current_user['points'] = max(0, new_points)
                
                # 更新窗口标题
                username = self.current_user.get('username', '用户')
                self.title(f"柴犬影院下单系统 - {username} (积分: {self.current_user['points']})")
            
            print(f"[积分扣除] {action_name}: -{points_cost}, {message}")
            return True
        else:
            messagebox.showerror("积分扣除失败", message)
            return False

    def _auto_load_initial_state(self):
        """
        自动加载初始状态：
        1. 加载账号列表（无需选择影院）
        2. 自动选择主账号
        3. 如果有主账号，自动选择对应影院
        """
        print("[程序启动] 执行自动加载初始状态...")
        
        try:
            # 1. 加载所有账号（无需先选择影院）
            with open("data/accounts.json", "r", encoding="utf-8") as f:
                all_accounts = json.load(f)
            
            if not all_accounts:
                print("[程序启动] 无账号数据")
                return
            
            # 2. 找到主账号
            main_accounts = [acc for acc in all_accounts if acc.get('is_main')]
            if not main_accounts:
                print("[程序启动] 无主账号，使用第一个账号")
                main_account = all_accounts[0]
            else:
                main_account = main_accounts[0]
                print(f"[程序启动] 找到主账号: {main_account.get('userid')} @ {main_account.get('cinemaid')}")
            
            # 3. 根据主账号的影院ID自动选择影院
            main_cinemaid = main_account.get('cinemaid')
            if main_cinemaid and hasattr(self.cinema_panel, 'cinemas'):
                for i, cinema in enumerate(self.cinema_panel.cinemas):
                    if cinema.get('cinemaid') == main_cinemaid:
                        print(f"[程序启动] 自动选择影院: {cinema.get('name', '未知影院')}")
                        self.cinema_panel.cinema_combo.current(i)
                        # 注意：不触发on_cinema_select，避免循环调用
                        break
            
            # 4. 刷新账号列表（现在有了选中的影院）
            self.refresh_account_list()
            
            print("[程序启动] 自动加载初始状态完成")
            
        except Exception as e:
            print(f"[程序启动] 自动加载初始状态异常: {e}")

    def _build_account_area(self):  # 构建账号管理区
        # 账号输入
        tk.Label(self.account_frame, text="账号:").pack(anchor="w")  # 账号标签
        tk.Entry(self.account_frame).pack(fill=tk.X, pady=2)  # 账号输入框
        tk.Label(self.account_frame, text="密码:").pack(anchor="w")  # 密码标签
        tk.Entry(self.account_frame, show="*").pack(fill=tk.X, pady=2)  # 密码输入框
        tk.Button(self.account_frame, text="登录", width=8).pack(side=tk.LEFT, pady=4, padx=2)  # 登录按钮
        tk.Button(self.account_frame, text="导入", width=8).pack(side=tk.LEFT, pady=4, padx=2)  # 导入按钮
        # 账号列表（简化为Listbox）
        tk.Label(self.account_frame, text="账号列表:").pack(anchor="w", pady=(6,0))  # 账号列表标签
        tk.Listbox(self.account_frame, height=5).pack(fill=tk.BOTH, expand=True, pady=2)  # 账号列表框

    

    def _build_coupon_area(self):  # 构建券列表区
        tk.Label(self.coupon_frame, text="可用券:").pack(anchor="w")  # 券列表标签
        tk.Listbox(self.coupon_frame, height=6).pack(fill=tk.BOTH, expand=True, pady=2)  # 券列表框

    def _build_seatmap_area(self):  # 构建座位图区
        # 座位图区域（用按钮模拟座位）
        seat_frame = tk.Frame(self.seatmap_frame)  # 座位按钮的Frame
        seat_frame.pack(pady=10)  # 上下留白
        rows, cols = 9, 20  # 9排20列
        for r in range(rows):  # 遍历每一排
            tk.Label(seat_frame, text=f"排{r+1}", fg="navy").grid(row=r, column=0, padx=2)  # 每排左侧显示排号
            for c in range(cols):  # 遍历每一列
                btn = tk.Button(seat_frame, text=str(c+1), width=2, height=1, bg="#fff", relief="groove")  # 创建座位按钮
                btn.grid(row=r, column=c+1, padx=1, pady=1)  # 放到对应位置
        # 选座和下单按钮
        tk.Button(self.seatmap_frame, text="提交订单", bg="#4caf50", fg="#fff", width=20).pack(pady=10)  # 提交订单按钮

    def _build_qrcode_area2(self):  # 构建取票码区
        tk.Label(self.qrcode_frame2, text="出票成功", fg="green", font=("Arial", 12)).pack(pady=2)  # 出票成功提示
        tk.Label(self.qrcode_frame2, text="109922684", font=("Arial", 14, "bold")).pack(pady=2)  # 取票码
        # 二维码占位
        qr_canvas = tk.Canvas(self.qrcode_frame2, width=100, height=100, bg="#eee")  # 二维码画布
        qr_canvas.create_text(50, 50, text="二维码", fill="gray")  # 显示"二维码"字样
        qr_canvas.pack(pady=5)  # 上下留白
        tk.Button(self.qrcode_frame2, text="复制取票码").pack(fill=tk.X, pady=2)  # 复制取票码按钮

    def _build_orderinfo_area(self):  # 构建订单信息区
        tk.Label(self.orderinfo_frame, text="订单详情", fg="red", font=("Arial", 12, "bold")).pack(anchor="w", pady=2)  # 订单详情标题
        order_text = tk.Text(self.orderinfo_frame, height=10, wrap="word")  # 订单详情文本框
        order_text.insert(tk.END, "订单号: 14700283316\n影片: 独一无二\n时间: 2025-05-18 17:50\n座位: 7排8座\n应付: ¥38.9\n余额: ¥1490.1\n")  # 示例订单内容
        order_text.pack(fill=tk.BOTH, expand=True, pady=2)  # 填充整个区域
        tk.Button(self.orderinfo_frame, text="一键支付", bg="#ff9800", fg="#fff").pack(fill=tk.X, pady=4)  # 一键支付按钮

    def get_selected_cinemaid(self):
        # 获取影院选择区当前选中的cinemaid
        idx = self.cinema_panel.cinema_combo.current()
        if idx < 0:
            return None
        return self.cinema_panel.cinemas[idx]['cinemaid']

    def set_current_account(self, account):
        self.current_account = account
        self.cinema_panel.set_current_account(account)
        # 更新券绑定界面的账号信息
        self.update_bind_account_info()
        # 更新兑换券界面的账号信息
        self.update_exchange_account_info()

    def set_main_account(self, account):
        # 设置主账号并保存到accounts.json
        import json
        try:
            with open("data/accounts.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)
            for acc in accounts:
                acc["is_main"] = (acc["userid"] == account["userid"] and acc["cinemaid"] == account["cinemaid"])
            with open("data/accounts.json", "w", encoding="utf-8") as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
            self.refresh_account_list()
            messagebox.showinfo("主账号设置", f"账号 {account['userid']} 已设为主账号")
        except Exception as e:
            messagebox.showerror("主账号设置失败", str(e))

    def clear_coupons(self):
        """清空券列表 - 根据UI状态决定是否执行"""
        CouponManager.clear_coupons_if_needed(self.ui_state, self._clear_coupons_impl)
    
    def _clear_coupons_impl(self):
        """实际执行清空券列表操作"""
        self.update_coupons(None)

    def refresh_coupons(self):
        # 账号Tab刷新券按钮逻辑，调用独立券接口（待开发），此处先清空券列表
        if self.ui_state == "order_submitted":
            # 只在订单提交后才刷新券
            self.update_coupons(None)
            if UIConstants.should_show_success_popup("coupon_refresh"):
                MessageManager.show_info(self, "刷新券", "已刷新券列表（接口待开发）")
        else:
            print("[券管理] 当前状态不允许刷新券列表")

    def refresh_account_list(self):
        try:
            with open("data/accounts.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)
        except Exception:
            accounts = []
        
        cinemaid = self.get_selected_cinemaid()
        print(f"[账号刷新] 当前选中影院ID: {cinemaid}")
        
        # 修复：当没有选择影院时，显示所有账号；有选择影院时，只显示该影院的账号
        if cinemaid:
            filtered = [acc for acc in accounts if acc['cinemaid'] == cinemaid]
            print(f"[账号刷新] 筛选影院 {cinemaid} 的账号: {len(filtered)} 个")
        else:
            filtered = accounts
            print(f"[账号刷新] 显示所有账号: {len(filtered)} 个")
        
        # 修复：优先选择当前影院的主账号，而不是全局第一个主账号
        main_idx = 0  # 默认选择第一个
        if cinemaid and filtered:
            # 找到当前影院的主账号
            cinema_main_idx = next((i for i, acc in enumerate(filtered) if acc.get('is_main') and acc.get('cinemaid') == cinemaid), -1)
            if cinema_main_idx >= 0:
                main_idx = cinema_main_idx
                print(f"[账号选择] 选择当前影院 {cinemaid} 的主账号: {filtered[main_idx].get('userid')}")
            else:
                print(f"[账号选择] 当前影院 {cinemaid} 无主账号，选择第一个账号")
        elif filtered and not cinemaid:
            # 没有选择影院时，选择全局主账号
            global_main_idx = next((i for i, acc in enumerate(filtered) if acc.get('is_main')), -1)
            if global_main_idx >= 0:
                main_idx = global_main_idx
                print(f"[账号选择] 选择全局主账号: {filtered[main_idx].get('userid')}")
        
        self.account_list_panel.update_accounts(filtered)
        if filtered:
            self.account_list_panel.tree.selection_set(self.account_list_panel.tree.get_children()[main_idx])
            self.set_current_account(filtered[main_idx])
            print(f"[账号选择] 已设置当前账号: {filtered[main_idx].get('userid')} (余额:{filtered[main_idx].get('balance', 0)})")
        else:
            self.set_current_account(None)
            print(f"[账号选择] 无可用账号")

    def on_cinema_changed(self):
        print(f"[影院切换] 影院已切换，正在刷新账号列表...")
        self.refresh_account_list()
        self.clear_coupons()

    def on_seat_selected(self, event):
        print(f"[DEBUG] on_seat_selected called with {len(selected_seats)} seats")
        print(f"[DEBUG] current last_priceinfo: {getattr(self, 'last_priceinfo', None)}")
        # 修复f-string语法错误
        seat_desc = [f"{s.get('row')}排{s.get('num')}座" for s in selected_seats]
        print(f"[DEBUG] selected seats: {seat_desc}")
        # 注意：这里不应该清空券列表，因为这只是选座操作，不应该影响已选择的券
        # self.clear_coupons()  # 暂时注释掉，避免影响选座体验

    def on_submit_order(self, selected_seats):
        """
        提交订单逻辑 - 完整流程
        1. 检查未付款订单并取消
        2. 获取会员信息
        3. 创建订单
        4. 更新支付信息
        5. 查询可用券
        """
        if not selected_seats:
            MessageManager.show_warning(self, "提示", "请先选择座位")
            return
            
        account = getattr(self, 'current_account', {})
        if not account.get('userid'):
            MessageManager.show_warning(self, "提示", "请先选择账号")
            return
            
        cinemaid = self.get_selected_cinemaid()
        if not cinemaid:
            MessageManager.show_warning(self, "提示", "请先选择影院")
            return
            
        print(f"[下单流程] 开始下单，座位数: {len(selected_seats)}")
        print(f"[下单流程] 当前账号: {account.get('userid')}")
        
        # 设置UI状态为下单中
        self.ui_state = "ordering"
        
        try:
            # 1. 取消未付款订单
            self._cancel_unpaid_orders(account, cinemaid)
            
            # 2. 获取会员信息
            self.member_info = self._get_member_info(account, cinemaid)
            
            # 3. 创建订单
            order_result = self._create_order(account, cinemaid, selected_seats)
            
            if order_result and order_result.get('resultCode') == '0':
                # 下单成功，设置UI状态为已提交订单
                self.ui_state = "order_submitted"
                print(f"[下单流程] 下单成功，状态更新为: {self.ui_state}")
                
                orderno = order_result['resultData']['orderno']
                print(f"[下单流程] 订单号: {orderno}")
                
                # 4. 查询未支付订单详情
                try:
                    detail_params = {
                        'orderno': orderno,
                        'groupid': '',
                        'cinemaid': cinemaid,
                        'cardno': account.get('cardno', ''),
                        'userid': account['userid'],
                        'openid': account['openid'],
                        'CVersion': '3.9.12',
                        'OS': 'Windows',
                        'token': account['token'],
                        'source': '2'
                    }
                    
                    unpaid_detail = get_unpaid_order_detail(detail_params)
                    print(f"[下单流程] 未支付订单详情: {unpaid_detail}")
                    
                    if unpaid_detail and unpaid_detail.get('resultCode') == '0':
                        self.current_order = unpaid_detail
                        self.show_order_detail(unpaid_detail)
                        
                        # 5. 查询可用券 - 使用未支付订单详情中的票数
                        ticket_count = unpaid_detail['resultData'].get('ticketcount', 1)
                        
                        # 查询可用券
                        coupon_params = {
                            'orderno': orderno,
                            'groupid': '',
                            'cinemaid': cinemaid,
                            'cardno': account.get('cardno', ''),
                            'userid': account['userid'],
                            'openid': account['openid'],
                            'CVersion': '3.9.12',
                            'OS': 'Windows',
                            'token': account['token'],
                            'source': '2'
                        }
                        
                        coupon_result = get_coupons_by_order(coupon_params)
                        print(f"[下单流程] 可用券查询结果: {coupon_result}")
                        
                        # 更新券列表显示 - 使用未支付订单详情中的票数
                        self.update_coupons(coupon_result, ticket_count)
                        
                        # 同时更新影院选择面板的券列表（如果存在）
                        if hasattr(self.cinema_panel, 'update_coupons'):
                            self.cinema_panel.update_coupons(coupon_result)
                    else:
                        # 获取未支付订单详情失败，使用原始创建订单结果
                        print(f"[下单流程] 获取未支付订单详情失败: {unpaid_detail}")
                        self.current_order = order_result
                        self.show_order_detail(order_result)
                        
                except Exception as e:
                    print(f"[下单流程] 获取未支付订单详情异常: {e}")
                    # 异常时使用原始创建订单结果
                    self.current_order = order_result
                    self.show_order_detail(order_result)
            elif order_result:
                # 下单失败，恢复初始状态
                self.ui_state = "initial"
                error_msg = order_result.get('resultDesc', '下单失败')
                MessageManager.show_error(self, "下单失败", error_msg)
            else:
                self.ui_state = "initial"
                MessageManager.show_error(self, "下单失败", "未收到有效的响应")
                
        except Exception as e:
            # 异常时恢复初始状态
            self.ui_state = "initial"
            print(f"[下单流程] 异常: {e}")
            MessageManager.show_error(self, "下单失败", f"下单过程中发生错误: {e}")
    
    def _cancel_unpaid_orders(self, account, cinemaid):
        """取消未付款订单"""
        print(f"[下单流程DEBUG] _cancel_unpaid_orders方法被调用！账号: {account.get('userid')}, 影院: {cinemaid}")
        try:
            print("[下单流程] 检查未付款订单...")
            result = cancel_all_unpaid_orders(account, cinemaid)
            if result:
                print(f"[下单流程] 取消了 {result.get('cancelledCount', 0)} 个未付款订单")
            else:
                print("[下单流程] cancel_all_unpaid_orders返回None")
        except Exception as e:
            print(f"[下单流程] 取消未付款订单异常: {e}")
            traceback.print_exc()
    
    def _get_member_info(self, account, cinemaid):
        """获取会员信息"""
        try:
            from services.member_service import member_service
            member_info = member_service(account, cinemaid)  # 直接调用函数，不是.get_member_info
            if member_info:
                print(f"[下单流程] 获取会员信息成功，余额: {member_info.get('balance', 0)}")
            else:
                print("[下单流程] 无会员卡信息")
            return member_info
        except Exception as e:
            print(f"[下单流程] 获取会员信息异常: {e}")
            return None
    
    def _create_order(self, account, cinemaid, selected_seats):
        """创建订单"""
        # 获取场次和影片信息
        session = self.cinema_panel.get_current_session_info()
        film = self.cinema_panel.get_current_film_info()
        priceinfo = getattr(self, 'last_priceinfo', {})
        
        # 验证必要信息
        print(f"[下单调试] session: {session}")
        print(f"[下单调试] film: {film}")
        print(f"[下单调试] priceinfo: {priceinfo}")
        
        if not session:
            raise Exception("获取场次信息失败，请重新选择场次")
        if not film:
            raise Exception("获取影片信息失败，请重新选择影片")
            
        # 提取必要的场次参数，使用安全的get方法
        show_time = session.get('k', '')
        hall_code = session.get('j', '')
        show_code = session.get('g', '')
        
        if not show_time or not hall_code or not show_code:
            raise Exception(f"场次信息不完整：showTime={show_time}, hallCode={hall_code}, showCode={show_code}")

        # 获取实际价格
        actual_price = int(float(priceinfo.get('proprice', 45))) if priceinfo.get('proprice') else 45
        
        seat_info_list = []
        for idx, seat in enumerate(selected_seats):
            # 修正座位信息的字段映射
            seat_row = int(seat['row'])
            seat_num = int(seat['num'])  # 座位号
            
            seat_info_list.append({
                "seatInfo": f"{seat['row']}排{seat['num']}座",
                "eventPrice": 0,
                "strategyPrice": actual_price,
                "ticketPrice": actual_price,
                "seatRow": seat_row,
                "seatRowId": seat_row,
                "seatCol": str(seat_num),  # 修正：使用座位号的字符串形式
                "seatColId": str(seat_num),  # 修正：使用座位号的字符串形式
                "seatNo": seat['sn'],
                "sectionId": seat.get('sectionId', '11111'),
                "ls": seat.get('ls', 19),  # 修正：使用正确的ls值，默认19
                "rowIndex": seat_row + 1,  # 修正：rowIndex应该是排数+1
                "colIndex": seat_num + 3,  # 修正：colIndex应该是座位号+3
                "index": idx + 6  # 修正：index从6开始递增
            })
        seat_info_json = json.dumps(seat_info_list, ensure_ascii=False)

        params = {
            'groupid': '',
            'cardno': 'undefined',  # 修正：应该是undefined而不是实际卡号
            'userid': account['userid'],
            'cinemaid': cinemaid,
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'openid': account['openid'],
            'source': '2',
            'oldOrderNo': '',
            'showTime': show_time,
            'eventCode': '',
            'hallCode': hall_code,
            'showCode': show_code,
            'filmCode': 'null',  # 修正：应该是字符串'null'
            'filmNo': film.get('fc', ''),  # 修正：使用fc字段而不是fno
            'recvpPhone': 'undefined',  # 修正：应该是undefined
            'seatInfo': seat_info_json,
            'payType': 3,
            'companyChannelId': 5,
            'shareMemberId': '',
            'limitprocount': 0
        }
        
        print(f"[下单调试] 修正后下单参数: {params}")
        
        try:
            result = create_order(params)
            print(f"[下单调试] create_order返回: {result}")
            return result
        except Exception as e:
            print(f"[下单调试] create_order异常: {e}")
            raise Exception(f"创建订单失败: {e}")
    
    def show_order_detail(self, detail):
        """显示订单详情"""
        self.orderinfo_text.config(state="normal")
        self.orderinfo_text.delete('1.0', 'end')
        self.orderinfo_mobile.config(text="")
        self.orderinfo_countdown.config(text="")
        
        if detail.get('resultCode') == '0':
            data = detail['resultData']
            print(f"[订单详情调试] 原始数据: {data}")
            
            # 手机号红色加粗 - 从订单详情中获取
            mobile = data.get('orderMobile', '')
            if not mobile:
                # 如果订单详情中没有手机号，从当前账号获取
                account = getattr(self, 'current_account', {})
                mobile = account.get('userid', '') if account else ''
            self.orderinfo_mobile.config(text=f"手机号：{mobile}")
            
            # 从订单详情中获取信息（新的数据结构）
            orderno = data.get('orderno', '')
            film_name = data.get('filmName', '未知影片')
            show_time = data.get('showTime', '未知时间')
            hall_name = data.get('hallName', '未知影厅')
            seat_info = data.get('seatInfo', '未知座位')  # 已经格式化好的座位信息
            
            # 票价计算 - 使用新的字段
            ticket_price_cents = int(data.get('ticketPrice', 0))  # 分为单位
            ticket_price = ticket_price_cents / 100  # 转为元
            
            # 按照要求的顺序构建信息
            info_lines = []
            info_lines.append(f"订单号：{orderno}")
            info_lines.append(f"影片：{film_name}")
            info_lines.append(f"时间：{show_time}")
            info_lines.append(f"影厅：{hall_name}")
            info_lines.append(f"座位：{seat_info}")
            info_lines.append(f"票价：¥{ticket_price:.2f}")
            
            # 会员相关信息（仅会员显示）
            is_member = self.member_info and self.member_info.get('is_member')
            if is_member:
                # 会员价：直接使用未支付订单详情接口的memprice字段（分转元）
                mem_price_cents = int(data.get('memprice', 0))
                mem_price = mem_price_cents / 100
                info_lines.append(f"会员价：¥{mem_price:.2f}")
                
                balance = self.member_info.get('balance', 0)
                info_lines.append(f"会员余额：¥{balance}")
            
            # 券选择情况显示
            coupon_info = getattr(self, 'current_coupon_info', None)
            if coupon_info and coupon_info.get('resultCode') == '0':
                coupon_data = coupon_info['resultData']
                coupon_count = coupon_data.get('couponcount', 0)
                info_lines.append(f"已选择券：{coupon_count}张")
                
                if is_member:
                    # 会员选券后显示会员支付金额（分转元）
                    mem_payment = int(coupon_data.get('mempaymentAmount', 0)) / 100
                    info_lines.append(f"会员支付：¥{mem_payment:.2f}")
                else:
                    # 非会员选券后显示总支付金额（分转元）
                    payment = int(coupon_data.get('paymentAmount', 0)) / 100
                    info_lines.append(f"需付金额：¥{payment:.2f}")
            else:
                # 未选择券或券信息无效的情况
                selected_coupons = getattr(self, 'selected_coupons', [])
                if selected_coupons:
                    # 有选择券但券信息无效
                    info_lines.append(f"券信息无效（已选{len(selected_coupons)}张）")
                else:
                    # 未选择券
                    info_lines.append("未选择券")
                
                if is_member:
                    # 会员未选券：使用mem_totalprice字段（分转元）
                    mem_total_price_cents = int(data.get('mem_totalprice', 0))
                    mem_total_price = mem_total_price_cents / 100
                    info_lines.append(f"会员支付：¥{mem_total_price:.2f}")
                else:
                    # 非会员未选券：显示payAmount字段（分转元）
                    pay_amount_cents = int(data.get('payAmount', 0))
                    pay_amount = pay_amount_cents / 100
                    info_lines.append(f"需付金额：¥{pay_amount:.2f}")
            
            # 订单超时时间
            timeout_ms = int(data.get('orderTimeOut', 420000))  # 默认7分钟
            self._order_timeout_left = timeout_ms // 1000
            self._order_timeout_active = True
            
            # 显示信息
            info = '\n'.join(info_lines)
            self.orderinfo_text.insert('end', info)
            self.orderinfo_text.config(state="disabled")
            
            # 启动倒计时显示（在文本框下方）
            self._update_order_countdown()
            
            print(f"[订单详情] 显示完成，订单号: {orderno}")
        else:
            error_msg = detail.get('resultDesc', '未知错误')
            self.orderinfo_text.insert('end', f"查询失败: {error_msg}")
            self.orderinfo_text.config(state="disabled")
            print(f"[订单详情] 显示失败: {error_msg}")

    def _update_order_countdown(self):
        if hasattr(self, '_order_timeout_left') and self._order_timeout_left > 0 and getattr(self, '_order_timeout_active', False):
            mins = self._order_timeout_left // 60
            secs = self._order_timeout_left % 60
            self.orderinfo_countdown.config(text=f"{mins}分{secs}秒后订单失效")
            self._order_timeout_left -= 1
            self.after(1000, self._update_order_countdown)
        elif hasattr(self, '_order_timeout_active') and self._order_timeout_active:
            self.orderinfo_countdown.config(text="订单已失效")
            self._order_timeout_active = False

    def update_coupons(self, coupon_result, ticketcount=1):
        """更新券列表显示"""
        # 清空现有券列表
        self.coupon_listbox.delete(0, 'end')
        self.coupons_data = []
        self.selected_coupons = []
        
        # 设置最大可选券数
        self.max_coupon_select = int(ticketcount) if str(ticketcount).isdigit() else 1
        
        # 确保Listbox为多选模式
        self.coupon_listbox.config(selectmode="multiple")
        
        if not coupon_result or coupon_result.get('resultCode') != '0':
            self.coupon_listbox.insert('end', '无可用优惠券')
            return
            
        # 获取券数据
        vouchers = coupon_result.get('resultData', {}).get('vouchers', [])
        
        if not vouchers:
            self.coupon_listbox.insert('end', '暂无可用优惠券')
            return
        
        # 按有效期升序排列
        vouchers.sort(key=lambda v: v.get('expireddate', ''))
        
        # 添加券到列表
        for i, v in enumerate(vouchers):
            # 获取券名 - 尝试多个字段
            name = v.get('couponname') or v.get('voucherName') or v.get('name', f'券{i+1}')
            
            # 获取有效期
            expire = v.get('expireddate') or v.get('expiredDate') or '未知'
            
            # 获取券号 - 尝试多个字段
            code = v.get('couponcode') or v.get('voucherCode') or v.get('code', f'未知券号{i+1}')
            
            # 格式化显示
            display = f"{name} | 有效期至 {expire} | 券号 {code}"
            self.coupon_listbox.insert('end', display)
            self.coupons_data.append(v)
        
        print(f"[券列表] 券列表更新完成，共 {len(vouchers)} 张券，最多可选 {self.max_coupon_select} 张")

    def on_coupon_select(self, event):
        # 获取当前选中的券码
        idxs = self.coupon_listbox.curselection()
        if not idxs or not self.current_order:
            self.selected_coupons_info = None
            self.current_coupon_info = None
            self.selected_coupons = []
            # 刷新订单详情显示
            self.show_order_detail(self.current_order)
            return

        # 只允许选择最多 self.max_coupon_select 张券
        if len(idxs) > self.max_coupon_select:
            # 取消超出数量的选择
            for i in idxs[self.max_coupon_select:]:
                self.coupon_listbox.selection_clear(i)
            idxs = self.coupon_listbox.curselection()
            messagebox.showwarning("选券数量限制", f"最多只能选择 {self.max_coupon_select} 张券！")

        # 正确获取券号 - 修复字段名问题
        selected_codes = []
        for i in idxs:
            coupon = self.coupons_data[i]
            # 尝试多个可能的券号字段
            code = coupon.get('couponcode') or coupon.get('voucherCode') or coupon.get('code', '')
            selected_codes.append(code)
        
        orderno = self.current_order['resultData']['orderno']
        account = getattr(self, 'current_account', {})
        cinemaid = self.get_selected_cinemaid()

        # 实时请求券抵扣信息
        if selected_codes and selected_codes[0]:  # 确保券号不为空
            try:
                from services.order_api import get_coupon_prepay_info
                couponcode = ','.join(selected_codes)
                
                prepay_params = {
                    'orderno': orderno,
                    'couponcode': couponcode,
                    'groupid': '',
                    'cinemaid': cinemaid,
                    'cardno': account.get('cardno', ''),
                    'userid': account['userid'],
                    'openid': account['openid'],
                    'CVersion': '3.9.12',
                    'OS': 'Windows',
                    'token': account['token'],
                    'source': '2'
                }
                
                print(f"[选券价格查询] 请求参数: {prepay_params}")
                coupon_info = get_coupon_prepay_info(prepay_params)
                print(f"[选券价格查询] 返回结果: {coupon_info}")
                
                if coupon_info.get('resultCode') == '0':
                    # 保存券价格信息
                    self.current_coupon_info = coupon_info
                    self.selected_coupons = selected_codes
                    print(f"[券选择] 已选择券: {selected_codes}")
                    print(f"[券选择] 券数: {len(selected_codes)}/{self.max_coupon_select}")
                    
                    # 刷新订单详情显示
                    self.show_order_detail(self.current_order)
                else:
                    # 查询失败，清空选择
                    self.current_coupon_info = None
                    self.selected_coupons = []
                    MessageManager.show_warning(self, "选券失败", coupon_info.get('resultDesc', '未知错误'))
                    # 取消选择
                    for i in idxs:
                        self.coupon_listbox.selection_clear(i)
                    
            except Exception as e:
                print(f"[选券价格查询] 异常: {e}")
                self.current_coupon_info = None
                self.selected_coupons = []
                messagebox.showerror("选券异常", f"查询券价格信息失败: {e}")
                # 取消选择
                for i in idxs:
                    self.coupon_listbox.selection_clear(i)
        else:
            # 券号为空
            self.current_coupon_info = None
            self.selected_coupons = []
            print(f"[券选择] 券号为空，已清空选择")

    def build_bind_coupon_tab(self, tab):
        # 券号输入区
        input_frame = tk.Frame(tab)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # 当前账号信息显示
        info_frame = tk.Frame(input_frame)
        info_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 8))
        self.bind_account_info = tk.Label(info_frame, text="当前账号：未选择", font=("微软雅黑", 10, "bold"), fg="red", wraplength=300, justify="left")
        self.bind_account_info.pack(anchor="w")
        
        tk.Label(input_frame, text="每行一个券号：").grid(row=1, column=0, sticky="w", padx=2, pady=(2, 0))
        # 输入框
        self.coupon_text = tk.Text(input_frame, height=16, width=24)
        self.coupon_text.grid(row=2, column=0, sticky="nsew", padx=0, pady=(0, 4))
        # 按钮
        bind_btn = tk.Button(input_frame, text="绑定当前账号", command=self.on_bind_coupons, bg="#4caf50", fg="#fff", font=("微软雅黑", 11, "bold"))
        bind_btn.grid(row=3, column=0, sticky="ew", padx=0, pady=(0, 0))
        # 行权重
        input_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(0, weight=1)
        
        # 日志输出区
        log_frame = tk.Frame(tab)
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        tk.Label(log_frame, text="绑定日志：").pack(anchor="w")
        self.bind_log_text = tk.Text(log_frame, height=18, width=40, state="normal")
        self.bind_log_text.pack(fill=tk.BOTH, expand=True)
        tk.Button(log_frame, text="复制日志", command=self.copy_bind_log).pack(anchor="e", pady=4)
        
        # 更新账号信息显示
        self.update_bind_account_info()

    def update_bind_account_info(self):
        """更新券绑定界面的账号信息显示"""
        account = getattr(self, 'current_account', None)
        if hasattr(self, 'bind_account_info'):
            if account:
                # 获取影院名称
                cinema_name = "未知影院"
                try:
                    from services.cinema_manager import cinema_manager
                    cinemas = cinema_manager.load_cinema_list()
                    for cinema in cinemas:
                        if cinema.get('cinemaid') == account.get('cinemaid'):
                            cinema_name = cinema.get('cinemaShortName', '未知影院')
                            break
                except:
                    pass
                
                info_text = (f"当前账号：{account['userid']}\n"
                           f"影院：{cinema_name}\n"
                           f"余额：{account.get('balance', 0)}  积分：{account.get('score', 0)}")
                self.bind_account_info.config(text=info_text, fg="blue")
            else:
                self.bind_account_info.config(text="请先选择账号和影院", fg="red")

    def on_bind_coupons(self):
        account = getattr(self, 'current_account', None)
        if not account:
            mb.showwarning("未选中账号", "请先在左侧账号列表选择要绑定的账号！")
            return
        
        # 验证账号信息完整性
        required_fields = ['cinemaid', 'userid', 'openid', 'token']
        for field in required_fields:
            if not account.get(field):
                mb.showwarning("账号信息不完整", f"当前账号缺少{field}字段，请重新登录！")
                return
        
        print(f"[券绑定] 使用账号: {account.get('userid')} @ {account.get('cinemaid')}")
        print(f"[券绑定] Token: {account.get('token', '')[:10]}...")
        
        coupon_codes = self.coupon_text.get("1.0", "end").strip().splitlines()
        coupon_codes = [c.strip() for c in coupon_codes if c.strip()]
        if not coupon_codes:
            mb.showwarning("无券号", "请输入至少一个券号！")
            return
        
        # 添加进度提示
        mb.showinfo("开始绑定", f"即将绑定{len(coupon_codes)}张券，每张券间隔0.2秒，请稍候...")
        
        log_lines = []
        success, fail = 0, 0
        fail_codes = []
        
        # 导入延迟模块
        import time
        
        for i, code in enumerate(coupon_codes, 1):
            params = {
                'couponcode': code,
                'cinemaid': account['cinemaid'],
                'userid': account['userid'],
                'openid': account['openid'],
                'token': account['token'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'source': '2',
                'groupid': '',
                'cardno': account.get('cardno', '')
            }
            
            print(f"[券绑定] 正在绑定第{i}/{len(coupon_codes)}张券: {code}")
            
            try:
                res = bind_coupon(params)
                print(f"[券绑定] 券{code}绑定结果: {res}")
                
                if res.get('resultCode') == '0':
                    log_lines.append(f"券{code} 绑定成功")
                    success += 1
                else:
                    error_desc = res.get('resultDesc', '未知错误')
                    log_lines.append(f"券{code} 绑定失败：{error_desc}")
                    fail += 1
                    fail_codes.append(code)
                    
                    # 特殊处理token失效问题
                    if 'TOKEN_INVALID' in error_desc:
                        log_lines.append(f"  -> Token可能已失效，建议重新登录账号")
                        
            except Exception as e:
                error_msg = str(e)
                log_lines.append(f"券{code} 绑定失败：{error_msg}")
                fail += 1
                fail_codes.append(code)
                print(f"[券绑定] 券{code}绑定异常: {e}")
            
            # 添加0.2秒延迟（除了最后一张券）
            if i < len(coupon_codes):
                print(f"[券绑定] 等待0.2秒后绑定下一张券...")
                time.sleep(0.2)
        
        # 更新UI并显示总结
        log_lines.append(f"\n=== 绑定完成 ===")
        log_lines.append(f"共{len(coupon_codes)}张券，绑定成功{success}，失败{fail}")
        if fail_codes:
            log_lines.append(f"失败券号：{', '.join(fail_codes)}")
        
        # 如果全部失败且都是TOKEN_INVALID，给出建议
        if fail == len(coupon_codes) and all('TOKEN_INVALID' in line for line in log_lines if '绑定失败' in line):
            log_lines.append(f"\n*** 建议 ***")
            log_lines.append(f"所有券都显示TOKEN_INVALID错误")
            log_lines.append(f"请尝试：")
            log_lines.append(f"1. 重新登录当前账号")
            log_lines.append(f"2. 检查账号是否在对应影院有效")
            log_lines.append(f"3. 确认券号格式是否正确")
        
        self.bind_log_text.config(state="normal")
        self.bind_log_text.delete("1.0", "end")
        self.bind_log_text.insert("end", "\n".join(log_lines))
        self.bind_log_text.config(state="normal")
        
        # 完成提示
        if success > 0:
            if UIConstants.should_show_success_popup("bind_coupon"):
                MessageManager.show_info(self, "绑定完成", f"成功绑定{success}张券，失败{fail}张券")
        else:
            MessageManager.show_warning(self, "绑定失败", f"所有{fail}张券绑定失败，请检查账号状态和券号")

    def copy_bind_log(self):
        log = self.bind_log_text.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(log)
        if UIConstants.should_show_success_popup("copy_log"):
            MessageManager.show_info(self, "复制成功", "日志内容已复制到剪贴板！")

    def build_order_list_tab(self, tab):
        # 顶部刷新按钮
        top_frame = tk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=4)
        refresh_btn = tk.Button(top_frame, text="刷新", width=8, command=self.refresh_order_list)
        refresh_btn.pack(side=tk.LEFT, padx=8)
        # 订单表格
        columns = ("影片", "影院", "状态", "订单号")
        style = ttk.Style()
        style.configure("Order.Treeview", font=("微软雅黑", 13), rowheight=36)
        style.configure("Order.Treeview.Heading", font=("微软雅黑", 13, "bold"))
        self.order_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12, style="Order.Treeview")
        for col in columns:
            self.order_tree.heading(col, text=col)
            self.order_tree.column(col, width=180 if col=="影院" else 150, anchor="center")
        self.order_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)
        # 滚动条
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.order_tree.delete(*self.order_tree.get_children())
        self.order_tree.bind('<Double-1>', self.on_order_double_click)
        
        # 添加右键菜单
        self.order_context_menu = tk.Menu(self.order_tree, tearoff=0)
        self.order_context_menu.add_command(label="取消订单", command=self.cancel_selected_order)
        self.order_tree.bind('<Button-3>', self.show_order_context_menu)  # 右键点击
        
        # 保存订单数据用于右键操作
        self.order_data_cache = []

    def show_order_context_menu(self, event):
        """显示订单右键菜单"""
        # 选择点击的行
        item = self.order_tree.identify_row(event.y)
        if item:
            self.order_tree.selection_set(item)
            # 检查是否为未付款订单
            values = self.order_tree.item(item, 'values')
            if len(values) >= 3:
                status = values[2]  # 状态列
                if status == "未付款":
                    # 只有未付款订单才显示取消菜单
                    self.order_context_menu.post(event.x_root, event.y_root)

    def cancel_selected_order(self):
        """取消选中的订单"""
        selection = self.order_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.order_tree.item(item, 'values')
        if len(values) < 4:
            return
            
        film, cinema, status, orderno = values
        
        if status != "未付款":
            MessageManager.show_warning(self, "无法取消", "只能取消未付款订单")
            return
            
        # 确认取消
        result = MessageManager.show_question(self, "确认取消", f"确定要取消订单 {orderno} 吗？\n影片：{film}")
        if not result:
            return
            
        # 获取当前账号和影院信息
        account = getattr(self, 'current_account', None)
        cinemaid = self.get_selected_cinemaid()
        if not account or not cinemaid:
            MessageManager.show_warning(self, "取消失败", "请先选择账号和影院")
            return
            
        try:
            from services.order_api import cancel_order
            cancel_params = {
                'orderno': orderno,
                'groupid': '',
                'cinemaid': cinemaid,
                'cardno': account.get('cardno', ''),
                'userid': account['userid'],
                'openid': account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account['token'],
                'source': '2'
            }
            
            print(f"[右键取消订单] 正在取消订单: {orderno}")
            # 调用取消接口，不检查返回值
            cancel_order(cancel_params)
            
            # 提示用户并刷新列表
            if UIConstants.should_show_success_popup("cancel_order"):
                MessageManager.show_info(self, "取消成功", f"已发送取消请求\n订单号：{orderno}")
            self.refresh_order_list()
            
        except Exception as e:
            print(f"[右键取消订单] 取消订单异常: {e}")
            MessageManager.show_error(self, "取消失败", f"取消订单时发生错误：{e}")

    def refresh_order_list(self):
        # 校验影院和账号
        cinemaid = self.get_selected_cinemaid()
        account = getattr(self, 'current_account', None)
        if not cinemaid:
            mb.showwarning("未选中影院", "请先选择影院！")
            return
        if not account or not account.get('userid'):
            mb.showwarning("未选中账号", "请先在左侧账号列表选择账号！")
            return
        params = {
            'pageNo': 1,
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'openid': account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'source': '2'
        }
        result = get_order_list(params)
        self.order_tree.delete(*self.order_tree.get_children())
        if result.get('resultCode') == '0' and result.get('resultData'):
            orders = result['resultData'].get('orders', [])
            for idx, order in enumerate(orders, 1):
                film = order.get('orderName', '')
                cinema = order.get('cinemaName', '') if 'cinemaName' in order else ''
                status = order.get('orderS', '')
                orderno = order.get('orderno', '')
                self.order_tree.insert('', 'end', values=(film, cinema, status, orderno))
        else:
            mb.showinfo("无订单", result.get('resultDesc', '未查询到订单'))

    def on_order_double_click(self, event):
        item = self.order_tree.focus()
        if not item:
            return
        values = self.order_tree.item(item, 'values')
        if len(values) < 4:
            return
        film, cinema, status, orderno = values
        # 获取订单详情
        account = getattr(self, 'current_account', None)
        cinemaid = self.get_selected_cinemaid()
        if not account or not cinemaid:
            mb.showwarning("未选中账号或影院", "请先选择账号和影院！")
            return
        params = {
            'orderno': orderno,
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'openid': account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'source': '2'
        }
        detail = get_order_detail(params)
        # 获取二维码
        qrcode_img = get_order_qrcode_api(orderno, cinemaid)
        # 合成美观图片并展示
        self.show_order_qrcode_img(detail, qrcode_img)

    def show_order_qrcode_img(self, detail, qrcode_img_bytes):
        if not detail or detail.get('resultCode') != '0':
            mb.showerror("订单详情获取失败", detail.get('resultDesc', '未知错误'))
            return
        data = detail['resultData']
        film = data.get('filmName', '')
        show_time = data.get('showTime', '')
        hall = data.get('hallName', '')
        seat_info = data.get('seatInfo', '')
        ticket_code = data.get('ticketCode', '') or data.get('ticketcode', '')
        ds_code = data.get('dsValidateCode', '')
        orderno = data.get('orderno', '')
        mobile = data.get('orderMobile', '')
        cinema_name = data.get('cinemaName', '')
        pay_time = data.get('payTime', '')
        pay_amount = data.get('payAmount', 0)
        pay_amount_str = f"¥{int(pay_amount)/100:.2f}" if pay_amount else ""
        
        # 取当前月日
        try:
            if pay_time:
                dt = datetime.datetime.strptime(pay_time[:10], "%Y-%m-%d")
            else:
                dt = datetime.datetime.now()
            month_day = dt.strftime("%m%d")
        except:
            month_day = datetime.datetime.now().strftime("%m%d")
        
        # 影院名去除特殊字符
        cinema_name_safe = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', cinema_name)
        img_filename = f"{cinema_name_safe}_{month_day}_{orderno}.png"
        
        # 优化图片尺寸和布局 - 减少留白，提升观感
        width, height = 320, 420
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font_title = ImageFont.truetype("msyh.ttc", 18)  # 标题稍大
            font_text = ImageFont.truetype("msyh.ttc", 12)   # 正文适中 
            font_code = ImageFont.truetype("msyh.ttc", 15)   # 取票码突出
            font_small = ImageFont.truetype("msyh.ttc", 10)  # 小字体
        except:
            font_title = font_text = font_code = font_small = None
        
        # 减少顶部边距
        y = 8
        
        # 电影名称（标题，加粗效果）
        draw.text((12, y), film, fill='black', font=font_title)
        y += 26
        
        # 场次时间
        draw.text((12, y), show_time, fill='#555', font=font_text)
        y += 18
        
        # 影厅和座位信息
        draw.text((12, y), f"{hall}  {seat_info}", fill='#555', font=font_text)
        y += 22
        
        # 取票分割线（减少间距）
        draw.line((12, y, width-12, y), fill='#ddd', width=1)
        y += 8
        draw.text((12, y), "取票", fill='black', font=font_text)
        y += 16
        
        # 二维码居中显示（增大尺寸）
        qr_size = 140
        qr_x = int((width - qr_size) / 2)
        if qrcode_img_bytes:
            try:
                qrcode = Image.open(io.BytesIO(qrcode_img_bytes)).resize((qr_size, qr_size))
                img.paste(qrcode, (qr_x, y))
            except Exception:
                # 如果二维码加载失败，绘制占位图
                draw.rectangle([qr_x, y, qr_x + qr_size, y + qr_size], outline='#ccc', width=2)
                draw.text((qr_x + qr_size//2 - 20, y + qr_size//2 - 6), "二维码", fill='#999', font=font_text)
        y += qr_size + 6
        
        # 取票码（橙色高亮，居中，减少间距）
        if ds_code:
            code_text = f"取票码：{ds_code}"
            try:
                code_w = draw.textlength(code_text, font=font_code)
            except:
                code_w = len(code_text) * 10
            draw.text(((width - code_w) // 2, y), code_text, fill='#ff6600', font=font_code)
            y += 20
        
        # 提示文字（缩小字体，减少间距）
        tip_text = "请到自助取票机扫描上述二维码取票"
        try:
            tip_w = draw.textlength(tip_text, font=font_small)
        except:
            tip_w = len(tip_text) * 6
        draw.text(((width - tip_w) // 2, y), tip_text, fill='#999', font=font_small)
        y += 18
        
        # 订单详情分割线（减少间距）
        draw.line((12, y, width-12, y), fill='#ddd', width=1)
        y += 8
        draw.text((12, y), "订单详情", fill='black', font=font_text)
        y += 16
        
        # 订单信息（紧凑布局，减少行间距）
        line_height = 15
        
        # 实付金额
        if pay_amount_str:
            draw.text((12, y), f"实付金额：{pay_amount_str}", fill='#333', font=font_text)
            y += line_height
        
        # 影院名称
        # 如果影院名太长，截断显示
        cinema_display = cinema_name[:15] + "..." if len(cinema_name) > 15 else cinema_name
        draw.text((12, y), f"影院名称：{cinema_display}", fill='#333', font=font_text)
        y += line_height
        
        # 手机号码
        if mobile:
            draw.text((12, y), f"手机号码：{mobile}", fill='#333', font=font_text)
            y += line_height
        
        # 订单号（分行显示，避免过长）
        if orderno:
            if len(orderno) > 16:
                draw.text((12, y), f"订单号：{orderno[:16]}", fill='#333', font=font_text)
                y += line_height
                draw.text((12, y), f"        {orderno[16:]}", fill='#333', font=font_text)
            else:
                draw.text((12, y), f"订单号：{orderno}", fill='#333', font=font_text)
            y += line_height
        
        # 购买时间
        if pay_time:
            draw.text((12, y), f"购买时间：{pay_time}", fill='#333', font=font_text)
        
        # 保存图片到data/img
        img_dir = os.path.join('data', 'img')
        os.makedirs(img_dir, exist_ok=True)
        img_path = os.path.abspath(os.path.join(img_dir, img_filename))
        img.save(img_path)
        self._last_qrcode_img_path = img_path
        self._last_qrcode_img_pil = img
        
        # 取票码区顶部按钮（始终显示）
        if not hasattr(self, 'qrcode_btn_frame') or not self.qrcode_btn_frame.winfo_ismapped():
            if hasattr(self, 'qrcode_btn_frame'):
                self.qrcode_btn_frame.destroy()
            self.qrcode_btn_frame = tk.Frame(self.qrcode_frame)
            self.qrcode_btn_frame.pack(side=tk.TOP, fill=tk.X, pady=(2,4))
            self.copy_path_btn = tk.Button(self.qrcode_btn_frame, text="复制路径", command=self.copy_qrcode_img_path)
            self.copy_path_btn.pack(side=tk.LEFT, padx=2)
            self.copy_img_btn = tk.Button(self.qrcode_btn_frame, text="复制图片", command=self.copy_qrcode_img_to_clipboard)
            self.copy_img_btn.pack(side=tk.LEFT, padx=2)
        
        # 清除之前的图片显示
        for widget in self.qrcode_frame.winfo_children():
            if widget != self.qrcode_btn_frame:
                widget.destroy()
        
        # 重新创建图片显示标签，使用滚动显示
        canvas = tk.Canvas(self.qrcode_frame, bg='white')
        scrollbar = tk.Scrollbar(self.qrcode_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 创建可滚动的frame
        scrollable_frame = tk.Frame(canvas, bg='white')
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # 将图片放在可滚动frame中
        img_tk = ImageTk.PhotoImage(img)
        img_label = tk.Label(scrollable_frame, image=img_tk, bg='white')
        img_label.image = img_tk  # 保持引用
        img_label.pack(pady=2)
        
        # 包装布局
        canvas.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        scrollbar.pack(side="right", fill="y")

    def copy_qrcode_img_path(self):
        if hasattr(self, '_last_qrcode_img_path'):
            self.clipboard_clear()
            self.clipboard_append(self._last_qrcode_img_path)
            # 移除弹窗提示

    def copy_qrcode_img_to_clipboard(self):
        if hasattr(self, '_last_qrcode_img_pil'):
            try:
                import win32clipboard
                from PIL import Image
                import io
                output = io.BytesIO()
                self._last_qrcode_img_pil.convert('RGB').save(output, 'BMP')
                data = output.getvalue()[14:]
                output.close()
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                # 移除弹窗提示
            except Exception as e:
                mb.showerror("复制失败", f"图片复制失败: {e}")

    def on_one_click_pay(self):
        """一键支付功能"""
        if not self.current_order:
            MessageManager.show_warning(self, "提示", "请先下单")
            return
            
        # 获取当前账号和影院信息
        account = getattr(self, 'current_account', None)
        cinemaid = self.get_selected_cinemaid()
        if not account or not cinemaid:
            MessageManager.show_warning(self, "支付失败", "请先选择账号和影院")
            return
            
        # 获取订单信息
        order_data = self.current_order.get('resultData', {})
        orderno = order_data.get('orderno', '')
        if not orderno:
            MessageManager.show_warning(self, "支付失败", "无效的订单号")
            return
            
        # 获取选中的券号
        selected_coupons = getattr(self, 'selected_coupons', [])
        couponcode = ','.join(selected_coupons) if selected_coupons else ''
        
        # 获取券选择后的价格信息
        coupon_info = getattr(self, 'current_coupon_info', None)
        
        # 判断是否使用券支付
        use_coupon = bool(couponcode and coupon_info and coupon_info.get('resultCode') == '0')
        
        if use_coupon:
            # 使用券支付：从券价格信息中获取支付参数
            coupon_data = coupon_info['resultData']
            pay_amount = coupon_data.get('paymentAmount', '0')  # 实付金额
            discount_price = coupon_data.get('discountprice', '0')  # 优惠价格
            
            # 检查会员支付金额
            is_member = self.member_info and self.member_info.get('is_member')
            if is_member:
                mem_payment = coupon_data.get('mempaymentAmount', '0')
                if mem_payment != '0':
                    pay_amount = mem_payment  # 会员优先使用会员支付金额
            
            print(f"[一键支付] 使用券支付，券号: {couponcode}")
            print(f"[一键支付] 实付金额: {pay_amount}分，优惠: {discount_price}分")
        else:
            # 不使用券，按原价支付
            couponcode = ''  # 清空券号
            
            # 获取原价支付金额
            is_member = self.member_info and self.member_info.get('is_member')
            if is_member:
                # 会员：使用会员总价
                pay_amount = str(order_data.get('mem_totalprice', 0))  # 会员总价（分）
            else:
                # 非会员：使用订单总价
                pay_amount = str(order_data.get('payAmount', 0))  # 订单总价（分）
            
            discount_price = '0'  # 无优惠
            
            print(f"[一键支付] 不使用券，按原价支付")
            print(f"[一键支付] 支付金额: {pay_amount}分（{'会员价' if is_member else '原价'}）")
        
        # 构建支付参数
        pay_params = {
            'orderno': orderno,
            'payprice': pay_amount,  # 实付金额
            'discountprice': discount_price,  # 优惠价格
            'couponcodes': couponcode,  # 券号列表（可为空）
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'openid': account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'source': '2'
        }
        
        print(f"[一键支付] 支付参数: {pay_params}")
        print(f"[一键支付] 正在支付订单: {orderno}")
        
        try:
            # 调用支付接口
            from services.order_api import pay_order
            pay_result = pay_order(pay_params)
            
            print(f"[一键支付] 支付结果: {pay_result}")
            
            if pay_result and pay_result.get('resultCode') == '0':
                # 支付成功，设置UI状态
                self.ui_state = "payment_success"
                print(f"[支付成功] 状态更新为: {self.ui_state}")
                
                # 不显示支付成功弹窗，直接获取订单详情和二维码
                try:
                    # 1. 获取已支付订单详情
                    from services.order_api import get_order_detail, get_order_qrcode_api
                    
                    detail_params = {
                        'orderno': orderno,
                        'groupid': '',
                        'cinemaid': cinemaid,
                        'cardno': account.get('cardno', ''),
                        'userid': account['userid'],
                        'openid': account['openid'],
                        'CVersion': '3.9.12',
                        'OS': 'Windows',
                        'token': account['token'],
                        'source': '2'
                    }
                    
                    print(f"[支付成功] 正在获取订单详情: {orderno}")
                    order_detail = get_order_detail(detail_params)
                    
                    if order_detail and order_detail.get('resultCode') == '0':
                        print(f"[支付成功] 订单详情获取成功")
                        
                        # 2. 获取订单二维码
                        print(f"[支付成功] 正在获取订单二维码: {orderno}")
                        qrcode_img = get_order_qrcode_api(orderno, cinemaid)
                        
                        # 3. 显示订单详情和二维码
                        self.show_order_qrcode_img(order_detail, qrcode_img)
                        
                        # 4. 更新订单详情区域显示支付成功状态
                        self.current_order = order_detail
                        self.show_order_detail(order_detail)
                        
                        print(f"[支付成功] 订单二维码已显示在取票码区域")
                    else:
                        print(f"[支付成功] 获取订单详情失败: {order_detail}")
                        messagebox.showwarning("提示", "支付成功，但获取订单详情失败，请手动在订单列表中查看")
                        
                        # 清空当前订单显示
                        self.current_order = None
                        self.show_order_detail({'resultCode': '0', 'resultData': {}})
                        
                except Exception as e:
                    print(f"[支付成功] 获取订单详情异常: {e}")
                    messagebox.showwarning("提示", f"支付成功，但获取订单详情时发生错误: {e}")
                    
                    # 清空当前订单显示
                    self.current_order = None
                    self.show_order_detail({'resultCode': '0', 'resultData': {}})
            else:
                error_msg = pay_result.get('resultDesc', '未知错误') if pay_result else '支付请求失败'
                messagebox.showerror("支付失败", f"支付失败: {error_msg}")
                
        except Exception as e:
             print(f"[一键支付] 支付异常: {e}")
             messagebox.showerror("支付失败", f"支付过程中发生错误: {e}")

    def build_cinema_management_tab(self, tab):
        """构建影院管理tab"""
        # 顶部操作按钮区
        top_frame = tk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=4, padx=8)
        
        refresh_btn = tk.Button(top_frame, text="刷新影院列表", width=12, command=self.refresh_cinema_list)
        refresh_btn.pack(side=tk.LEFT, padx=4)
        
        add_btn = tk.Button(top_frame, text="添加影院", width=10, command=self.add_cinema, bg="#4caf50", fg="#fff")
        add_btn.pack(side=tk.LEFT, padx=4)
        
        delete_btn = tk.Button(top_frame, text="删除影院", width=10, command=self.delete_cinema, bg="#f44336", fg="#fff")
        delete_btn.pack(side=tk.LEFT, padx=4)
        
        # 分隔线
        separator = ttk.Separator(tab, orient='horizontal')
        separator.pack(fill=tk.X, pady=4, padx=8)
        
        # 影院列表表格
        columns = ("影院名称", "影院ID", "地址", "状态")
        
        # 设置表格样式
        style = ttk.Style()
        style.configure("Cinema.Treeview", font=("微软雅黑", 11), rowheight=32)
        style.configure("Cinema.Treeview.Heading", font=("微软雅黑", 12, "bold"))
        
        # 创建表格容器
        table_frame = tk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # 创建表格
        self.cinema_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, style="Cinema.Treeview")
        
        # 设置列标题和宽度
        for col in columns:
            self.cinema_tree.heading(col, text=col)
            if col == "影院名称":
                self.cinema_tree.column(col, width=300, anchor="w")
            elif col == "影院ID":
                self.cinema_tree.column(col, width=150, anchor="center")
            elif col == "地址":
                self.cinema_tree.column(col, width=400, anchor="w")
            else:  # 状态
                self.cinema_tree.column(col, width=100, anchor="center")
        
        # 滚动条
        cinema_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.cinema_tree.yview)
        self.cinema_tree.configure(yscrollcommand=cinema_scrollbar.set)
        
        # 布局
        self.cinema_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cinema_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件
        self.cinema_tree.bind('<Double-1>', self.on_cinema_double_click)
        
        # 添加右键菜单
        self.cinema_context_menu = tk.Menu(self.cinema_tree, tearoff=0)
        self.cinema_context_menu.add_command(label="编辑影院", command=self.edit_cinema)
        self.cinema_context_menu.add_command(label="刷新影院信息", command=self.refresh_cinema_info)
        self.cinema_context_menu.add_command(label="删除影院", command=self.delete_cinema)
        self.cinema_context_menu.add_separator()
        self.cinema_context_menu.add_command(label="复制影院ID", command=self.copy_cinema_id)
        self.cinema_tree.bind('<Button-3>', self.show_cinema_context_menu)
        
        # 初始加载影院列表
        self.refresh_cinema_list()

    def refresh_cinema_list(self):
        """刷新影院列表"""
        try:
            # 清空现有数据
            self.cinema_tree.delete(*self.cinema_tree.get_children())
            
            # 从cinema_select_panel获取影院数据
            if hasattr(self.cinema_panel, 'cinemas') and self.cinema_panel.cinemas:
                for cinema in self.cinema_panel.cinemas:
                    # 修复字段映射：cinemas.json中使用name字段，不是cinemaname
                    cinema_name = cinema.get('name', cinema.get('cinemaname', '未知影院'))
                    cinema_id = cinema.get('cinemaid', '')
                    # 使用base_url作为地址信息，或者address字段（如果有）
                    address = cinema.get('address', cinema.get('base_url', '地址未知'))
                    status = "正常"  # 默认状态
                    
                    self.cinema_tree.insert('', 'end', values=(cinema_name, cinema_id, address, status))
                    
                print(f"[影院管理] 已加载 {len(self.cinema_panel.cinemas)} 个影院")
            else:
                # 如果没有影院数据，插入提示行
                self.cinema_tree.insert('', 'end', values=("暂无影院数据", "请先在影院/券tab中选择影院", "", ""))
                print("[影院管理] 暂无影院数据")
                
        except Exception as e:
            print(f"[影院管理] 刷新影院列表异常: {e}")
            messagebox.showerror("刷新失败", f"刷新影院列表时发生错误: {e}")

    def add_cinema(self):
        """添加影院对话框 - 简化版本：输入API域名和影院ID"""
        # 创建添加影院的对话框
        dialog = tk.Toplevel(self)
        dialog.title("添加影院")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 输入框架
        input_frame = tk.Frame(dialog, padx=20, pady=20)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # API域名输入
        tk.Label(input_frame, text="API域名：", font=("微软雅黑", 12)).grid(row=0, column=0, sticky="w", pady=8)
        domain_entry = tk.Entry(input_frame, width=40, font=("微软雅黑", 11))
        domain_entry.grid(row=0, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        # 影院ID输入
        tk.Label(input_frame, text="影院ID：", font=("微软雅黑", 12)).grid(row=1, column=0, sticky="w", pady=8)
        id_entry = tk.Entry(input_frame, width=40, font=("微软雅黑", 11))
        id_entry.grid(row=1, column=1, padx=(10, 0), pady=8, sticky="ew")
        
        # 状态显示标签
        status_label = tk.Label(input_frame, text="", font=("微软雅黑", 10))
        status_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=4)
        
        # 按钮框架
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 配置列权重
        input_frame.columnconfigure(1, weight=1)
        
        def validate_and_add():
            # 获取输入的域名和ID
            domain = domain_entry.get().strip()
            cinema_id = id_entry.get().strip()
            
            if not domain:
                messagebox.showwarning("输入错误", "请输入API域名！")
                return
                
            if not cinema_id:
                messagebox.showwarning("输入错误", "请输入影院ID！")
                return
            
            # 显示验证中状态
            status_label.config(text=f"正在验证影院ID ({domain})...", fg="blue")
            dialog.update()
            
            try:
                # 使用指定域名验证影院ID
                from services.cinema_info_api import get_cinema_info, format_cinema_data
                
                print(f"[添加影院] 使用指定域名验证: {domain}")
                cinema_info = get_cinema_info(domain, cinema_id)
                
                if cinema_info:
                    # 验证成功，格式化影院数据
                    cinema_data = format_cinema_data(cinema_info, domain, cinema_id)  # 传入原始影院ID
                    
                    # 检查是否已存在
                    from services.cinema_manager import cinema_manager
                    existing = cinema_manager.get_cinema_by_id(cinema_id)
                    if existing:
                        messagebox.showerror("添加失败", f"影院ID {cinema_id} 已存在")
                        return
                    
                    # 添加到影院列表
                    cinemas = cinema_manager.load_cinema_list()
                    cinemas.append(cinema_data)
                    
                    if cinema_manager.save_cinema_list(cinemas):
                        cinema_name = cinema_data.get('cinemaShortName', '未知影院')
                        city_name = cinema_data.get('cityName', '未知城市')
                        
                        status_label.config(text=f"验证成功：{cinema_name} ({city_name})", fg="green")
                        dialog.update()
                        
                        # 更新界面
                        self.refresh_cinema_dropdown()
                        self.refresh_cinema_list()
                        
                        messagebox.showinfo("添加成功", 
                                          f"影院添加成功！\n"
                                          f"影院名称：{cinema_name}\n"
                                          f"所在城市：{city_name}\n"
                                          f"API域名：{domain}\n"
                                          f"影院地址：{cinema_data.get('cinemaAddress', '地址未知')}")
                        dialog.destroy()
                    else:
                        messagebox.showerror("添加失败", "保存影院信息失败")
                else:
                    # 验证失败
                    status_label.config(text=f"验证失败：影院ID在域名 {domain} 中不存在", fg="red")
                    messagebox.showerror("添加失败", f"影院ID在域名 {domain} 中不存在")
                    
            except Exception as e:
                print(f"[添加影院] 异常: {e}")
                status_label.config(text=f"验证异常：{e}", fg="red")
                messagebox.showerror("添加失败", f"添加影院时发生错误：{e}")
        
        def cancel_add():
            dialog.destroy()
        
        # 按钮
        save_btn = tk.Button(button_frame, text="验证并添加", command=validate_and_add, 
                           bg="#4caf50", fg="#fff", font=("微软雅黑", 11), width=12)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="取消", command=cancel_add, 
                             bg="#f44336", fg="#fff", font=("微软雅黑", 11), width=10)
        cancel_btn.pack(side=tk.LEFT)
        
        # 让API域名输入框获得焦点
        domain_entry.focus_set()
        
        # 绑定回车键
        domain_entry.bind('<Return>', lambda e: id_entry.focus_set())
        id_entry.bind('<Return>', lambda e: validate_and_add())
    
    def refresh_cinema_dropdown(self):
        """刷新影院选择下拉框"""
        try:
            # 重新加载影院数据
            from services.film_service import load_cinemas
            self.cinema_panel.cinemas = load_cinemas()
            
            # 更新下拉框选项
            if hasattr(self.cinema_panel, 'cinema_combo'):
                cinema_names = [c.get('name', c.get('cinemaShortName', '未知影院')) for c in self.cinema_panel.cinemas]
                self.cinema_panel.cinema_combo['values'] = cinema_names
                print(f"[影院下拉框] 已更新，共 {len(cinema_names)} 个影院")
        except Exception as e:
            print(f"[影院下拉框] 刷新失败: {e}")

    def delete_cinema(self):
        """删除选中的影院 - 使用新的影院管理器"""
        selection = self.cinema_tree.selection()
        if not selection:
            messagebox.showwarning("删除影院", "请先选择要删除的影院！")
            return
            
        item = selection[0]
        values = self.cinema_tree.item(item, 'values')
        if len(values) < 2:
            return
            
        cinema_name, cinema_id = values[0], values[1]
        
        # 确认删除
        result = messagebox.askyesno("确认删除", f"确定要删除影院 '{cinema_name}' 吗？\n影院ID：{cinema_id}")
        if not result:
            return
            
        try:
            # 使用新的影院管理器删除影院
            from services.cinema_manager import cinema_manager
            success, message = cinema_manager.delete_cinema_by_id(cinema_id)
            
            if success:
                # 删除成功，更新界面
                self.refresh_cinema_dropdown()
                self.refresh_cinema_list()
                messagebox.showinfo("删除成功", f"影院 '{cinema_name}' 已删除！")
            else:
                messagebox.showerror("删除失败", f"删除失败：{message}")
                
        except Exception as e:
            print(f"[影院管理] 删除影院异常: {e}")
            messagebox.showerror("删除失败", f"删除影院时发生错误: {e}")

    def edit_cinema(self):
        """编辑选中的影院"""
        selection = self.cinema_tree.selection()
        if not selection:
            messagebox.showwarning("编辑影院", "请先选择要编辑的影院！")
            return
            
        # 暂时显示提示，功能待实现
        messagebox.showinfo("功能提示", "编辑影院功能正在开发中...")

    def copy_cinema_id(self):
        """复制影院ID到剪贴板"""
        selection = self.cinema_tree.selection()
        if not selection:
            messagebox.showwarning("复制影院ID", "请先选择影院！")
            return
            
        item = selection[0]
        values = self.cinema_tree.item(item, 'values')
        if len(values) >= 2:
            cinema_id = values[1]
            self.clipboard_clear()
            self.clipboard_append(cinema_id)
            messagebox.showinfo("复制成功", f"影院ID '{cinema_id}' 已复制到剪贴板！")

    def show_cinema_context_menu(self, event):
        """显示影院右键菜单"""
        # 选择点击的行
        item = self.cinema_tree.identify_row(event.y)
        if item:
            self.cinema_tree.selection_set(item)
            self.cinema_context_menu.post(event.x_root, event.y_root)

    def on_cinema_double_click(self, event):
        """双击影院行的处理"""
        selection = self.cinema_tree.selection()
        if not selection:
            return
            
        item = selection[0]
        values = self.cinema_tree.item(item, 'values')
        if len(values) >= 2:
            cinema_name, cinema_id = values[0], values[1]
            
            # 在影院选择下拉框中选中这个影院
            if hasattr(self.cinema_panel, 'cinema_combo'):
                try:
                    # 找到对应的影院索引
                    for i, cinema in enumerate(self.cinema_panel.cinemas):
                        if cinema.get('cinemaid') == cinema_id:
                            self.cinema_panel.cinema_combo.current(i)
                            self.cinema_panel.on_cinema_select(None)  # 触发影院选择事件
                            messagebox.showinfo("影院切换", f"已切换到影院：{cinema_name}")
                            break
                except Exception as e:
                    print(f"[影院管理] 切换影院异常: {e}")

    def refresh_cinema_info(self):
        """刷新选中影院的信息（从API重新获取）"""
        selection = self.cinema_tree.selection()
        if not selection:
            messagebox.showwarning("刷新影院信息", "请先选择要刷新的影院！")
            return
            
        item = selection[0]
        values = self.cinema_tree.item(item, 'values')
        if len(values) < 2:
            return
            
        cinema_name, cinema_id = values[0], values[1]
        
        try:
            # 使用新的影院管理器刷新影院信息
            from services.cinema_manager import cinema_manager
            success, result = cinema_manager.refresh_cinema_info(cinema_id)
            
            if success:
                # 刷新成功
                updated_cinema = result
                new_name = updated_cinema.get('cinemaShortName', '未知影院')
                city_name = updated_cinema.get('cityName', '未知城市')
                
                # 更新界面
                self.refresh_cinema_dropdown()
                self.refresh_cinema_list()
                
                messagebox.showinfo("刷新成功", 
                                  f"影院信息已更新！\n"
                                  f"影院名称：{new_name}\n"
                                  f"所在城市：{city_name}\n"
                                  f"影院地址：{updated_cinema.get('cinemaAddress', '地址未知')}")
            else:
                error_msg = result
                messagebox.showerror("刷新失败", f"刷新失败：{error_msg}")
                
        except Exception as e:
            print(f"[影院管理] 刷新影院信息异常: {e}")
            messagebox.showerror("刷新失败", f"刷新影院信息时发生错误: {e}")

    def build_coupon_exchange_tab(self, tab):
        """构建兑换券tab - 显示当前账号的券列表"""
        # 顶部控制区
        top_frame = tk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=4, padx=8)
        
        # 刷新按钮
        self.exchange_refresh_btn = tk.Button(top_frame, text="刷新", width=8, command=self.refresh_coupon_exchange_list)
        self.exchange_refresh_btn.pack(side=tk.LEFT, padx=4)
        
        # 有效期统计标签
        self.coupon_stats_label = tk.Label(top_frame, text="", font=("微软雅黑", 10), fg="blue")
        self.coupon_stats_label.pack(side=tk.LEFT, padx=(20, 4))
        
        # 当前账号信息
        self.exchange_account_info = tk.Label(top_frame, text="当前账号：未选择", font=("微软雅黑", 10), fg="red")
        self.exchange_account_info.pack(side=tk.RIGHT, padx=4)
        
        # 券列表区域
        # 使用与下单后券列表相同的样式
        self.exchange_coupon_listbox = tk.Listbox(tab, selectmode="single", font=("微软雅黑", 10), activestyle="dotbox")
        self.exchange_coupon_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        
        # 保存券数据
        self.exchange_coupons_data = []
        
        # 初始更新账号信息
        self.update_exchange_account_info()
    
    def update_exchange_account_info(self):
        """更新兑换券界面的账号信息显示"""
        account = getattr(self, 'current_account', None)
        if hasattr(self, 'exchange_account_info'):
            if account:
                # 获取影院名称
                cinema_name = "未知影院"
                try:
                    from services.cinema_manager import cinema_manager
                    cinemas = cinema_manager.load_cinema_list()
                    for cinema in cinemas:
                        if cinema.get('cinemaid') == account.get('cinemaid'):
                            cinema_name = cinema.get('cinemaShortName', '未知影院')
                            break
                except:
                    pass
                
                info_text = f"当前账号：{account['userid']} @ {cinema_name} (余额:{account.get('balance', 0)} 积分:{account.get('score', 0)})"
                self.exchange_account_info.config(text=info_text, fg="blue")
            else:
                self.exchange_account_info.config(text="请先选择账号和影院", fg="red")
    
    def refresh_coupon_exchange_list(self):
        """刷新兑换券列表"""
        # 防重复调用机制
        if hasattr(self, '_refreshing_exchange_coupons') and self._refreshing_exchange_coupons:
            print("[兑换券刷新] 已有刷新请求在进行中，跳过重复请求")
            return
        
        account = getattr(self, 'current_account', None)
        cinemaid = self.get_selected_cinemaid()
        
        if not account:
            messagebox.showwarning("未选中账号", "请先在左侧账号列表选择账号！")
            return
        
        if not cinemaid:
            messagebox.showwarning("未选中影院", "请先选择影院！")
            return
        
        # 设置刷新状态标志
        self._refreshing_exchange_coupons = True
        
        # 禁用刷新按钮并更改文本
        if hasattr(self, 'exchange_refresh_btn'):
            self.exchange_refresh_btn.config(state="disabled", text="刷新中...")
        
        # 显示刷新状态
        if hasattr(self, 'coupon_stats_label'):
            self.coupon_stats_label.config(text="正在获取券列表...", fg="orange")
        
        # 构建请求参数 - 确保只请求当前选择的影院和账号
        params = {
            'voucherType': -1,  # -1表示获取所有类型券
            'pageNo': 1,
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'openid': account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'source': '2'
        }
        
        print(f"[兑换券刷新] 正在获取账号 {account['userid']} @ 影院 {cinemaid} 的券列表...")
        
        try:
            from services.order_api import get_coupon_list
            result = get_coupon_list(params)
            
            print(f"[兑换券刷新] 券列表结果: {result}")
            
            if result.get('resultCode') == '0':
                self.update_exchange_coupon_list(result)
                print(f"[兑换券刷新] 成功获取券列表")
            else:
                error_desc = result.get('resultDesc', '未知错误')
                print(f"[兑换券刷新] 获取券列表失败: {error_desc}")
                messagebox.showwarning("获取券列表失败", f"获取失败：{error_desc}")
                self.clear_exchange_coupon_list()
                
        except Exception as e:
            print(f"[兑换券刷新] 异常: {e}")
            messagebox.showerror("获取券列表异常", f"获取券列表时发生错误: {e}")
            self.clear_exchange_coupon_list()
        finally:
            # 无论成功失败都要恢复按钮状态和清除刷新状态标志
            self._refreshing_exchange_coupons = False
            if hasattr(self, 'exchange_refresh_btn'):
                self.exchange_refresh_btn.config(state="normal", text="刷新")
            print(f"[兑换券刷新] 刷新完成，重置状态标志")
    
    def update_exchange_coupon_list(self, coupon_result):
        """更新兑换券列表显示"""
        # 清空现有列表
        self.exchange_coupon_listbox.delete(0, 'end')
        self.exchange_coupons_data = []
        
        if not coupon_result or coupon_result.get('resultCode') != '0':
            self.exchange_coupon_listbox.insert('end', '获取券列表失败')
            self.coupon_stats_label.config(text="")
            return
        
        # 获取券数据 - 适配不同的数据结构
        coupon_data = coupon_result.get('resultData', {})
        vouchers = coupon_data.get('vouchers', []) or coupon_data.get('coupons', []) or coupon_data.get('data', [])
        
        if not vouchers:
            self.exchange_coupon_listbox.insert('end', '暂无可用优惠券')
            self.coupon_stats_label.config(text="券数量：0张")
            return
        
        # 过滤券：只保留未使用且未过期的券
        valid_vouchers = []
        total_count = len(vouchers)
        used_count = 0
        expired_count = 0
        
        for voucher in vouchers:
            # 检查是否已使用 (redeemed=1表示已使用)
            is_used = str(voucher.get('redeemed', '0')) == '1'
            # 检查是否已过期 (expired=1表示已过期)
            is_expired = str(voucher.get('expired', '0')) == '1'
            
            if is_used:
                used_count += 1
            elif is_expired:
                expired_count += 1
            else:
                # 未使用且未过期的券
                valid_vouchers.append(voucher)
        
        if not valid_vouchers:
            self.exchange_coupon_listbox.insert('end', '暂无可用优惠券')
            self.coupon_stats_label.config(text=f"总券数：{total_count}张 (已使用:{used_count}张, 已过期:{expired_count}张, 可用:0张)")
            return
        
        # 按有效期分组统计
        expire_stats = {}
        
        for voucher in valid_vouchers:
            # 获取有效期 - 尝试多个字段
            expire_date = voucher.get('expireddate') or voucher.get('expiredDate') or voucher.get('expire_date', '未知')
            
            # 统计
            if expire_date != '未知':
                expire_key = expire_date.split(' ')[0]  # 只取日期部分
                expire_stats[expire_key] = expire_stats.get(expire_key, 0) + 1
        
        # 按有效期升序排列券
        valid_vouchers.sort(key=lambda v: v.get('expireddate', ''))
        
        # 显示券列表
        for i, voucher in enumerate(valid_vouchers):
            # 获取券信息
            name = voucher.get('couponname') or voucher.get('voucherName') or voucher.get('name', f'券{i+1}')
            expire = voucher.get('expireddate') or voucher.get('expiredDate') or '未知'
            code = voucher.get('couponcode') or voucher.get('voucherCode') or voucher.get('code', f'未知券号{i+1}')
            
            # 格式化显示
            display = f"{name} | 有效期至 {expire} | 券号 {code}"
            self.exchange_coupon_listbox.insert('end', display)
            self.exchange_coupons_data.append(voucher)
        
        # 生成统计文本
        if expire_stats:
            stats_items = []
            for expire_date in sorted(expire_stats.keys()):
                count = expire_stats[expire_date]
                stats_items.append(f"{expire_date}到期{count}张")
            stats_text = f"可用券：{len(valid_vouchers)}张 ({' '.join(stats_items)}) | 总计:{total_count}张 (已用:{used_count}张, 过期:{expired_count}张)"
        else:
            stats_text = f"可用券：{len(valid_vouchers)}张 | 总计:{total_count}张 (已用:{used_count}张, 过期:{expired_count}张)"
        
        self.coupon_stats_label.config(text=stats_text)
        print(f"[兑换券列表] 更新完成，总计 {total_count} 张券，可用 {len(valid_vouchers)} 张券，已使用 {used_count} 张，已过期 {expired_count} 张")
    
    def clear_exchange_coupon_list(self):
        """清空兑换券列表"""
        if hasattr(self, 'exchange_coupon_listbox'):
            self.exchange_coupon_listbox.delete(0, 'end')
            self.exchange_coupon_listbox.insert('end', '暂无券数据')
        if hasattr(self, 'coupon_stats_label'):
            self.coupon_stats_label.config(text="")
        self.exchange_coupons_data = []

    def on_seat_selection_changed(self, selected_seats):
        """座位选择变化回调"""
        if self.show_debug:
            print(f"[UI状态] 座位选择变化，已选座位: {len(selected_seats)}")
        
        # 选座操作不改变UI状态，不清空券列表
        # 保持当前的ui_state不变

if __name__ == "__main__":  # 程序入口
    app = CinemaOrderSimulatorUI()  # 创建主窗口对象
    app.mainloop()  # 进入主事件循环，显示窗口