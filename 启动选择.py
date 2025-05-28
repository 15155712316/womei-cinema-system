#!/usr/bin/env python3
"""
乐影系统启动选择器
让用户选择运行哪个版本的系统
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class LauncherApp:
    """启动选择器应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎬 乐影系统启动选择器")
        self.root.geometry("600x400")
        self.center_window()
        
        self.create_ui()
    
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = 600
        height = 400
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_ui(self):
        """创建用户界面"""
        # 主框架
        main_frame = tk.Frame(self.root, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(main_frame, text="🎬 乐影系统启动选择器", 
                              font=("微软雅黑", 18, "bold"), 
                              fg="#2196F3", bg="white")
        title_label.pack(pady=(0, 30))
        
        # 说明文字
        info_label = tk.Label(main_frame, text="请选择要运行的系统版本：", 
                             font=("微软雅黑", 12), 
                             fg="#666", bg="white")
        info_label.pack(pady=(0, 20))
        
        # 选项框架
        options_frame = tk.Frame(main_frame, bg="white")
        options_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # 创建选项卡
        notebook = ttk.Notebook(options_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 新系统选项卡
        new_tab = self.create_new_system_tab(notebook)
        notebook.add(new_tab, text="🆕 新版积分系统")
        
        # 原系统选项卡
        old_tab = self.create_old_system_tab(notebook)
        notebook.add(old_tab, text="📽️ 原版票务系统")
        
        # 底部信息
        bottom_frame = tk.Frame(main_frame, bg="white")
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        info_text = "💡 提示：新版积分系统是登录验证+出票功能的完整集成版本\n📞 如有问题，请查看项目中的使用说明文档"
        bottom_label = tk.Label(bottom_frame, text=info_text, 
                               font=("微软雅黑", 9), 
                               fg="#999", bg="white", justify=tk.CENTER)
        bottom_label.pack()
    
    def create_new_system_tab(self, parent):
        """创建新系统选项卡"""
        tab = tk.Frame(parent, bg="white")
        
        # 系统介绍
        intro_frame = tk.LabelFrame(tab, text="系统介绍", font=("微软雅黑", 10), bg="white")
        intro_frame.pack(fill=tk.X, padx=20, pady=10)
        
        intro_text = """✅ 集成用户登录验证 + 影院出票功能
✅ 手机号+机器码双重验证，确保账号安全
✅ 积分系统：10积分=1元，购票可抵扣50%
✅ 积分商城：兑换优惠券和礼品
✅ 云端管理：在线管理用户账号和积分
✅ 现代UI设计，操作简单直观"""
        
        intro_label = tk.Label(intro_frame, text=intro_text, 
                              font=("微软雅黑", 10), 
                              fg="#333", bg="white", justify=tk.LEFT)
        intro_label.pack(padx=15, pady=10, anchor="w")
        
        # 启动选项
        launch_frame = tk.LabelFrame(tab, text="启动选项", font=("微软雅黑", 10), bg="white")
        launch_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 演示版按钮
        demo_btn = tk.Button(launch_frame, text="🎪 启动演示版（推荐）", 
                            font=("微软雅黑", 12, "bold"),
                            bg="#4CAF50", fg="white", 
                            height=2, width=25,
                            command=self.launch_demo)
        demo_btn.pack(pady=10)
        
        demo_desc = tk.Label(launch_frame, text="简化版本，包含核心功能，界面友好", 
                            font=("微软雅黑", 9), fg="#666", bg="white")
        demo_desc.pack()
        
        # 完整版按钮
        full_btn = tk.Button(launch_frame, text="🎬 启动完整版", 
                            font=("微软雅黑", 12, "bold"),
                            bg="#2196F3", fg="white", 
                            height=2, width=25,
                            command=self.launch_full)
        full_btn.pack(pady=(15, 10))
        
        full_desc = tk.Label(launch_frame, text="完整功能版本，包含所有高级功能", 
                            font=("微软雅黑", 9), fg="#666", bg="white")
        full_desc.pack()
        
        # 测试账号信息
        account_frame = tk.LabelFrame(tab, text="测试账号", font=("微软雅黑", 10), bg="white")
        account_frame.pack(fill=tk.X, padx=20, pady=10)
        
        account_text = "📱 手机号：15155712316\n💰 积分：800分\n🔧 机器码：自动获取"
        account_label = tk.Label(account_frame, text=account_text, 
                                font=("微软雅黑", 10), 
                                fg="#333", bg="white", justify=tk.LEFT)
        account_label.pack(padx=15, pady=10)
        
        return tab
    
    def create_old_system_tab(self, parent):
        """创建原系统选项卡"""
        tab = tk.Frame(parent, bg="white")
        
        # 系统介绍
        intro_frame = tk.LabelFrame(tab, text="系统介绍", font=("微软雅黑", 10), bg="white")
        intro_frame.pack(fill=tk.X, padx=20, pady=10)
        
        intro_text = """🎫 专业的电影票务管理系统
🏢 支持多影院、多账号管理
🎪 完整的选座、下单、支付流程
🎟️ 优惠券管理和绑定功能
📊 订单详情和取票码生成
🔧 丰富的配置和管理选项"""
        
        intro_label = tk.Label(intro_frame, text=intro_text, 
                              font=("微软雅黑", 10), 
                              fg="#333", bg="white", justify=tk.LEFT)
        intro_label.pack(padx=15, pady=10, anchor="w")
        
        # 启动按钮
        launch_frame = tk.LabelFrame(tab, text="启动系统", font=("微软雅黑", 10), bg="white")
        launch_frame.pack(fill=tk.X, padx=20, pady=10)
        
        old_btn = tk.Button(launch_frame, text="📽️ 启动原版票务系统", 
                           font=("微软雅黑", 12, "bold"),
                           bg="#FF9800", fg="white", 
                           height=2, width=25,
                           command=self.launch_old)
        old_btn.pack(pady=15)
        
        # 功能说明
        features_frame = tk.LabelFrame(tab, text="主要功能", font=("微软雅黑", 10), bg="white")
        features_frame.pack(fill=tk.X, padx=20, pady=10)
        
        features_text = """• 影院管理：万友影城等多影院支持
• 座位选择：可视化座位图，支持多座位选择
• 订单管理：完整的下单、支付、取票流程
• 券系统：优惠券绑定、查询、使用
• 账号管理：多账号切换，会员卡管理"""
        
        features_label = tk.Label(features_frame, text=features_text, 
                                 font=("微软雅黑", 9), 
                                 fg="#333", bg="white", justify=tk.LEFT)
        features_label.pack(padx=15, pady=10, anchor="w")
        
        return tab
    
    def launch_demo(self):
        """启动演示版"""
        try:
            self.root.withdraw()  # 隐藏选择器窗口
            subprocess.run([sys.executable, "cinema_demo.py"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("启动失败", f"启动演示版失败：{e}")
        except FileNotFoundError:
            messagebox.showerror("文件未找到", "找不到 cinema_demo.py 文件")
        finally:
            self.root.deiconify()  # 重新显示选择器窗口
    
    def launch_full(self):
        """启动完整版"""
        try:
            self.root.withdraw()
            subprocess.run([sys.executable, "integrated_cinema_system.py"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("启动失败", f"启动完整版失败：{e}")
        except FileNotFoundError:
            messagebox.showerror("文件未找到", "找不到 integrated_cinema_system.py 文件")
        finally:
            self.root.deiconify()
    
    def launch_old(self):
        """启动原版系统"""
        try:
            self.root.withdraw()
            subprocess.run([sys.executable, "main.py"], check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("启动失败", f"启动原版系统失败：{e}")
        except FileNotFoundError:
            messagebox.showerror("文件未找到", "找不到 main.py 文件")
        finally:
            self.root.deiconify()
    
    def run(self):
        """运行应用"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n程序已退出")

def main():
    """主函数"""
    print("🎬 启动乐影系统选择器...")
    app = LauncherApp()
    app.run()

if __name__ == "__main__":
    main() 