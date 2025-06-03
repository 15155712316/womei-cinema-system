import tkinter as tk

class SeatMapPanel(tk.Frame):
    """
    影院座位图UI组件（Canvas方案），每个座位为黑色边框矩形，支持可售/已售/选中状态，交互逻辑与原Button方案一致。
    """
    def __init__(self, master, seat_data=None, *args, **kwargs):
        """
        初始化座位图面板。
        参数：
            master: 父窗口对象
            seat_data: 二维座位数据列表
        """
        super().__init__(master, *args, **kwargs)
        self.seat_data = seat_data or []  # 二维座位数据
        self.selected_seats = set()       # 选中座位集合
        self._priceinfo = {}              # 当前价格信息
        self.account_getter = lambda: {}   # 获取账号信息的函数
        self._build_ui()

    def _build_ui(self):
        """
        构建座位图UI，包括Canvas和滚动条、底部提交订单按钮。
        """
        # 滚动区域
        self.canvas = tk.Canvas(self, bg="#fff", highlightthickness=0)
        self.scroll_x = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.seat_items = {}  # (r, c): (rect_id, text_id)
        self._draw_seats()
        # 新增：底部按钮区
        self.submit_btn = tk.Button(self, text="提交订单", font=("微软雅黑", 11, "bold"), fg="#333", command=self._on_submit_order_click)
        self.submit_btn.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    def _draw_seats(self):
        """
        绘制所有座位格子，根据状态显示不同颜色和交互。
        """
        self.canvas.delete("all")
        self.seat_items.clear()
        # 座位格子参数
        cell_w, cell_h = 32, 32
        pad_x, pad_y = 4, 4
        label_w = 16
        max_x, max_y = 0, 0
        
        for r, row in enumerate(self.seat_data):
            # 简化：直接使用基础间距，无需复杂的间距计算
            y = pad_y + r * (cell_h + pad_y)
            
            # 获取当前行的排号（直接从座位数据中读取）
            row_label = "?"
            for seat in row:
                if seat is not None:
                    row_label = str(seat.get('row', r+1))  # 使用seat中的row字段
                    break
            
            self.canvas.create_text(label_w//2, y + cell_h//2, text=row_label, font=("微软雅黑", 8, "bold"), fill="#333")
            
            for c, seat in enumerate(row):
                if seat is None:
                    continue
                cn = int(seat.get('cn', c+1))
                x = label_w + pad_x + (cn-1) * (cell_w + pad_x)
                num = seat.get('num', '')
                status = seat.get('status', 'available')
                if status == 'empty':
                    continue
                fill = self.get_bg(status)
                rect_id = self.canvas.create_rectangle(
                    x, y, x+cell_w, y+cell_h,
                    fill=fill, outline="#000", width=1
                )
                text_id = self.canvas.create_text(
                    x+cell_w//2, y+cell_h//2, text=str(num),
                    font=("微软雅黑", 9, "bold") if status=="sold" else ("微软雅黑", 9),
                    fill=self.get_fg(status)
                )
                self.seat_items[(r, c)] = (rect_id, text_id)
                if status == "available":
                    self.canvas.tag_bind(rect_id, '<Button-1>', lambda e, r=r, c=c: self.toggle_seat(r, c))
                    self.canvas.tag_bind(text_id, '<Button-1>', lambda e, r=r, c=c: self.toggle_seat(r, c))
                max_x = max(max_x, x+cell_w)
                max_y = max(max_y, y+cell_h)
        
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.config(scrollregion=bbox)
            # 居中显示
            canvas_w = self.canvas.winfo_width()
            canvas_h = self.canvas.winfo_height()
            content_w = max_x + pad_x
            content_h = max_y + pad_y
            x_offset = max((canvas_w - content_w) // 2, 0)
            y_offset = max((canvas_h - content_h) // 2, 0)
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
            if x_offset > 0 or y_offset > 0:
                self.canvas.move("all", x_offset, y_offset)

    def get_bg(self, status):
        """
        根据座位状态返回背景色。
        参数：
            status: 座位状态字符串
        返回：
            str: 背景色
        """
        if status == "available":
            return "#fff"  # 可售座位白色
        elif status == "sold":
            return "#bdbdbd"
        elif status == "selected":
            return "#00FF00"  # 亮绿色
        return "#fff"

    def get_fg(self, status):
        """
        根据座位状态返回前景色（字体颜色）。
        参数：
            status: 座位状态字符串
        返回：
            str: 字体颜色
        """
        if status == "sold":
            return "#000"
        elif status == "selected":
            return "#fff"
        return "#000"

    def toggle_seat(self, r, c):
        """
        切换指定座位的选中状态，并刷新UI。
        参数：
            r: 行索引
            c: 列索引
        """
        seat = self.seat_data[r][c]
        key = (r, c)
        if key in self.selected_seats:
            self.selected_seats.remove(key)
            seat['status'] = 'available' if seat.get('s', 'F') == 'F' else 'sold'
        else:
            self.selected_seats.add(key)
            seat['status'] = "selected"
        self._update_seat_visual(r, c)
        # 新增：选座回调
        if hasattr(self, 'on_seat_selected') and callable(self.on_seat_selected):
            selected = [self.seat_data[r][c] for (r, c) in self.selected_seats]
            self.on_seat_selected(selected)
        # 新增：自动刷新底部显示
        self.update_info_label()

    def _update_seat_visual(self, r, c):
        """
        刷新指定座位的UI显示（颜色等）。
        参数：
            r: 行索引
            c: 列索引
        """
        seat = self.seat_data[r][c]
        status = seat.get('status', 'available')
        rect_id, text_id = self.seat_items[(r, c)]
        self.canvas.itemconfig(rect_id, fill=self.get_bg(status))
        self.canvas.itemconfig(text_id, fill=self.get_fg(status))

    def update_seats(self, seat_data):
        """
        更新座位数据并重绘座位图。
        参数：
            seat_data: 新的二维座位数据
        """
        self.seat_data = seat_data or []
        self.selected_seats.clear()
        self._draw_seats()
        self.update_info_label()

    def get_selected_seats(self):
        """
        获取当前选中的所有座位编号。
        返回：
            list: 选中座位的编号列表
        """
        return [self.seat_data[r][c]['num'] for (r, c) in self.selected_seats] 

    def set_on_seat_selected(self, callback):
        """
        设置选座回调函数。
        参数：
            callback: 回调函数
        """
        self.on_seat_selected = callback

    def update_info_label(self):
        """
        刷新底部提交订单按钮的显示内容，包括选中座位和价格。
        """
        selected = [self.seat_data[r][c] for (r, c) in self.selected_seats]
        priceinfo = self._priceinfo
        print(f"[DEBUG] update_info_label: selected seats = {len(selected)}")
        account = self.account_getter() if hasattr(self, 'account_getter') else {}
        if account and account.get('cardno'):
            price = float(priceinfo.get('proprice', 0) or 0)
            price_type = "会员价"
        else:
            price = float(priceinfo.get('orgprice', 0) or 0)
            price_type = "原价"
        print(f"[DEBUG] calculated price: {price} ({price_type})")
        seat_strs = []
        for r, c in self.selected_seats:
            seat = self.seat_data[r][c]
            # 直接使用座位数据中的row字段
            display_row = seat.get('row', r + 1)  # 使用数据中的row字段
            num = seat.get('num')
            seat_strs.append(f"{display_row}排{num}")
            # 调试：显示座位信息
            print(f"[DEBUG] 座位显示: {display_row}排{num}座 (数据r={seat.get('r')}, 真实rn={seat.get('rn')})")
        seat_info = '  '.join(seat_strs)
        total = int(price) * len(selected)
        price_part = f"  单价{int(price)}*{len(selected)}={total}元" if seat_strs else ""
        btn_text = f"提交订单  {seat_info}{price_part}" if seat_info else "提交订单"
        self.submit_btn.config(text=btn_text)

    def _on_submit_order_click(self):
        """
        提交订单按钮点击事件，调用外部回调。
        """
        if hasattr(self, 'on_submit_order') and callable(self.on_submit_order):
            selected = [self.seat_data[r][c] for (r, c) in self.selected_seats]
            self.on_submit_order(selected)

    def set_on_submit_order(self, callback):
        """
        设置提交订单回调函数。
        参数：
            callback: 回调函数
        """
        self.on_submit_order = callback

    def set_priceinfo(self, priceinfo):
        """
        设置当前价格信息，并刷新底部显示。
        参数：
            priceinfo: 价格信息字典
        """
        self._priceinfo = priceinfo or {}
        self.update_info_label()

    def set_account_getter(self, getter):
        """
        设置获取账号信息的回调函数。
        参数：
            getter: 回调函数
        """
        self.account_getter = getter 