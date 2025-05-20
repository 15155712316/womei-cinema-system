import tkinter as tk
from tkinter import ttk

class AccountPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#f5f5f5")
        self.pack_propagate(False)

        # 第一行：账号输入框 + 导入按钮
        row1 = tk.Frame(self, bg="#f5f5f5")
        row1.pack(fill=tk.X, pady=2)
        self.account_entry = tk.Entry(row1)
        self.account_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        tk.Button(row1, text="导入", width=6).pack(side=tk.LEFT, padx=2)

        # 第二行：密码输入框 + 登录按钮
        row2 = tk.Frame(self, bg="#f5f5f5")
        row2.pack(fill=tk.X, pady=2)
        self.password_entry = tk.Entry(row2, show="*")
        self.password_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        tk.Button(row2, text="登录", width=6).pack(side=tk.LEFT, padx=2)

        # 第三行：ck输入框
        row3 = tk.Frame(self, bg="#f5f5f5")
        row3.pack(fill=tk.X, pady=2)
        self.ck_entry = tk.Entry(row3)
        self.ck_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 第四行：搜索账号 + 模糊搜索 + 刷新会员卡
        row4 = tk.Frame(self, bg="#f5f5f5")
        row4.pack(fill=tk.X, pady=2)
        self.search_entry = tk.Entry(row4)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 2), fill=tk.X, expand=True)
        tk.Button(row4, text="模糊搜索", width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(row4, text="刷新会员卡", width=10).pack(side=tk.LEFT, padx=2)

        # 账号列表区
        columns = ("账号", "余额", "积分")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor="center")
        self.tree.pack(padx=5, pady=10, fill=tk.BOTH, expand=True)

        # 示例数据（可删除）
        example_data = [
            ("15155712316", "6.8", "4089"),
            ("1386655...", "1.8", "111"),
            ("1470028...", "28", "972"),
            ("1470028...", "0.5", "2502"),
            ("1470028...", "1451.2", "550"),
            ("1515553...", "40.2", "960"),
            ("1515571...", "0.2", "1038"),
            ("1553444...", "110.6", "816"),
            ("1565171...", "0.1", "1000"),
            ("1775141...", "0", "0"),
            ("1845579...", "6796.2", "56991"),
        ]
        for row in example_data:
            self.tree.insert("", tk.END, values=row)
