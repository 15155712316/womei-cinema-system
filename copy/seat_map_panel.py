import tkinter as tk

class SeatMapPanel(tk.Frame):
    """
    影院座位图UI组件，支持自适应滚动、可售/已售/选中座位样式、排号、辅助图例、交互逻辑。
    """
    def __init__(self, master, seat_data=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.seat_data = seat_data or []  # 二维座位数据
        self.selected_seats = set()       # 选中座位集合
        self._build_ui()

    def _build_ui(self):
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
        # 内部Frame
        self.inner = tk.Frame(self.canvas, bg="#fff")
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.seat_btns = {}
        self._draw_seats()
        self.inner.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self._draw_legend()

    def _draw_seats(self):
        # 清空旧按钮
        for btn in self.seat_btns.values():
            btn.destroy()
        self.seat_btns.clear()
        # 绘制座位
        for r, row in enumerate(self.seat_data):
            # 排号标签
            tk.Label(self.inner, text=str(r+1), width=2, bg="#fff", fg="#333", font=("微软雅黑", 10, "bold")).grid(row=r, column=0, padx=2, pady=2)
            last_cn = 0
            for c, seat in enumerate(row):
                if seat is None:
                    continue
                cn = int(seat.get('cn', c+1))
                # 跳号空位
                for _ in range(last_cn+1, cn):
                    tk.Label(self.inner, text='', width=3, height=1, bg="#fff", relief="flat", bd=0).grid(row=r, column=_, padx=2, pady=2)
                last_cn = cn
                num = seat.get('num', '')
                status = seat.get('status', 'available')
                if status == 'empty':
                    continue
                btn = tk.Button(
                    self.inner,
                    text=str(num),
                    width=3, height=1,
                    relief="solid",
                    bd=1 if status == "available" else (2 if status == "sold" else 1),
                    font=("微软雅黑", 10, "bold") if status == "sold" else ("微软雅黑", 10),
                    bg=self.get_bg(status),
                    fg=self.get_fg(status),
                    activebackground=self.get_bg(status),
                    activeforeground=self.get_fg(status),
                    cursor="arrow",
                    highlightthickness=1,
                    highlightbackground="#000",
                )
                if status == "available":
                    btn.config(command=lambda r=r, c=c: self.toggle_seat(r, c))
                btn.grid(row=r, column=cn, padx=2, pady=2)
                self.seat_btns[(r, c)] = btn

        # 新增：强制刷新所有按钮的背景色
        for (r, c), btn in self.seat_btns.items():
            seat = self.seat_data[r][c]
            status = seat.get('status', 'available')
            btn.config(bg=self.get_bg(status), fg=self.get_fg(status))

    def _draw_legend(self):
        # 辅助图例
        legend = tk.Frame(self, bg="#fff")
        legend.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6,0))
        items = [
            ("#fff", "#000", "可售"),
            ("#4caf50", "#fff", "已选"),
            ("#bdbdbd", "#000", "已售"),
        ]
        for i, (bg, fg, label) in enumerate(items):
            tk.Button(legend, text=" ", width=2, height=1, bg=bg, fg=fg, relief="solid", bd=2 if label=="已售" else 1, state="disabled").grid(row=0, column=2*i, padx=(0,2))
            tk.Label(legend, text=label, bg="#fff", fg="#333", font=("微软雅黑", 9)).grid(row=0, column=2*i+1, padx=(0,8))

    def get_bg(self, status):
        if status == "available":
            return "#fff"  # 可售座位与背景一致
        elif status == "sold":
            return "#bdbdbd"
        elif status == "selected":
            return "#4caf50"
        return "#fff"

    def get_fg(self, status):
        if status == "sold":
            return "#000"
        elif status == "selected":
            return "#fff"
        return "#000"  # 可售座位黑字

    def toggle_seat(self, r, c):
        seat = self.seat_data[r][c]
        key = (r, c)
        if key in self.selected_seats:
            self.selected_seats.remove(key)
            seat['status'] = 'available' if seat.get('s', 'F') == 'F' else 'sold'
        else:
            self.selected_seats.add(key)
            seat['status'] = "selected"
        btn = self.seat_btns[key]
        btn.config(bg=self.get_bg(seat['status']), fg=self.get_fg(seat['status']))

    def update_seats(self, seat_data):
        self.seat_data = seat_data or []
        self.selected_seats.clear()
        self._draw_seats()
        self.inner.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def get_selected_seats(self):
        return [self.seat_data[r][c]['num'] for (r, c) in self.selected_seats] 