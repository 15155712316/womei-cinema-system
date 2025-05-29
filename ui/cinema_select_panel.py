import tkinter as tk
from tkinter import ttk  # 使用标准ttk替代ttkbootstrap
from services.cinema_manager import cinema_manager
from services.film_service import get_films, load_cinemas, normalize_film_data, get_plan_seat_info
from services.ui_utils import MessageManager
import json
import os

class CinemaSelectPanel(tk.Frame):  # 使用标准tk.Frame
    def __init__(self, master, on_cinema_changed=None):
        super().__init__(master)
        self.pack_propagate(False)
        self.on_cinema_changed = on_cinema_changed
        
        # 添加主窗口引用，便于访问current_account
        self.main_window = None

        # 字体和间距参数
        combo_font = ("微软雅黑", 10)         # 下拉框和输入框字体
        btn_font = ("微软雅黑", 10, "bold")   # 按钮字体
        row_pady = 2                        # 行间距
        row_padx = 5                        # 列间距

        # 1. 读取影院参数
        self.cinemas = load_cinemas()
        cinema_names = [c['name'] for c in self.cinemas]

        # ========== 行1：影院下拉 ==========
        row1 = tk.Frame(self)  # 使用标准tk.Frame
        row1.pack(fill="x", padx=row_padx, pady=row_pady)
        tk.Label(row1, text="影院：", font=combo_font).pack(side="left", padx=(0, 2))  # 使用标准tk.Label
        self.cinema_var = tk.StringVar()  # 使用标准tk.StringVar
        self.cinema_combo = ttk.Combobox(  # 使用标准ttk.Combobox
            row1, textvariable=self.cinema_var, values=cinema_names, font=combo_font, state="readonly"
        )
        self.cinema_combo.pack(side="left", fill="x", expand=True)
        self.cinema_combo.bind('<<ComboboxSelected>>', self.on_cinema_select)

        # ========== 行2：电影下拉 ==========
        row2 = tk.Frame(self)
        row2.pack(fill="x", padx=row_padx, pady=row_pady)
        tk.Label(row2, text="影片：", font=combo_font).pack(side="left", padx=(0, 2))
        self.movie_var = tk.StringVar()
        self.movie_combo = ttk.Combobox(
            row2, textvariable=self.movie_var, values=[], font=combo_font, state="readonly"
        )
        self.movie_combo.pack(side="left", fill="x", expand=True)
        self.movie_combo.bind('<<ComboboxSelected>>', self.on_movie_select)

        # ========== 行3：日期下拉 ==========
        row3 = tk.Frame(self)
        row3.pack(fill="x", padx=row_padx, pady=row_pady)
        tk.Label(row3, text="日期：", font=combo_font).pack(side="left", padx=(0, 2))
        self.date_var = tk.StringVar()
        self.date_combo = ttk.Combobox(
            row3, textvariable=self.date_var, values=[], font=combo_font, state="readonly"
        )
        self.date_combo.pack(side="left", fill="x", expand=True)
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_select)

        # ========== 行5：场次选择 ==========
        row5 = tk.Frame(self)
        row5.pack(fill="x", padx=row_padx, pady=row_pady)
        tk.Label(row5, text="场次：", font=combo_font).pack(anchor="w")
        self.session_var = tk.StringVar()
        self.session_combo = ttk.Combobox(row5, textvariable=self.session_var, state="readonly", font=combo_font)
        self.session_combo.pack(fill="x", padx=2, pady=2)
        self.session_combo.bind("<<ComboboxSelected>>", self.on_session_select)

        # ========== 行6：操作按钮 ==========
        row6 = tk.Frame(self)
        row6.pack(fill="x", padx=row_padx, pady=row_pady+1)
        tk.Button(row6, text="打开选座 获取可用券", font=btn_font, width=18)\
            .pack(fill="x", pady=0)
        # 当前账号显示区
        self.current_account_label = tk.Label(self, text="当前账号：-", font=("微软雅黑", 11, "bold"), fg="red")
        self.current_account_label.pack(fill="x", padx=8, pady=(2, 0))

    def set_main_window(self, main_window):
        """
        设置主窗口引用，便于访问当前账号信息
        参数：
            main_window: 主窗口对象
        """
        self.main_window = main_window

    def get_current_account(self):
        """
        获取当前登录的账号信息
        返回：
            dict: 当前账号信息，如果没有登录则返回None
        """
        if self.main_window and hasattr(self.main_window, 'current_account'):
            account = getattr(self.main_window, 'current_account', None)
            print(f"[DEBUG] get_current_account: main_window存在={self.main_window is not None}")
            print(f"[DEBUG] get_current_account: account存在={account is not None}")
            if account:
                print(f"[DEBUG] account详情: userid={account.get('userid', 'N/A')}, cinemaid={account.get('cinemaid', 'N/A')}, balance={account.get('balance', 'N/A')}")
            else:
                print(f"[DEBUG] account为空，main_window.current_account={getattr(self.main_window, 'current_account', 'ATTR_NOT_FOUND')}")
            return account
        else:
            print(f"[DEBUG] get_current_account: main_window={self.main_window}, has_current_account={hasattr(self.main_window, 'current_account') if self.main_window else 'N/A'}")
            return None

    # ========== 联动事件 ==========
    def on_cinema_select(self, event):
        """
        影院下拉框选中事件，加载对应影院的影片和场次数据，并自动联动更新影片下拉框。
        参数：
            event: 事件对象（可为None）
        """
        print("[DEBUG] on_cinema_select 被触发")
        print(f"[DEBUG] event: {event}")
        
        # 清空券列表
        if hasattr(self.main_window, 'clear_coupons'):
            self.main_window.clear_coupons()
        
        idx = self.cinema_combo.current()
        print(f"[DEBUG] cinema_combo.current() = {idx}")
        
        if idx < 0:
            print("[DEBUG] idx < 0, 提前返回")
            return
            
        selected = self.cinemas[idx]
        base_url = selected['base_url']
        cinemaid = selected['cinemaid']
        print(f"[DEBUG] 选中影院: {selected.get('name', '未知')}, cinemaid: {cinemaid}")
        
        # 修复：使用新的获取当前账号的方法
        print("[DEBUG] 正在调用 get_current_account()...")
        current_account = self.get_current_account()
        print(f"[DEBUG] get_current_account() 返回: {current_account is not None}")
        
        if not current_account:
            print("[DEBUG] current_account为空，显示登录提示")
            MessageManager.show_warning(self.master, "登录提示", "请先登录账号后再选择影院")
            return
            
        print("[DEBUG] 账号验证通过，继续执行...")
        openid = current_account.get('openid', '')
        token = current_account.get('token', '')
        userid = current_account.get('userid', '')

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

        if self.on_cinema_changed:
            self.on_cinema_changed()

    def on_movie_select(self, event):
        """
        影片下拉框选中事件，加载对应影片的日期和场次数据，并自动联动更新日期下拉框。
        参数：
            event: 事件对象（可为None）
        """
        # 清空券列表
        if hasattr(self.main_window, 'clear_coupons'):
            self.main_window.clear_coupons()
            
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
        """
        日期下拉框选中事件，加载对应日期的场次数据，并自动联动更新场次下拉框。
        参数：
            event: 事件对象（可为None）
        """
        # 清空券列表
        if hasattr(self.main_window, 'clear_coupons'):
            self.main_window.clear_coupons()
            
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
        self.current_sessions = session_list
        # 自动联动：选中第一个场次并自动刷新座位图
        if session_list and hasattr(self, 'seat_panel'):
            self.on_session_select(0)

    def on_session_select(self, idx_or_event):
        """
        场次下拉框选中事件或索引选中，加载对应场次的座位图信息，并联动座位面板。
        参数：
            idx_or_event: 事件对象或场次索引
        """
        # 清空券列表
        if hasattr(self.main_window, 'clear_coupons'):
            self.main_window.clear_coupons()
            
        # 支持事件或索引
        if isinstance(idx_or_event, int):
            idx = idx_or_event
        else:
            idx = self.session_combo.current()
        if not hasattr(self, 'current_sessions') or idx < 0 or idx >= len(self.current_sessions):
            return
        session = self.current_sessions[idx]
        # ====== 参数提取 ======
        showCode = session['g']           # 场次唯一编码
        hallCode = session['j']           # 影厅编码
        filmCode = session.get('h', self.current_film_key)  # 影片编码
        filmNo = self.films_map[self.current_film_key]['fno']  # 影片No
        showDate = session['k'].split(' ')[0]  # 放映日期
        startTime = session['q']          # 放映开始时间
        
        # 修复：使用新的获取当前账号的方法
        current_account = self.get_current_account()
        if not current_account:
            MessageManager.show_warning(self.master, "登录提示", "请先登录账号后再查看座位")
            return
            
        userid = current_account.get('userid', '')
        openid = current_account.get('openid', '')
        token = current_account.get('token', '')
        
        # 影院参数
        cinema = self.cinemas[self.cinema_combo.current()]
        cinemaid = cinema['cinemaid']     # 影院ID
        
        print(f"[DEBUG] 座位请求参数检查:")
        print(f"  用户认证信息: userid={userid}, openid={openid[:10]}..., token={token[:10]}...")
        print(f"  影院信息: cinemaid={cinemaid}, base_url={cinema['base_url']}")
        print(f"  场次信息: showCode={showCode}, startTime={startTime}, showDate={showDate}")
        
        # ====== 请求座位图接口 ======
        seats_data = get_plan_seat_info(
            cinema['base_url'], showCode, hallCode, filmCode, filmNo, showDate, startTime,
            userid, openid, token, cinemaid
        )
        # 新增：保存价格信息到主窗口（无条件赋值，确保后续读取不为None）
        priceinfo = seats_data['resultData'].get('priceinfo', {}) if seats_data and 'resultData' in seats_data and seats_data['resultData'] else {}
        self.master.master.last_priceinfo = priceinfo
        print("last_priceinfo set to:", priceinfo)
        if hasattr(self, 'seat_panel') and hasattr(self.seat_panel, 'set_priceinfo'):
            self.seat_panel.set_priceinfo(priceinfo)
        if hasattr(self.master.master, 'current_account'):
            self.master.master.current_account = getattr(self.master.master, 'current_account', None)
        if not seats_data or 'resultData' not in seats_data or not seats_data['resultData']:
            # 分析具体的错误类型
            result_code = seats_data.get('resultCode', '') if seats_data else ''
            result_desc = seats_data.get('resultDesc', '') if seats_data else ''
            
            print(f"[DEBUG] 座位请求失败: resultCode={result_code}, resultDesc={result_desc}")
            
            # 修复：检查resultDesc中是否包含"已过场"关键词（无论resultCode是什么）
            if '过期' in result_desc or '已过场' in result_desc or '时间' in result_desc:
                MessageManager.show_warning(self.master, "已过场", "该场次已过场，无法选座")
            elif seats_data and result_code == '500':
                # 500错误但不是过场问题
                MessageManager.show_warning(self.master, "获取座位失败", f"无法获取座位信息：{result_desc}")
            elif seats_data and result_code == '400':
                if 'TOKEN_INVALID' in result_desc:
                    MessageManager.show_warning(self.master, "登录失效", "登录信息已失效，请重新登录")
                else:
                    MessageManager.show_warning(self.master, "获取座位失败", "座位信息暂时无法获取，请稍后重试")
            elif seats_data and seats_data.get('error'):
                # 网络错误或接口错误
                MessageManager.show_warning(self.master, "网络错误", f"座位接口请求失败：{seats_data.get('error', '未知错误')}")
            else:
                # 其他未知错误
                MessageManager.show_warning(self.master, "获取座位失败", "座位信息获取失败，请检查网络连接或稍后重试")
            
            self.seat_panel.update_seats([])
            return
        if 'seats' in seats_data['resultData']:
            # 处理为seat_map格式
            seats = seats_data['resultData']['seats']
            print(f"[座位数据调试] 原始座位数据总数: {len(seats)}")
            
            # 关键修复：使用数据中的r字段（连续行号）而不是rn字段（真实排号）
            all_rows = sorted(set(int(seat['r']) for seat in seats))  # 使用r字段！
            all_cols = sorted(set(int(seat['cn']) for seat in seats))
            max_col = max(all_cols) if all_cols else 0
            
            print(f"[座位数据调试] 数据行号(r): {all_rows}")
            print(f"[座位数据调试] 真实排号(rn): {sorted(set(int(seat['rn']) for seat in seats))}")
            print(f"[座位数据调试] 实际列数: {all_cols}")
            print(f"[座位数据调试] 最大列数: {max_col}")
            
            # 使用r字段的最大值作为行数
            max_row = max(all_rows) if all_rows else 0
            seat_map = [[None for _ in range(max_col)] for _ in range(max_row)]
            
            print(f"[座位映射调试] 使用数据行号r作为排号，范围: {all_rows}")
            
            for seat in seats:
                data_row = int(seat['r'])      # 数据中的行号（用于界面和下单）
                real_row = int(seat['rn'])     # 真实排号（仅用于参考）
                api_col = int(seat['cn'])
                ui_row = data_row - 1          # 转为数组索引
                ui_col = api_col - 1           # 列数减1作为索引
                
                # 修正：严格判断已售座位（如B、S、E等都算已售）
                status = 'available' if seat['s'] == 'F' else 'sold'
                
                # 详细调试输出关键座位
                if data_row in [1, 2, 3, 4] and api_col in [5, 6, 7, 9, 10]:
                    print(f"[关键座位] 数据排{data_row}列{api_col} -> 界面排{data_row}列{api_col}: r={seat['r']}, rn={seat['rn']}, cn={seat['cn']}, c={seat['c']}, s={seat['s']}, status={status}")
                
                seat_map[ui_row][ui_col] = {
                    'num': seat['c'],
                    'status': status,
                    'row': data_row,           # 保存数据行号，用于界面显示和下单
                    'real_row': real_row,      # 保存真实排号，仅用于参考
                    'sn': seat['sn'],
                    's': seat['s'],
                    'cn': seat['cn'],
                    'r': seat['r'],            # 保存原始r字段
                    'rn': seat['rn'],          # 保存原始rn字段
                }
            
            # 统计实际可用座位数量
            available_count = sum(1 for seat in seats if seat['s'] == 'F')
            sold_count = len(seats) - available_count
            print(f"[座位数据调试] 可用座位: {available_count}, 已售座位: {sold_count}")
            print(f"[座位数据调试] 最终seat_map尺寸: {len(seat_map)}行 x {max_col}列")
            
            self.seat_panel.update_seats(seat_map)
        else:
            self.seat_panel.update_seats([])

        print("on_seat_selected: last_priceinfo =", getattr(self.master.master, 'last_priceinfo', None))

        if hasattr(self.seat_panel, 'update_info_label'):
            self.seat_panel.update_info_label()

    def set_seat_panel(self, seat_panel):
        """
        设置座位面板对象，便于后续联动更新座位信息。
        参数：
            seat_panel: SeatMapPanel对象
        """
        self.seat_panel = seat_panel

    def set_current_account(self, account):
        """
        设置当前账号并更新显示
        参数：
            account: 账号信息字典
        """
        if account:
            userid = account.get('userid', '')
            cinemaid = account.get('cinemaid', '')
            self.current_account_label.config(text=f"当前账号：{userid}@{cinemaid}")
        else:
            self.current_account_label.config(text="当前账号：-")

    def get_current_session_info(self):
        """
        获取当前选中的场次信息。
        返回：
            dict: 当前选中的场次信息字典，包含 showCode、hallCode、filmCode、filmNo、showDate、startTime 等字段。
        """
        idx = self.session_combo.current()
        if hasattr(self, 'current_sessions') and 0 <= idx < len(self.current_sessions):
            return self.current_sessions[idx]
        return {}

    def get_current_film_info(self):
        """
        获取当前选中的影片信息。
        返回：
            dict: 当前选中的影片信息字典，包含 fc（影片编码）、fno（影片No）、fn（影片名称）等字段。
        """
        if hasattr(self, 'current_film_key') and hasattr(self, 'films_map'):
            return self.films_map.get(self.current_film_key, {})
        return {}
