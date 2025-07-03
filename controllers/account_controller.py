#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号控制器 - 处理账号相关的业务逻辑
"""

from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal
from utils.signals import event_bus, event_handler
from services.account_api import get_account_list, save_account, delete_account
from services.auth_service import AuthService
from services.member_service import MemberService


class AccountController(QObject):
    """账号控制器"""
    
    # 信号定义
    account_selected = pyqtSignal(dict)  # 账号选择
    account_login_success = pyqtSignal(dict)  # 账号登录成功
    account_login_failed = pyqtSignal(str)  # 账号登录失败
    account_list_updated = pyqtSignal(list)  # 账号列表更新
    account_error = pyqtSignal(str, str)  # 账号错误 (title, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 服务实例
        self.auth_service = AuthService()
        self.member_service = MemberService()
        
        # 当前状态
        self.current_account = None
        self.current_cinema = None
        self.account_list = []
        
        # 连接事件总线
        self._connect_events()
        
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.cinema_selected.connect(self._on_cinema_selected)
        event_bus.user_login_success.connect(self._on_user_login_success)
    
    @event_handler("cinema_selected")
    def _on_cinema_selected(self, cinema_data: dict):
        """影院选择处理"""
        self.current_cinema = cinema_data
        print(f"[账号控制器] 影院已选择: {cinema_data.get('cinemaShortName', 'N/A')}")
        
        # 重新加载账号列表（按影院过滤）
        self.load_account_list()
    
    @event_handler("user_login_success")
    def _on_user_login_success(self, user_data: dict):
        """用户登录成功处理"""
        print(f"[账号控制器] 用户登录成功: {user_data.get('phone', 'N/A')}")
        
        # 加载账号列表
        self.load_account_list()
    
    def load_account_list(self) -> List[dict]:
        """加载账号列表"""
        try:
            pass
            
            # 获取所有账号
            all_accounts = get_account_list()
            
            if not all_accounts:
                print("[账号控制器] 没有找到账号数据")
                self.account_list = []
                self.account_list_updated.emit([])
                return []
            
            # 如果有选择的影院，按影院过滤账号
            if self.current_cinema:
                cinema_id = self.current_cinema.get('cinemaid', '')
                filtered_accounts = []
                
                for account in all_accounts:
                    # 检查账号是否属于当前影院
                    account_cinema_id = account.get('cinemaid', '')
                    if account_cinema_id == cinema_id:
                        filtered_accounts.append(account)
                
                print(f"[账号控制器] 影院 {cinema_id} 过滤后账号数量: {len(filtered_accounts)}")
                self.account_list = filtered_accounts
            else:
                print(f"[账号控制器] 未选择影院，显示所有账号: {len(all_accounts)}")
                self.account_list = all_accounts
            
            # 发布账号列表更新事件
            self.account_list_updated.emit(self.account_list)
            
            return self.account_list
            
        except Exception as e:
            print(f"[账号控制器] 加载账号列表错误: {e}")
            self.account_error.emit("加载失败", f"加载账号列表失败: {str(e)}")
            return []
    
    def select_account(self, account_data: dict):
        """选择账号"""
        try:
            if not account_data:
                return
            
            self.current_account = account_data
            phone = account_data.get('phone', 'N/A')
            
            print(f"[账号控制器] 账号已选择: {phone}")
            
            # 发布账号选择事件
            self.account_selected.emit(account_data)
            event_bus.account_selected.emit(account_data)
            
            # 尝试获取会员信息
            self._load_member_info(account_data)
            
        except Exception as e:
            print(f"[账号控制器] 选择账号错误: {e}")
            self.account_error.emit("选择失败", f"选择账号失败: {str(e)}")
    
    def _load_member_info(self, account_data: dict):
        """加载会员信息"""
        try:
            if not self.current_cinema:
                return
            
            cinema_id = self.current_cinema.get('cinemaid', '')
            member_info = self.member_service.get_member_info(account_data, cinema_id)
            
            if member_info:
                print(f"[账号控制器] 会员信息加载成功")
                
                # 发布会员信息事件
                event_bus.emit_custom('member_info_loaded', {
                    'account': account_data,
                    'member_info': member_info
                })
            else:
                print(f"[账号控制器] 会员信息加载失败")
                
        except Exception as e:
            print(f"[账号控制器] 加载会员信息错误: {e}")
    
    def login_account(self, account_data: dict) -> bool:
        """登录账号"""
        try:
            if not account_data or not self.current_cinema:
                self.account_login_failed.emit("登录信息不完整")
                return False
            
            phone = account_data.get('phone', '')
            openid = account_data.get('openid', '')
            token = account_data.get('token', '')
            cinema_id = self.current_cinema.get('cinemaid', '')
            
            if not all([phone, openid, token, cinema_id]):
                self.account_login_failed.emit("账号信息不完整")
                return False
            
            # 调用登录API
            login_result = self.auth_service.cinema_login(phone, openid, token, cinema_id)
            
            if login_result and login_result.get('resultCode') == '0':
                print(f"[账号控制器] 账号登录成功: {phone}")
                
                # 更新账号信息
                updated_account = account_data.copy()
                updated_account.update(login_result.get('resultData', {}))
                
                # 发布登录成功事件
                self.account_login_success.emit(updated_account)
                event_bus.account_login_success.emit(updated_account)
                
                # 自动选择该账号
                self.select_account(updated_account)
                
                return True
            else:
                error_msg = login_result.get('resultDesc', '登录失败') if login_result else '网络错误'
                print(f"[账号控制器] 账号登录失败: {error_msg}")
                self.account_login_failed.emit(error_msg)
                return False
                
        except Exception as e:
            print(f"[账号控制器] 登录账号错误: {e}")
            self.account_login_failed.emit(f"登录处理失败: {str(e)}")
            return False
    
    def add_account(self, account_data: dict) -> bool:
        """添加账号"""
        try:
            # 验证账号数据
            required_fields = ['phone', 'openid', 'token']
            for field in required_fields:
                if not account_data.get(field):
                    self.account_error.emit("添加失败", f"缺少必要字段: {field}")
                    return False
            
            # 如果有当前影院，添加影院信息
            if self.current_cinema:
                account_data['cinemaid'] = self.current_cinema.get('cinemaid', '')
                account_data['cinema_name'] = self.current_cinema.get('cinemaShortName', '')
            
            # 保存账号
            result = save_account(account_data)
            
            if result:
                print(f"[账号控制器] 账号添加成功: {account_data.get('phone', 'N/A')}")
                
                # 重新加载账号列表
                self.load_account_list()
                
                # 发布账号添加事件
                event_bus.account_added.emit(account_data)
                
                return True
            else:
                self.account_error.emit("添加失败", "保存账号失败")
                return False
                
        except Exception as e:
            print(f"[账号控制器] 添加账号错误: {e}")
            self.account_error.emit("添加失败", f"添加账号失败: {str(e)}")
            return False
    
    def remove_account(self, phone: str) -> bool:
        """删除账号"""
        try:
            if not phone:
                self.account_error.emit("删除失败", "手机号不能为空")
                return False
            
            # 删除账号
            result = delete_account(phone)
            
            if result:
                print(f"[账号控制器] 账号删除成功: {phone}")
                
                # 如果删除的是当前账号，清空当前账号
                if self.current_account and self.current_account.get('phone') == phone:
                    self.current_account = None
                
                # 重新加载账号列表
                self.load_account_list()
                
                # 发布账号删除事件
                event_bus.account_removed.emit(phone)
                
                return True
            else:
                self.account_error.emit("删除失败", "删除账号失败")
                return False
                
        except Exception as e:
            print(f"[账号控制器] 删除账号错误: {e}")
            self.account_error.emit("删除失败", f"删除账号失败: {str(e)}")
            return False
    
    def get_current_account(self) -> Optional[dict]:
        """获取当前账号"""
        return self.current_account
    
    def get_account_list(self) -> List[dict]:
        """获取账号列表"""
        return self.account_list.copy()
    
    def find_account_by_phone(self, phone: str) -> Optional[dict]:
        """根据手机号查找账号"""
        for account in self.account_list:
            if account.get('phone') == phone:
                return account
        return None
