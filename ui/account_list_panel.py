import tkinter as tk
from tkinter import ttk

class AccountListPanel(tk.Frame):
    def __init__(self, master, on_account_selected=None, on_set_main=None, on_clear_coupons=None, on_refresh_coupons=None):
        super().__init__(master, bg="#f5f5f5")
        self.pack_propagate(False)
        self.on_account_selected = on_account_selected
        self.on_set_main = on_set_main
        self.on_clear_coupons = on_clear_coupons
        self.on_refresh_coupons = on_refresh_coupons

        # 搜索行
        search_frame = tk.Frame(self, bg="#f5f5f5")
        search_frame.pack(fill=tk.X, pady=2)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        tk.Button(search_frame, text="模糊搜索", width=8).pack(side=tk.LEFT, padx=2)
        # 刷新券按钮
        self.refresh_btn = tk.Button(search_frame, text="刷新券", width=8, command=self.on_refresh_coupons)
        self.refresh_btn.pack(side=tk.LEFT, padx=2)

        # 账号列表
        columns = ("账号", "余额", "积分")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col=="账号" else 90, anchor="center")
        self.tree.pack(padx=5, pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.on_right_click)
        self._accounts = []
        self._main_tag = "main_account"
        self.tree.tag_configure(self._main_tag, foreground="red", font=("微软雅黑", 10, "bold"))
        # 右键菜单
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="设为主账号", command=self.set_main_account)

    def update_accounts(self, accounts):
        self._accounts = accounts
        self.tree.delete(*self.tree.get_children())
        for idx, acc in enumerate(accounts):
            tags = (self._main_tag,) if acc.get('is_main') else ()
            self.tree.insert("", tk.END, values=(
                acc.get('userid', ''),
                acc.get('balance', 0),
                acc.get('score', 0)
            ), tags=tags)

    def on_tree_select(self, event):
        item = self.tree.focus()
        if not item:
            return
        idx = self.tree.index(item)
        if 0 <= idx < len(self._accounts):
            acc = self._accounts[idx]
            if self.on_account_selected:
                self.on_account_selected(acc)
            if self.on_clear_coupons:
                self.on_clear_coupons()  # 切换账号时清空券列表

    def on_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            self.menu.post(event.x_root, event.y_root)
            self._right_click_idx = self.tree.index(iid)
        else:
            self._right_click_idx = None

    def set_main_account(self):
        idx = getattr(self, '_right_click_idx', None)
        if idx is not None and 0 <= idx < len(self._accounts):
            if self.on_set_main:
                self.on_set_main(self._accounts[idx])

    def clear_coupons(self):
        if self.on_clear_coupons:
            self.on_clear_coupons() 