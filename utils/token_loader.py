#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的Token加载工具
确保所有token都从accounts.json文件加载，不使用硬编码token
"""

import json
import os
from typing import Optional, Dict, Any


class TokenLoader:
    """Token加载器 - 统一从accounts.json文件加载token"""
    
    @staticmethod
    def get_accounts_file_path() -> str:
        """获取accounts.json文件路径"""
        # 从当前文件位置向上查找data目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)  # 上一级目录
        accounts_file = os.path.join(project_root, 'data', 'accounts.json')
        
        if not os.path.exists(accounts_file):
            raise FileNotFoundError(f"accounts.json文件不存在: {accounts_file}")
        
        return accounts_file
    
    @staticmethod
    def load_accounts() -> list:
        """加载所有账号信息"""
        accounts_file = TokenLoader.get_accounts_file_path()
        
        try:
            with open(accounts_file, "r", encoding="utf-8") as f:
                accounts = json.load(f)
            
            if not isinstance(accounts, list):
                raise ValueError("accounts.json格式错误：应该是账号列表")
            
            if not accounts:
                raise ValueError("accounts.json为空，请添加账号信息")
            
            return accounts
            
        except json.JSONDecodeError as e:
            raise ValueError(f"accounts.json格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载accounts.json失败: {e}")
    
    @staticmethod
    def get_current_token() -> str:
        """获取当前有效的token（第一个账号的token）"""
        accounts = TokenLoader.load_accounts()
        
        if not accounts or len(accounts) == 0:
            raise ValueError("没有可用的账号信息")
        
        first_account = accounts[0]
        token = first_account.get('token')
        
        if not token:
            raise ValueError("第一个账号缺少token信息")
        
        return token
    
    @staticmethod
    def get_current_account() -> Dict[str, Any]:
        """获取当前账号的完整信息"""
        accounts = TokenLoader.load_accounts()
        
        if not accounts or len(accounts) == 0:
            raise ValueError("没有可用的账号信息")
        
        return accounts[0]
    
    @staticmethod
    def get_account_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """根据手机号获取账号信息"""
        accounts = TokenLoader.load_accounts()
        
        for account in accounts:
            if account.get('phone') == phone:
                return account
        
        return None
    
    @staticmethod
    def get_token_by_phone(phone: str) -> Optional[str]:
        """根据手机号获取token"""
        account = TokenLoader.get_account_by_phone(phone)
        
        if account:
            return account.get('token')
        
        return None
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """验证token格式是否正确"""
        if not token:
            return False
        
        # 检查token长度和格式（32位十六进制字符串）
        if len(token) != 32:
            return False
        
        try:
            int(token, 16)  # 尝试解析为十六进制
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_validated_token() -> str:
        """获取经过验证的token"""
        token = TokenLoader.get_current_token()
        
        if not TokenLoader.validate_token(token):
            raise ValueError(f"Token格式无效: {token}")
        
        return token


# 便捷函数
def load_current_token() -> str:
    """加载当前token的便捷函数"""
    return TokenLoader.get_current_token()


def load_current_account() -> Dict[str, Any]:
    """加载当前账号的便捷函数"""
    return TokenLoader.get_current_account()


def load_token_by_phone(phone: str) -> Optional[str]:
    """根据手机号加载token的便捷函数"""
    return TokenLoader.get_token_by_phone(phone)


# 使用示例
if __name__ == "__main__":
    try:
        # 加载当前token
        token = load_current_token()
        print(f"✅ 成功加载token: {token[:20]}...")
        
        # 加载当前账号
        account = load_current_account()
        print(f"✅ 当前账号: {account.get('phone')}")
        
        # 验证token格式
        if TokenLoader.validate_token(token):
            print("✅ Token格式验证通过")
        else:
            print("❌ Token格式验证失败")
            
    except Exception as e:
        print(f"❌ 加载失败: {e}")
