#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美影院系统适配实施方案
基于HAR文件分析结果，提供具体的代码修改方案
"""

import requests
import json
import urllib3
from typing import Dict, Any, Optional

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_womei_api_with_ssl_fix():
    """测试沃美API（修复SSL问题）"""
    print("=== 测试沃美API（修复SSL问题）===\n")
    
    # 使用HAR文件中的真实token
    real_token = "47794858a832916d8eda012e7cabd269"
    
    # 构建请求头（基于HAR文件）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'token': real_token,
        'accept': '*/*',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    
    # 测试城市列表API
    try:
        print("测试城市列表API...")
        url = "https://ct.womovie.cn/ticket/wmyc/citys/"
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        print(f"✓ 城市列表API调用成功")
        print(f"响应格式: ret={result.get('ret')}, msg={result.get('msg')}")
        
        # 分析城市数据结构
        data = result.get('data', {})
        if 'hot' in data:
            hot_cities = data['hot']
            print(f"热门城市数量: {len(hot_cities)}")
            if hot_cities:
                first_city = hot_cities[0]
                print(f"第一个城市: {first_city.get('city_name')}")
                cinemas = first_city.get('cinemas', [])
                print(f"该城市影院数量: {len(cinemas)}")
                if cinemas:
                    first_cinema = cinemas[0]
                    cinema_id = first_cinema.get('cinema_id')
                    print(f"第一个影院ID: {cinema_id}")
                    return cinema_id
        
    except Exception as e:
        print(f"✗ 城市列表API测试失败: {e}")
        return None

def generate_updated_adapter():
    """生成更新后的适配器代码"""
    print("\n=== 生成更新后的适配器代码 ===\n")
    
    updated_config = '''
# 更新后的沃美系统配置
WOMEI: {
    "system_name": "沃美连锁影院",
    "api_config": {
        "base_url": "https://ct.womovie.cn",
        "tenant_short": "wmyc",
        "channel_id": "40000",
        "client_version": "4.0",
        "wx_app_id": "wx4bb9342b9d97d53c",
        "default_token": "b0779d60d098e77e36cbae0545e8ddc3"
    },
    "endpoints": {
        # 基础端点（不需要cinema_id）
        "cities": "/ticket/{tenant_short}/citys/",
        
        # 影院相关端点（需要cinema_id）
        "cinema_info": "/ticket/{tenant_short}/cinema/{cinema_id}/info/",
        "movies": "/ticket/{tenant_short}/cinema/{cinema_id}/movies/",
        "shows": "/ticket/{tenant_short}/cinema/{cinema_id}/shows/",
        
        # 座位相关端点
        "hall_info": "/ticket/{tenant_short}/cinema/{cinema_id}/hall/info/",
        "hall_saleable": "/ticket/{tenant_short}/cinema/{cinema_id}/hall/saleable/",
        
        # 订单相关端点
        "order_ticket": "/ticket/{tenant_short}/cinema/{cinema_id}/order/ticket/",
        "order_info": "/ticket/{tenant_short}/cinema/{cinema_id}/order/info/",
        "order_change": "/ticket/{tenant_short}/cinema/{cinema_id}/order/change/",
        "order_vcc_list": "/ticket/{tenant_short}/cinema/{cinema_id}/order/vcc/list/",
        
        # 用户相关端点
        "user_info": "/ticket/{tenant_short}/cinema/{cinema_id}/user/info/",
        "user_cards": "/ticket/{tenant_short}/cinema/{cinema_id}/user/cards/",
        "user_vouchers": "/ticket/{tenant_short}/cinema/{cinema_id}/user/vouchers",
        "user_check_phone": "/ticket/{tenant_short}/user/check_phone/",
        
        # 会员相关端点
        "member_card": "/ticket/{tenant_short}/cinema/{cinema_id}/member/card/auto_solid/",
        
        # 广告相关端点
        "cinema_ads": "/ticket/{tenant_short}/cinema/{cinema_id}/ads/"
    }
}
'''
    
    print("1. 更新后的配置结构:")
    print(updated_config)
    
    updated_methods = '''
# 更新后的API方法
class CinemaAPIAdapter:
    def build_api_url(self, endpoint: str, cinema_id: str = None, **params) -> str:
        """构建API完整URL，支持cinema_id参数"""
        config = CinemaConfig.get_config(self.system_type)
        api_config = config["api_config"]
        endpoint_path = config["endpoints"].get(endpoint)
        
        if not endpoint_path:
            raise ValueError(f"不支持的接口端点: {endpoint}")
        
        # 替换路径中的占位符
        path = endpoint_path.format(
            tenant_short=api_config["tenant_short"],
            cinema_id=cinema_id or ""
        )
        
        url = f"{api_config['base_url']}{path}"
        
        # 添加查询参数
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
            if query_string:
                url += f"?{query_string}"
        
        return url
    
    def get_cinema_info(self, cinema_id: str) -> Dict[str, Any]:
        """获取影院信息"""
        url = self.build_api_url('cinema_info', cinema_id=cinema_id)
        headers = CinemaConfig.build_request_headers(self.system_type, self.token)
        response = self.session.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_movies(self, cinema_id: str) -> Dict[str, Any]:
        """获取影院电影列表"""
        url = self.build_api_url('movies', cinema_id=cinema_id)
        headers = CinemaConfig.build_request_headers(self.system_type, self.token)
        response = self.session.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_shows(self, cinema_id: str, movie_id: str) -> Dict[str, Any]:
        """获取电影场次列表"""
        url = self.build_api_url('shows', cinema_id=cinema_id, movie_id=movie_id)
        headers = CinemaConfig.build_request_headers(self.system_type, self.token)
        response = self.session.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    
    def get_hall_info(self, cinema_id: str, hall_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取影厅座位信息"""
        url = self.build_api_url('hall_info', cinema_id=cinema_id, 
                                hall_id=hall_id, schedule_id=schedule_id)
        headers = CinemaConfig.build_request_headers(self.system_type, self.token)
        response = self.session.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    
    def create_order(self, cinema_id: str, seatlable: str, schedule_id: str) -> Dict[str, Any]:
        """创建订单"""
        url = self.build_api_url('order_ticket', cinema_id=cinema_id)
        headers = CinemaConfig.build_request_headers(self.system_type, self.token)
        
        # 移除content-type让requests自动设置
        headers.pop('content-type', None)
        
        data = {
            'seatlable': seatlable,
            'schedule_id': schedule_id
        }
        
        response = self.session.post(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        return response.json()
'''
    
    print("2. 更新后的API方法:")
    print(updated_methods)

def create_implementation_plan():
    """创建实施计划"""
    print("\n=== 实施计划 ===\n")
    
    plan = {
        "阶段1": {
            "名称": "更新API适配器",
            "时间": "1天",
            "任务": [
                "更新cinema_api_adapter.py的端点配置",
                "修改build_api_url方法支持cinema_id参数",
                "添加新的API方法（get_cinema_info, get_shows等）",
                "修复SSL验证问题"
            ]
        },
        "阶段2": {
            "名称": "修改业务服务层",
            "时间": "2天", 
            "任务": [
                "更新services/film_service.py适配新的API结构",
                "修改services/cinema_manager.py支持cinema_id参数",
                "更新services/order_api.py的订单创建逻辑",
                "适配新的数据格式和响应结构"
            ]
        },
        "阶段3": {
            "名称": "更新主窗口逻辑",
            "时间": "2天",
            "任务": [
                "修改main_modular.py的业务流程",
                "确保cinema_id在各个步骤间正确传递",
                "更新UI组件的数据绑定",
                "适配新的API调用方式"
            ]
        },
        "阶段4": {
            "名称": "测试和优化",
            "时间": "1天",
            "任务": [
                "完整流程测试",
                "错误处理优化",
                "性能调优",
                "文档更新"
            ]
        }
    }
    
    for stage, details in plan.items():
        print(f"{stage}: {details['名称']} ({details['时间']})")
        for task in details['任务']:
            print(f"  - {task}")
        print()

def generate_specific_code_changes():
    """生成具体的代码修改建议"""
    print("=== 具体代码修改建议 ===\n")
    
    print("1. 修改cinema_api_adapter.py:")
    print("   - 在第49-55行更新WOMEI端点配置")
    print("   - 在第80-91行修改build_api_url方法")
    print("   - 在第135-203行添加新的API方法")
    
    print("\n2. 修改services/film_service.py:")
    print("   - 更新get_films函数，添加cinema_id参数")
    print("   - 修改API调用方式")
    
    print("\n3. 修改main_modular.py:")
    print("   - 在影院选择后保存cinema_id")
    print("   - 在后续API调用中传递cinema_id")
    
    print("\n4. 添加SSL验证禁用:")
    print("   - 在requests调用中添加verify=False")
    print("   - 或者配置SSL证书")

def main():
    """主函数"""
    print("沃美影院系统适配实施方案")
    print("=" * 50)
    
    # 测试API
    cinema_id = test_womei_api_with_ssl_fix()
    
    # 生成更新后的适配器
    generate_updated_adapter()
    
    # 创建实施计划
    create_implementation_plan()
    
    # 生成具体修改建议
    generate_specific_code_changes()
    
    print("\n总结:")
    print("1. HAR文件分析显示沃美系统API结构与现有配置有显著差异")
    print("2. 主要差异是大部分API需要cinema_id参数")
    print("3. 需要更新适配器配置和API方法")
    print("4. 建议分4个阶段实施，总计约6天完成")
    print("5. 关键是要先解决SSL验证问题，然后逐步适配API结构")

if __name__ == "__main__":
    main()
