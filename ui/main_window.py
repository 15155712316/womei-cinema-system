import tkinter as tk  # 导入tkinter库，tk是Python自带的GUI库
from tkinter import ttk, messagebox  # 导入ttk（美化控件）和messagebox（弹窗）
from ui.login_panel import LoginPanel
from ui.account_list_panel import AccountListPanel
from ui.cinema_select_panel import CinemaSelectPanel
from ui.seat_map_panel import SeatMapPanel

class CinemaOrderSimulatorUI(tk.Tk):  # 定义主窗口类，继承自tk.Tk
    def __init__(self):  # 初始化方法
        super().__init__()  # 调用父类初始化
        self.title("柴犬影院下单系统")  # 设置窗口标题
        self.geometry("1250x750")  # 设置窗口大小
        self.configure(bg="#f8f8f8")  # 设置窗口背景色

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

        # 集成登录面板和账号列表面板
        self.login_panel = LoginPanel(self.login_frame)
        self.login_panel.pack(fill=tk.BOTH, expand=True)
        self.account_list_panel = AccountListPanel(self.account_list_frame)
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
        self.cinema_panel = CinemaSelectPanel(tab1_left)
        self.cinema_panel.pack(fill="both", expand=True)
        self.center_notebook.add(tab1, text="影院/券")
        # 其余tab: 全宽
        for i, name in enumerate(["出票", "账号", "绑券", "订单", "积分", "会员卡"]):
            tab = tk.Frame(self.center_notebook)
            self.center_notebook.add(tab, text=name)
        # 下部座位区
        center_bottom_frame = tk.LabelFrame(center_frame, text="座位区域", fg="red")
        center_bottom_frame.place(x=0, y=center_top_h, width=center_w, height=center_bottom_h)
        # 选座区 SeatMapPanel 只放在座位区域
        self.seat_panel = SeatMapPanel(center_bottom_frame, seat_data=[])
        self.seat_panel.pack(fill="both", expand=True, padx=10, pady=5)
        # 绑定场次选择事件
        self.cinema_panel.set_seat_panel(self.seat_panel)

        # ========== 右栏 ==========
        right_frame = tk.Frame(self, bg="#f0f0f0")
        right_frame.place(x=left_w+center_w, y=0, width=right_w, height=total_height)
        self.right_notebook = ttk.Notebook(right_frame)
        self.right_notebook.place(x=0, y=0, width=right_w, height=total_height)
        # 订单tab
        order_tab = tk.Frame(self.right_notebook)
        order_top_h = int(total_height * 0.66)
        order_bottom_h = total_height - order_top_h
        order_top = tk.LabelFrame(order_tab, text="订单取票码区", fg="red")
        order_top.place(x=0, y=0, width=right_w, height=order_top_h)
        order_bottom = tk.LabelFrame(order_tab, text="订单详情区", fg="red")
        order_bottom.place(x=0, y=order_top_h, width=right_w, height=order_bottom_h)
        self.right_notebook.add(order_tab, text="订单")
        # 用户tab
        user_tab = tk.Frame(self.right_notebook)
        user_top = tk.LabelFrame(user_tab, text="公告区", fg="red")
        user_top.place(x=0, y=0, width=right_w, height=order_top_h)
        user_bottom = tk.LabelFrame(user_tab, text="设备登录区", fg="red")
        user_bottom.place(x=0, y=order_top_h, width=right_w, height=order_bottom_h)
        self.right_notebook.add(user_tab, text="用户")

        # ========== 预留：后续可在各分区填充内容 ==========
        # self.login_frame, self.account_list_frame, tab1_left, tab1_right, center_bottom_frame, order_top, order_bottom, user_top, user_bottom
        # 都可以直接添加控件

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

if __name__ == "__main__":  # 程序入口
    app = CinemaOrderSimulatorUI()  # 创建主窗口对象
    app.mainloop()  # 进入主事件循环，显示窗口