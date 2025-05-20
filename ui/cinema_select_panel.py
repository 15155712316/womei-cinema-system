import ttkbootstrap as tb
from services.film_service import load_cinemas, get_films, normalize_film_data
import json
import os

class CinemaSelectPanel(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack_propagate(False)

        # 字体和间距参数
        combo_font = ("微软雅黑", 10)         # 下拉框和输入框字体
        btn_font = ("微软雅黑", 10, "bold")   # 按钮字体
        row_pady = 2                        # 行间距
        row_padx = 5                        # 列间距

        # 1. 读取影院参数
        self.cinemas = load_cinemas()
        cinema_names = [c['name'] for c in self.cinemas]

        # ========== 行1：影院下拉 ==========
        row1 = tb.Frame(self)
        row1.pack(fill="x", padx=row_padx, pady=row_pady)
        tb.Label(row1, text="影院：", font=combo_font).pack(side="left", padx=(0, 2))
        self.cinema_var = tb.StringVar()
        self.cinema_combo = tb.Combobox(
            row1, textvariable=self.cinema_var, values=cinema_names, font=combo_font, bootstyle="secondary", state="readonly"
        )
        self.cinema_combo.pack(side="left", fill="x", expand=True)
        self.cinema_combo.bind('<<ComboboxSelected>>', self.on_cinema_select)

        # ========== 行2：电影下拉 ==========
        row2 = tb.Frame(self)
        row2.pack(fill="x", padx=row_padx, pady=row_pady)
        tb.Label(row2, text="影片：", font=combo_font).pack(side="left", padx=(0, 2))
        self.movie_var = tb.StringVar()
        self.movie_combo = tb.Combobox(
            row2, textvariable=self.movie_var, values=[], font=combo_font, bootstyle="secondary", state="readonly"
        )
        self.movie_combo.pack(side="left", fill="x", expand=True)
        self.movie_combo.bind('<<ComboboxSelected>>', self.on_movie_select)

        # ========== 行3：日期下拉 ==========
        row3 = tb.Frame(self)
        row3.pack(fill="x", padx=row_padx, pady=row_pady)
        tb.Label(row3, text="日期：", font=combo_font).pack(side="left", padx=(0, 2))
        self.date_var = tb.StringVar()
        self.date_combo = tb.Combobox(
            row3, textvariable=self.date_var, values=[], font=combo_font, bootstyle="secondary", state="readonly"
        )
        self.date_combo.pack(side="left", fill="x", expand=True)
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_select)

        # ========== 行4：场次下拉 ==========
        row4 = tb.Frame(self)
        row4.pack(fill="x", padx=row_padx, pady=row_pady)
        tb.Label(row4, text="场次：", font=combo_font).pack(side="left", padx=(0, 2))
        self.session_var = tb.StringVar()
        self.session_combo = tb.Combobox(
            row4, textvariable=self.session_var, values=[], font=combo_font, bootstyle="secondary", state="readonly"
        )
        self.session_combo.pack(side="left", fill="x", expand=True)

        # ========== 行5：操作按钮 ==========
        row5 = tb.Frame(self)
        row5.pack(fill="x", padx=row_padx, pady=row_pady+1)
        tb.Button(row5, text="打开选座 获取可用券", bootstyle="secondary", width=18, style="Heavy.TButton")\
            .pack(fill="x", pady=0)

        # 美化：按钮纯黑字、加粗
        style = tb.Style()
        style.configure("Heavy.TButton", background="#fff", foreground="#000", font=btn_font, borderwidth=2)
        style.map("Heavy.TButton", foreground=[("active", "#000")], background=[("active", "#f0f0f0")])

    # ========== 联动事件 ==========
    def on_cinema_select(self, event):
        idx = self.cinema_combo.current()
        if idx < 0:
            return
        selected = self.cinemas[idx]
        base_url = selected['base_url']
        cinemaid = selected['cinemaid']
        openid = selected['openid']
        token = selected['token']
        userid = selected['userid']

        # 获取接口数据并标准化
        raw_data = get_films(base_url, cinemaid, openid, userid, token)
        self.films = raw_data['films']
        self.shows = raw_data['shows']

        film_names = [film['fn'] for film in self.films]
        film_keys = [film['fc'] for film in self.films]
        self.movie_combo['values'] = film_names
        self.movie_var.set(film_names[0] if film_names else "")
        self.film_key_map = dict(zip(film_names, film_keys))
        self.films_map = {film['fc']: film for film in self.films}

        # 自动联动：选中第一个影片，触发影片选择事件
        if film_names:
            self.on_movie_select(None)

    def on_movie_select(self, event):
        film_name = self.movie_var.get()
        film_key = self.film_key_map.get(film_name)
        if not film_key or film_key not in self.shows:
            self.date_combo['values'] = []
            self.date_var.set("")
            return
        date_list = list(self.shows[film_key].keys())
        self.date_combo['values'] = date_list
        self.date_var.set(date_list[0] if date_list else "")
        self.session_combo['values'] = []
        self.session_var.set("")
        self.current_film_key = film_key
        # 自动联动：选中第一个日期，触发日期选择事件
        if date_list:
            self.on_date_select(None)

    def on_date_select(self, event):
        date = self.date_var.get()
        film_key = getattr(self, 'current_film_key', None)
        if not film_key or not date or film_key not in self.shows:
            self.session_combo['values'] = []
            self.session_var.set("")
            return
        session_list = self.shows[film_key].get(date, [])
        session_display = [f"{s['q']} {s['t']} {s['r']} 票价:{s['tbprice']}" for s in session_list]
        self.session_combo['values'] = session_display
        self.session_var.set(session_display[0] if session_display else "")
        # 自动联动：选中第一个场次并自动刷新座位图
        if session_list and hasattr(self, 'seat_panel'):
            session_id = session_list[0].get('g')  # 假设'g'是场次ID
            seat_data = self.get_seats(session_id)  # 你需要实现get_seats
            self.seat_panel.update_seats(seat_data)

    def get_seats(self, session_id):
        # 实际项目中应根据 session_id 请求接口，这里用 result1.json 演示
        json_path = os.path.join(os.path.dirname(__file__), '../result1.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result = data['resultData']
        seats = result['seats']
        # 统计所有物理排号、列号
        all_rows = set(int(seat['rn']) for seat in seats)
        all_cols = set(int(seat['cn']) for seat in seats)
        max_row = max(all_rows)
        max_col = max(all_cols)
        # 初始化二维数组
        seat_map = [[None for _ in range(max_col)] for _ in range(max_row)]
        for seat in seats:
            row = int(seat['rn']) - 1  # 物理排号
            col = int(seat['cn']) - 1  # 物理列号
            status = 'available' if seat['s'] == 'F' else 'sold'
            seat_map[row][col] = {
                'num': seat['c'],      # 逻辑列号
                'status': status,
                'row': seat['rn'],
                'sn': seat['sn'],
                's': seat['s'],
                'cn': seat['cn'],      # 物理列号
            }
        return seat_map

    def set_seat_panel(self, seat_panel):
        self.seat_panel = seat_panel
