import ttkbootstrap as tb

class LoginPanel(tb.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack_propagate(False)

        # 第一行：手机号输入框
        row1 = tb.Frame(self)
        row1.pack(fill="x", padx=10, pady=6)
        self.phone_entry = tb.Entry(row1, font=("微软雅黑", 11))
        self.phone_entry.pack(fill="x", expand=True, ipadx=8, ipady=4)

        # 第二行：ck输入框
        row2 = tb.Frame(self)
        row2.pack(fill="x", padx=10, pady=6)
        self.ck_entry = tb.Entry(row2, font=("微软雅黑", 11))
        self.ck_entry.pack(fill="x", expand=True, ipadx=8, ipady=4)

        # 第三行：登录按钮（单独一行）
        row3 = tb.Frame(self)
        row3.pack(fill="x", padx=10, pady=6)
        login_btn = tb.Button(
            row3,
            text="登录",
            bootstyle="secondary,outline",
            width=8
        )
        login_btn.pack(side="left", ipadx=4, ipady=2)

        # 美化：按钮背景白色，字体黑色
        style = tb.Style()
        style.configure("TButton", background="#fff", foreground="#000", font=("微软雅黑", 11))
        style.map("TButton", background=[("active", "#f0f0f0")])

        # 输入框圆角（ttkbootstrap已较圆润，极致圆角需更高级UI库） 