import tkinter as tk
from tkinter import ttk

class AccountListPanel(tk.Frame):
    def __init__(self, master, on_account_selected=None):
        super().__init__(master, bg="#f5f5f5")
        self.pack_propagate(False)
        self.on_account_selected = on_account_selected

        # 搜索行
        search_frame = tk.Frame(self, bg="#f5f5f5")
        search_frame.pack(fill=tk.X, pady=2)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        tk.Button(search_frame, text="模糊搜索", width=8).pack(side=tk.LEFT, padx=2)

        # 账号列表
        columns = ("账号", "余额", "积分")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col=="账号" else 90, anchor="center")
        self.tree.pack(padx=5, pady=10, fill=tk.BOTH, expand=True)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)
        self._accounts = []

    def update_accounts(self, accounts):
        self._accounts = accounts
        self.tree.delete(*self.tree.get_children())
        for acc in accounts:
            self.tree.insert("", tk.END, values=(
                acc.get('userid', ''),
                acc.get('balance', 0),
                acc.get('score', 0)
            ))

    def on_tree_select(self, event):
        item = self.tree.focus()
        if not item:
            return
        idx = self.tree.index(item)
        if 0 <= idx < len(self._accounts):
            acc = self._accounts[idx]
            if self.on_account_selected:
                self.on_account_selected(acc) 