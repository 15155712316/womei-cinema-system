import requests
import json
from .api_base import api_get

def get_member_info(account, cinemaid):
    """
    获取会员信息的服务函数 - 使用动态base_url
    参数：
        account: 账号信息字典
        cinemaid: 影院ID
    返回：
        dict: 会员信息
    """
    try:
        if not cinemaid:
            return None
            
        # 构建会员信息查询参数
        params = {
            'cinemaid': cinemaid,
            'userid': account.get('userid', ''),
            'openid': account.get('openid', ''),
            'token': account.get('token', ''),
            'pageNo': '1',
            'groupid': '',
            'cardno': account.get('cardno', ''),
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'source': '2'
        }
        
        print(f"[会员服务] 用户ID: {account.get('userid')}")
        
        # 调用会员卡列表接口
        result = api_get('MiniTicket/index.php/MiniMember/getMemcardList', cinemaid, params=params)
        
        if result and result.get('resultCode') == '0':
            result_data = result.get('resultData', {})
            
            # 解析会员信息
            member_info = {
                'userid': account.get('userid', ''),
                'cardno': result_data.get('cardno', ''),
                'balance': float(result_data.get('balance', 0)),
                'score': int(result_data.get('score', 0)),
                'is_member': bool(result_data.get('cardno', '')),
                'member_name': result_data.get('member_name', ''),
                'member_level': result_data.get('member_level', '')
            }
            
            if member_info['is_member']:
                pass

            return member_info
        else:
            print(f"[会员服务] 会员信息API调用失败: {result.get('resultDesc', '未知错误')}")
            # 返回基础信息
            return {
                'userid': account.get('userid', ''),
                'cardno': account.get('cardno', ''),
                'balance': account.get('balance', 0),
                'score': account.get('score', 0),
                'is_member': bool(account.get('cardno', ''))
            }
            
    except Exception as e:
        # 返回基础信息
        return {
            'userid': account.get('userid', ''),
            'cardno': account.get('cardno', ''),
            'balance': account.get('balance', 0),
            'score': account.get('score', 0),
            'is_member': bool(account.get('cardno', ''))
        }

# 为了兼容现有的导入语句，提供member_service函数
def member_service(account, cinemaid):
    """
    会员服务的主要入口函数，兼容现有导入。
    参数：
        account: 账号信息字典
        cinemaid: 影院ID
    返回：
        dict: 会员信息
    """
    return get_member_info(account, cinemaid)


class MemberService:
    """会员服务类，封装会员相关功能"""
    
    def __init__(self):
        pass
    
    def get_member_info(self, account, cinemaid):
        """获取会员信息"""
        return get_member_info(account, cinemaid) 