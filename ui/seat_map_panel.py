import tkinter as tk

class SeatMapPanel(tk.Frame):
    def __init__(self, master, seat_data=None, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.seat_data = seat_data or []
        self.selected_seats = set()
        self._init_ui()

    def _init_ui(self):
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
        self.draw_seats()
        self.inner.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def draw_seats(self):
        for btn in self.seat_btns.values():
            btn.destroy()
        self.seat_btns.clear()
        for r, row in enumerate(self.seat_data):
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
                    bd=1,
                    font=("微软雅黑", 10),
                    bg=self.get_bg(status),
                    fg=self.get_fg(status),
                    state="normal" if status != "sold" else "disabled",
                    command=lambda r=r, c=c: self.toggle_seat(r, c)
                )
                btn.grid(row=r, column=cn, padx=2, pady=2)
                self.seat_btns[(r, c)] = btn

    def get_bg(self, status):
        if status == "available":
            return "#2196f3"  # 蓝色
        elif status == "sold":
            return "#f44336"  # 红色
        elif status == "selected":
            return "#4caf50"  # 绿色
        return "#fff"

    def get_fg(self, status):
        if status == "sold":
            return "#000"     # 黑色
        elif status == "selected":
            return "#fff"
        return "#fff"         # 蓝底白字

    def toggle_seat(self, r, c):
        seat = self.seat_data[r][c]
        key = (r, c)
        if key in self.selected_seats:
            self.selected_seats.remove(key)
            # 恢复为原始状态
            seat['status'] = 'available' if seat.get('s', 'F') == 'F' else 'sold'
        else:
            self.selected_seats.add(key)
            seat['status'] = "selected"
        btn = self.seat_btns[key]
        btn.config(bg=self.get_bg(seat['status']), fg=self.get_fg(seat['status']))

    def update_seats(self, seat_data):
        self.seat_data = seat_data or []
        self.selected_seats.clear()
        self.draw_seats()
        self.inner.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def get_selected_seats(self):
        return [self.seat_data[r][c]['num'] for (r, c) in self.selected_seats] 