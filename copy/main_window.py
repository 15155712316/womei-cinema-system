import tkinter as tk  # 导入tkinter库，tk是Python自带的GUI库
from tkinter import ttk, messagebox  # 导入ttk（美化控件）和messagebox（弹窗）
from ui.login_panel import LoginPanel
from ui.account_list_panel import AccountListPanel
from ui.cinema_select_panel import CinemaSelectPanel
from ui.seat_map_panel import SeatMapPanel
import json
from services.order_api import create_order, get_unpaid_order_detail, get_coupons_by_order
import tkinter.messagebox as mb

class CinemaOrderSimulatorUI(tk.Tk):  # 定义主窗口类，继承自tk.Tk
    def __init__(self):  # 初始化方法
        super().__init__()  # 调用父类初始化
        self.title("柴犬影院下单系统")  # 设置窗口标题
        self.geometry("1250x750")  # 设置窗口大小
        self.configure(bg="#f8f8f8")  # 设置窗口背景色
        self.last_priceinfo = {}

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
        self.login_panel = LoginPanel(
            self.login_frame,
            get_cinemaid_func=self.get_selected_cinemaid,
            refresh_account_list_func=self.refresh_account_list
        )
        self.login_panel.pack(fill=tk.BOTH, expand=True)
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
        self.cinema_panel.pack(fill="both", expand=True)
        # 券列表Listbox直接放到tab1_right，支持多选
        self.coupon_listbox = tk.Listbox(tab1_right, selectmode="multiple", font=("微软雅黑", 10), activestyle="dotbox")
        self.coupon_listbox.pack(fill="both", expand=True, padx=8, pady=8)
        self.coupons_data = []
        self.selected_coupons = []
        self.max_coupon_select = 1  # 默认最多可选1张券，后续由订单详情接口ticketcount动态赋值
        self.coupon_listbox.bind('<<ListboxSelect>>', self.on_coupon_select)
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
        self.seat_panel.set_account_getter(lambda: getattr(self, 'current_account', {}))
        self.seat_panel.set_on_submit_order(self.on_submit_order)
        # 绑定场次选择事件
        self.cinema_panel.set_seat_panel(self.seat_panel)

        # ========== 右栏 ==========
        right_frame = tk.Frame(self, bg="#f0f0f0")
        right_frame.place(x=left_w+center_w, y=0, width=right_w, height=total_height)
        # 右侧上下分布
        right_top = tk.Frame(right_frame, bg="#f0f0f0")
        right_top.place(x=0, y=0, width=right_w, height=total_height//2)
        right_bottom = tk.Frame(right_frame, bg="#f0f0f0")
        right_bottom.place(x=0, y=total_height//2, width=right_w, height=total_height//2)
        # 先放二维码区在上
        self.qrcode_frame = tk.LabelFrame(right_top, text="取票码区", fg="red")
        self.qrcode_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        # 再放订单详情区在下
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
        self.orderinfo_countdown = tk.Label(self.orderinfo_frame, text="", fg="#0077ff", font=("微软雅黑", 10, "bold"))
        self.orderinfo_countdown.pack(anchor="w", padx=4, pady=(0,4))
        # 新增一键支付按钮
        self.pay_btn = tk.Button(self.orderinfo_frame, text="一键支付", bg="#ff9800", fg="#fff", font=("微软雅黑", 11, "bold"))
        self.pay_btn.pack(fill=tk.X, padx=4, pady=(0,4))

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

    def get_selected_cinemaid(self):
        # 获取影院选择区当前选中的cinemaid
        idx = self.cinema_panel.cinema_combo.current()
        if idx < 0:
            return None
        return self.cinema_panel.cinemas[idx]['cinemaid']

    def set_current_account(self, account):
        self.current_account = account
        self.cinema_panel.set_current_account(account)

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
        self.update_coupons(None)

    def refresh_coupons(self):
        # 账号Tab刷新券按钮逻辑，调用独立券接口（待开发），此处先清空券列表
        self.update_coupons(None)
        messagebox.showinfo("刷新券", "已刷新券列表（接口待开发）")

    def refresh_account_list(self):
        try:
            with open("data/accounts.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)
        except Exception:
            accounts = []
        cinemaid = self.get_selected_cinemaid()
        filtered = [acc for acc in accounts if acc['cinemaid'] == cinemaid] if cinemaid else accounts
        # 优先高亮主账号
        main_idx = next((i for i, acc in enumerate(filtered) if acc.get('is_main')), 0)
        self.account_list_panel.update_accounts(filtered)
        if filtered:
            self.account_list_panel.tree.selection_set(self.account_list_panel.tree.get_children()[main_idx])
            self.set_current_account(filtered[main_idx])
        else:
            self.set_current_account(None)

    def on_cinema_changed(self):
        self.refresh_account_list()
        self.clear_coupons()

    def on_seat_selected(self, selected_seats):
        self.clear_coupons()

    def on_submit_order(self, selected_seats):
        self.clear_coupons()
        account = self.current_account
        cinema = self.cinema_panel.cinemas[self.cinema_panel.cinema_combo.current()]
        session = self.cinema_panel.current_sessions[self.cinema_panel.session_combo.current()]
        priceinfo = getattr(self, 'last_priceinfo', {})
        seat_info_list = []
        for seat in selected_seats:
            seat_info_list.append({
                "seatInfo": f"{seat['row']}排{seat['num']}座",
                "eventPrice": 0,
                "strategyPrice": int(float(priceinfo.get('proprice', 0))),
                "ticketPrice": int(float(priceinfo.get('proprice', 0))),
                "seatRow": int(seat['row']),
                "seatRowId": int(seat['row']),
                "seatCol": int(seat['cn']),
                "seatColId": int(seat['cn']),
                "seatNo": seat['sn'],
                "sectionId": seat.get('sectionId', '11111'),
                "ls": seat.get('ls', ''),
                "rowIndex": int(seat.get('rowIndex', 0)),
                "colIndex": int(seat.get('colIndex', 0)),
                "index": int(seat.get('index', 0))
            })
        seat_info_json = json.dumps(seat_info_list, ensure_ascii=False)
        params = {
            'groupid': '',
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'cinemaid': cinema['cinemaid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'openid': account['openid'],
            'source': '2',
            'oldOrderNo': '',
            'showTime': session['k'],
            'eventCode': '',
            'hallCode': session['j'],
            'showCode': session['g'],
            'filmCode': session.get('h', ''),
            'filmNo': session.get('fno', ''),
            'recvpPhone': '',
            'seatInfo': seat_info_json,
            'payType': 3,
            'companyChannelId': 5,
            'shareMemberId': '',
            'limitprocount': 0
        }
        try:
            result = create_order(params)
            if result.get('resultCode') == '0':
                orderno = result['resultData']['orderno']
                print("下单返回数据：", result)
                print("当前账号信息：", account)
                print("当前影院信息：", cinema)
                coupon_params = {
                    'orderno': orderno,
                    'cinemaid': cinema['cinemaid'],
                    'userid': account['userid'],
                    'openid': account['openid'],
                    'token': account['token'],
                    'CVersion': '3.9.12',
                    'OS': 'Windows',
                    'source': '2',
                    'pageNo': 1,
                    'getWay': 'new',
                    'voucherType': 'count',
                    'groupid': '',
                }
                print("即将请求优惠券参数：", coupon_params)
                coupon_result = get_coupons_by_order(coupon_params)
                print("[下单后可用优惠券接口返回]", coupon_result)
                # 查询订单详情
                detail_params = {
                    'orderno': orderno,
                    'groupid': '',
                    'cinemaid': cinema['cinemaid'],
                    'cardno': account.get('cardno', ''),
                    'userid': account['userid'],
                    'openid': account['openid'],
                    'CVersion': '3.9.12',
                    'OS': 'Windows',
                    'token': account['token'],
                    'source': '2'
                }
                detail = get_unpaid_order_detail(detail_params)
                ticketcount = 1
                if detail.get('resultCode') == '0':
                    ticketcount = detail['resultData'].get('ticketcount', 1)
                self.update_coupons(coupon_result, ticketcount)
                self.show_order_detail(detail)
            else:
                mb.showerror("下单失败", result.get('resultDesc', '未知错误'))
        except Exception as e:
            mb.showerror("网络错误", str(e))

    def show_order_detail(self, detail):
        self.orderinfo_text.config(state="normal")
        self.orderinfo_text.delete('1.0', 'end')
        self.orderinfo_mobile.config(text="")
        self.orderinfo_countdown.config(text="")
        if detail.get('resultCode') == '0':
            data = detail['resultData']
            # 手机号红色加粗
            mobile = data.get('orderMobile', '')
            self.orderinfo_mobile.config(text=f"手机号：{mobile}")
            # 座位
            seat_info = data.get('seatInfo', '')
            # 影片、时间、影厅
            film = data.get('filmName', '')
            show_time = data.get('showTime', '')
            hall = data.get('hallName', '')
            # 支付方式
            memprice = int(data.get('memprice', 0))
            mem_totalprice = int(data.get('mem_totalprice', 0))
            ticket_price = int(data.get('ticketPrice', 0))
            pay_amount = int(data.get('payAmount', 0))
            pay_strs = []
            if memprice > 0:
                pay_strs.append(f"会员支付：¥{memprice/100:.2f}")
                pay_strs.append(f"总会员支付：¥{mem_totalprice/100:.2f}")
            if ticket_price > 0:
                pay_strs.append(f"券支付：¥{ticket_price/100:.2f}")
            pay_strs.append(f"应付：¥{pay_amount/100:.2f}")
            pay_info = '\n'.join(pay_strs)
            # 订单超时时间
            timeout_ms = int(data.get('orderTimeOut', 0))
            self._order_timeout_left = timeout_ms // 1000
            self._order_timeout_active = True
            self._update_order_countdown()
            # 详情文本
            info = f"影片：{film}\n时间：{show_time}\n影厅：{hall}\n座位：{seat_info}\n{pay_info}\n状态：{data.get('orderStatusDesc', '')}\n"
            self.orderinfo_text.insert('end', info)
            self.orderinfo_text.config(state="disabled")
        else:
            self.orderinfo_text.insert('end', f"查询失败: {detail.get('resultDesc', '未知错误')}")
            self.orderinfo_text.config(state="disabled")

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
        self.coupon_listbox.delete(0, 'end')
        self.coupons_data = []
        self.selected_coupons = []
        self.max_coupon_select = int(ticketcount) if str(ticketcount).isdigit() else 1
        if not coupon_result or coupon_result.get('resultCode') != '0':
            self.coupon_listbox.insert('end', '无可用优惠券')
            return
        vouchers = coupon_result['resultData'].get('vouchers', [])
        vouchers.sort(key=lambda v: v.get('expireddate', ''))
        for v in vouchers:
            name = v.get('couponname', v.get('voucherName', ''))
            expire = v.get('expireddate', '')
            code = v.get('couponcode', v.get('voucherCode', ''))
            display = f"{name} | 有效期至 {expire} | 券号 {code}"
            self.coupon_listbox.insert('end', display)
            self.coupons_data.append(v)
        # 默认不选中
        self.selected_coupons = []

    def on_coupon_select(self, event):
        idxs = self.coupon_listbox.curselection()
        if len(idxs) > self.max_coupon_select:
            mb.showwarning("券选择超限", f"最多只能选择{self.max_coupon_select}张券，已超出座位数量！")
            # 取消最后一次多选
            for i in idxs[self.max_coupon_select:]:
                self.coupon_listbox.selection_clear(i)
            idxs = self.coupon_listbox.curselection()
        self.selected_coupons = [self.coupons_data[i] for i in idxs]

if __name__ == "__main__":  # 程序入口
    app = CinemaOrderSimulatorUI()  # 创建主窗口对象
    app.mainloop()  # 进入主事件循环，显示窗口