import tkinter as tk

class SeatMapPanel(tk.Frame):
    """
    影院座位图UI组件（Canvas方案），每个座位为黑色边框矩形，支持可售/已售/选中状态，交互逻辑与原Button方案一致。
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
        self.seat_items = {}  # (r, c): (rect_id, text_id)
        self._draw_seats()
        self._draw_legend()

    def _draw_seats(self):
        self.canvas.delete("all")
        self.seat_items.clear()
        # 座位格子参数
        cell_w, cell_h = 32, 32
        pad_x, pad_y = 6, 6
        label_w = 24
        for r, row in enumerate(self.seat_data):
            y = pad_y + r * (cell_h + pad_y)
            # 排号
            self.canvas.create_text(label_w//2, y + cell_h//2, text=str(r+1), font=("微软雅黑", 10, "bold"), fill="#333")
            last_cn = 0
            for c, seat in enumerate(row):
                if seat is None:
                    continue
                cn = int(seat.get('cn', c+1))
                x = label_w + pad_x + (cn-1) * (cell_w + pad_x)
                num = seat.get('num', '')
                status = seat.get('status', 'available')
                if status == 'empty':
                    continue
                # 画矩形（黑色边框）
                fill = self.get_bg(status)
                rect_id = self.canvas.create_rectangle(
                    x, y, x+cell_w, y+cell_h,
                    fill=fill, outline="#000", width=1
                )
                text_id = self.canvas.create_text(
                    x+cell_w//2, y+cell_h//2, text=str(num),
                    font=("微软雅黑", 12, "bold") if status=="sold" else ("微软雅黑", 12),
                    fill=self.get_fg(status)
                )
                self.seat_items[(r, c)] = (rect_id, text_id)
                # 绑定点击事件
                if status == "available":
                    self.canvas.tag_bind(rect_id, '<Button-1>', lambda e, r=r, c=c: self.toggle_seat(r, c))
                    self.canvas.tag_bind(text_id, '<Button-1>', lambda e, r=r, c=c: self.toggle_seat(r, c))
        # 更新滚动区域
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.config(scrollregion=bbox)

    def _draw_legend(self):
        # 图例用Canvas画
        legend = tk.Canvas(self, bg="#fff", height=36, highlightthickness=0)
        legend.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6,0))
        items = [
            ("#fff", "#000", "可售"),
            ("#4caf50", "#fff", "已选"),
            ("#bdbdbd", "#000", "已售"),
        ]
        for i, (bg, fg, label) in enumerate(items):
            x = 10 + i*90
            legend.create_rectangle(x, 8, x+28, 32, fill=bg, outline="#000", width=1)
            legend.create_text(x+14, 20, text="座", font=("微软雅黑", 10, "bold"), fill=fg)
            legend.create_text(x+44, 20, text=label, font=("微软雅黑", 9), fill="#333")

    def get_bg(self, status):
        if status == "available":
            return "#fff"  # 可售座位白色
        elif status == "sold":
            return "#bdbdbd"
        elif status == "selected":
            return "#00FF00"  # 亮绿色
        return "#fff"

    def get_fg(self, status):
        if status == "sold":
            return "#000"
        elif status == "selected":
            return "#fff"
        return "#000"

    def toggle_seat(self, r, c):
        seat = self.seat_data[r][c]
        key = (r, c)
        if key in self.selected_seats:
            self.selected_seats.remove(key)
            seat['status'] = 'available' if seat.get('s', 'F') == 'F' else 'sold'
        else:
            self.selected_seats.add(key)
            seat['status'] = "selected"
        self._update_seat_visual(r, c)

    def _update_seat_visual(self, r, c):
        seat = self.seat_data[r][c]
        status = seat.get('status', 'available')
        rect_id, text_id = self.seat_items[(r, c)]
        self.canvas.itemconfig(rect_id, fill=self.get_bg(status))
        self.canvas.itemconfig(text_id, fill=self.get_fg(status))

    def update_seats(self, seat_data):
        self.seat_data = seat_data or []
        self.selected_seats.clear()
        self._draw_seats()

    def get_selected_seats(self):
        return [self.seat_data[r][c]['num'] for (r, c) in self.selected_seats] 