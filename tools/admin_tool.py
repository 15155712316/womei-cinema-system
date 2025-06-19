#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐影系统管理工具
提供用户管理、机器码更新等管理功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import json
import hashlib
import platform
import subprocess
import time
from services.admin_api import admin_api_service
from services.auth_service import AuthService

class AdminTool:
    """管理工具主界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("乐影系统管理工具 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 样式配置
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.refresh_users()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="乐影系统管理工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 当前机器码显示
        machine_frame = ttk.LabelFrame(main_frame, text="当前机器信息", padding="10")
        machine_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        machine_frame.columnconfigure(1, weight=1)
        
        ttk.Label(machine_frame, text="当前机器码:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.current_machine_code = self.get_current_machine_code()
        self.machine_code_var = tk.StringVar(value=self.current_machine_code)
        machine_code_entry = ttk.Entry(machine_frame, textvariable=self.machine_code_var, 
                                     state='readonly', font=('Courier', 10))
        machine_code_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        copy_button = ttk.Button(machine_frame, text="复制", 
                               command=self.copy_machine_code)
        copy_button.grid(row=0, column=2)
        
        # 用户列表框架
        users_frame = ttk.LabelFrame(main_frame, text="用户管理", padding="10")
        users_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        users_frame.columnconfigure(0, weight=1)
        users_frame.rowconfigure(1, weight=1)
        
        # 工具栏
        toolbar = ttk.Frame(users_frame)
        toolbar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(toolbar, text="刷新列表", command=self.refresh_users).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="修改机器码", command=self.update_machine_code).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="修改积分", command=self.update_points).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(toolbar, text="修改状态", command=self.update_status).pack(side=tk.LEFT)
        
        # 用户列表
        self.tree_frame = ttk.Frame(users_frame)
        self.tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ('phone', 'points', 'status', 'machine_code', 'create_time')
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题和宽度
        self.tree.heading('phone', text='手机号')
        self.tree.heading('points', text='积分')
        self.tree.heading('status', text='状态')
        self.tree.heading('machine_code', text='机器码')
        self.tree.heading('create_time', text='创建时间')
        
        self.tree.column('phone', width=120, anchor=tk.CENTER)
        self.tree.column('points', width=80, anchor=tk.CENTER)
        self.tree.column('status', width=80, anchor=tk.CENTER)
        self.tree.column('machine_code', width=200, anchor=tk.CENTER)
        self.tree.column('create_time', width=150, anchor=tk.CENTER)
        
        # 滚动条
        scrollbar_y = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 网格布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def get_current_machine_code(self):
        """获取当前机器的机器码"""
        try:
            auth_service = AuthService()
            return auth_service.get_machine_code()
        except Exception as e:
            return f"获取失败: {e}"
    
    def copy_machine_code(self):
        """复制机器码到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_machine_code)
            self.root.update()
            messagebox.showinfo("成功", "机器码已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")
    
    def refresh_users(self):
        """刷新用户列表"""
        self.status_var.set("正在刷新用户列表...")
        self.root.update()
        
        try:
            # 清空现有数据
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # 模拟用户数据（实际应该从API获取）
            users_data = [
                {
                    "phone": "15155712316",
                    "points": 800,
                    "status": 1,
                    "machine_code": "7DA491096E7B6854",
                    "create_time": "2025-05-28 23:02"
                }
            ]
            
            # 添加用户数据到树形视图
            for user in users_data:
                status_text = "启用" if user["status"] == 1 else "禁用"
                self.tree.insert('', tk.END, values=(
                    user["phone"],
                    user["points"],
                    status_text,
                    user["machine_code"],
                    user["create_time"]
                ))
            
            self.status_var.set(f"已加载 {len(users_data)} 个用户")
            
        except Exception as e:
            messagebox.showerror("错误", f"刷新用户列表失败: {e}")
            self.status_var.set("刷新失败")
    
    def get_selected_user(self):
        """获取选中的用户"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个用户")
            return None
        
        item = self.tree.item(selection[0])
        values = item['values']
        return {
            'phone': values[0],
            'points': values[1],
            'status': values[2],
            'machine_code': values[3],
            'create_time': values[4]
        }
    
    def update_machine_code(self):
        """修改用户机器码"""
        user = self.get_selected_user()
        if not user:
            return
        
        # 创建输入对话框
        dialog = MachineCodeDialog(self.root, user['phone'], user['machine_code'])
        if dialog.result:
            new_machine_code = dialog.result
            
            self.status_var.set(f"正在更新用户 {user['phone']} 的机器码...")
            self.root.update()
            
            try:
                # 这里应该调用实际的API，现在先模拟
                success = True
                
                if success:
                    messagebox.showinfo("成功", f"用户 {user['phone']} 的机器码已更新为:\n{new_machine_code}")
                    self.refresh_users()
                    self.status_var.set("机器码更新成功")
                else:
                    messagebox.showerror("失败", "机器码更新失败")
                    self.status_var.set("机器码更新失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"更新机器码时发生错误: {e}")
                self.status_var.set("更新失败")
    
    def update_points(self):
        """修改用户积分"""
        user = self.get_selected_user()
        if not user:
            return
        
        current_points = str(user['points']).replace("启用", "").replace("禁用", "").strip()
        new_points = simpledialog.askinteger(
            "修改积分",
            f"用户: {user['phone']}\n当前积分: {current_points}\n\n请输入新的积分数量:",
            initialvalue=int(current_points) if current_points.isdigit() else 0,
            minvalue=0,
            maxvalue=999999
        )
        
        if new_points is not None:
            self.status_var.set(f"正在更新用户 {user['phone']} 的积分...")
            self.root.update()
            
            try:
                # 这里应该调用实际的API
                success = True
                
                if success:
                    messagebox.showinfo("成功", f"用户 {user['phone']} 的积分已更新为 {new_points}")
                    self.refresh_users()
                    self.status_var.set("积分更新成功")
                else:
                    messagebox.showerror("失败", "积分更新失败")
                    self.status_var.set("积分更新失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"更新积分时发生错误: {e}")
                self.status_var.set("更新失败")
    
    def update_status(self):
        """修改用户状态"""
        user = self.get_selected_user()
        if not user:
            return
        
        current_status = user['status']
        new_status_text = "禁用" if current_status == "启用" else "启用"
        
        if messagebox.askyesno("确认", f"确定要将用户 {user['phone']} 的状态改为 {new_status_text} 吗？"):
            self.status_var.set(f"正在更新用户 {user['phone']} 的状态...")
            self.root.update()
            
            try:
                # 这里应该调用实际的API
                success = True
                
                if success:
                    messagebox.showinfo("成功", f"用户 {user['phone']} 的状态已更新为 {new_status_text}")
                    self.refresh_users()
                    self.status_var.set("状态更新成功")
                else:
                    messagebox.showerror("失败", "状态更新失败")
                    self.status_var.set("状态更新失败")
                    
            except Exception as e:
                messagebox.showerror("错误", f"更新状态时发生错误: {e}")
                self.status_var.set("更新失败")
    
    def run(self):
        """运行管理工具"""
        self.root.mainloop()


class MachineCodeDialog:
    """机器码修改对话框"""
    
    def __init__(self, parent, phone, current_machine_code):
        self.result = None
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("修改机器码")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui(phone, current_machine_code)
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def setup_ui(self, phone, current_machine_code):
        """设置对话框界面"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 用户信息
        info_frame = ttk.LabelFrame(main_frame, text="用户信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(info_frame, text=f"手机号: {phone}", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"当前机器码: {current_machine_code}").pack(anchor=tk.W, pady=(5, 0))
        
        # 新机器码输入
        input_frame = ttk.LabelFrame(main_frame, text="新机器码", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(input_frame, text="请输入新的机器码:").pack(anchor=tk.W)
        
        self.machine_code_var = tk.StringVar(value=current_machine_code)
        self.machine_code_entry = ttk.Entry(input_frame, textvariable=self.machine_code_var, 
                                           font=('Courier', 10), width=40)
        self.machine_code_entry.pack(fill=tk.X, pady=(5, 10))
        
        # 快捷操作
        quick_frame = ttk.Frame(input_frame)
        quick_frame.pack(fill=tk.X)
        
        ttk.Button(quick_frame, text="使用当前机器码", 
                  command=self.use_current_machine_code).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(quick_frame, text="清空", 
                  command=lambda: self.machine_code_var.set("")).pack(side=tk.LEFT)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.RIGHT)
    
    def use_current_machine_code(self):
        """使用当前机器码"""
        try:
            auth_service = AuthService()
            current_code = auth_service.get_machine_code()
            self.machine_code_var.set(current_code)
        except Exception as e:
            messagebox.showerror("错误", f"获取当前机器码失败: {e}")
    
    def ok_clicked(self):
        """确定按钮点击"""
        new_code = self.machine_code_var.get().strip()
        if not new_code:
            messagebox.showwarning("警告", "请输入机器码")
            return
        
        if len(new_code) != 16:
            messagebox.showwarning("警告", "机器码长度应为16位")
            return
        
        self.result = new_code
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """取消按钮点击"""
        self.dialog.destroy()


def main():
    """主函数"""
    try:
        app = AdminTool()
        app.run()
    except Exception as e:
        import traceback
        error_msg = f"程序启动失败:\n{e}\n\n详细错误:\n{traceback.format_exc()}"
        print(error_msg)
        
        # 如果tkinter可用，显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("启动错误", error_msg)
        except:
            pass


if __name__ == "__main__":
    main() 