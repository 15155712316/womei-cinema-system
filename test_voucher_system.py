#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券管理系统测试脚本
测试券API接口和数据处理功能
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.voucher_api import get_voucher_api, get_user_vouchers, get_valid_vouchers, search_vouchers
from services.voucher_service import get_voucher_service
from utils.voucher_utils import get_voucher_processor, get_voucher_formatter
from utils.data_utils import DataUtils

class VoucherSystemTester:
    """券系统测试器"""
    
    def __init__(self):
        self.voucher_api = get_voucher_api()
        self.voucher_service = get_voucher_service()
        self.voucher_processor = get_voucher_processor()
        self.voucher_formatter = get_voucher_formatter()
        self.data_utils = DataUtils()
        
        # 从accounts.json加载测试账号
        self.test_account = self._load_test_account()
        self.cinema_id = "400028"  # 测试影院ID
    
    def _load_test_account(self) -> dict:
        """加载测试账号"""
        try:
            accounts_file = "data/accounts.json"
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                    if accounts and len(accounts) > 0:
                        return accounts[0]
            
            # 如果没有找到账号文件，使用默认测试账号
            return {
                "phone": "15155712316",
                "token": "c33d6b500b34c87b71ac8fad4cfb6769"
            }
        except Exception as e:
            print(f"加载测试账号失败: {e}")
            return {
                "phone": "15155712316",
                "token": "c33d6b500b34c87b71ac8fad4cfb6769"
            }
    
    def test_basic_voucher_api(self):
        """测试基础券API功能"""
        print("=" * 60)
        print("🧪 测试基础券API功能")
        print("=" * 60)
        
        token = self.test_account['token']
        
        # 测试获取单页券数据
        print("\n1. 测试获取单页券数据...")
        result = self.voucher_service.get_vouchers_page(self.cinema_id, token, page_index=1)
        
        if result.get('ret') == 0:
            data = result.get('data', {})
            page_info = data.get('page', {})
            vouchers = data.get('result', [])
            
            print(f"✅ 获取成功")
            print(f"   总数据: {page_info.get('data_total', 0)} 条")
            print(f"   总页数: {page_info.get('total_page', 0)} 页")
            print(f"   当前页: {page_info.get('page_num', 0)} 页")
            print(f"   本页数据: {len(vouchers)} 条")
            
            if vouchers:
                first_voucher = vouchers[0]
                print(f"   第一张券: {first_voucher.get('voucher_name')} ({first_voucher.get('voucher_code_mask')})")
                print(f"   券状态: {first_voucher.get('status')}")
        else:
            print(f"❌ 获取失败: {result.get('msg')}")
    
    def test_all_vouchers_retrieval(self):
        """测试获取所有券数据"""
        print("\n2. 测试获取所有券数据...")
        
        token = self.test_account['token']
        
        start_time = time.time()
        vouchers, page_info = self.voucher_service.get_all_vouchers(self.cinema_id, token)
        end_time = time.time()
        
        print(f"✅ 获取完成，耗时: {end_time - start_time:.2f}秒")
        print(f"   总券数: {len(vouchers)} 张")
        print(f"   总页数: {page_info.get('total_page', 0)} 页")
        
        # 统计券状态
        valid_count = len([v for v in vouchers if v.is_valid()])
        expired_count = len([v for v in vouchers if v.is_expired()])
        disabled_count = len([v for v in vouchers if v.status == "DISABLED"])
        
        print(f"   有效券: {valid_count} 张")
        print(f"   过期券: {expired_count} 张")
        print(f"   作废券: {disabled_count} 张")
        
        return vouchers
    
    def test_voucher_filtering(self, vouchers):
        """测试券过滤功能"""
        print("\n3. 测试券过滤功能...")
        
        # 测试只获取有效券
        valid_vouchers = self.voucher_service.filter_vouchers(
            vouchers, status_filter="UN_USE", expired_filter=False
        )
        print(f"   有效券过滤: {len(valid_vouchers)} 张")
        
        # 测试按名称过滤
        guangzhou_vouchers = self.voucher_service.filter_vouchers(
            vouchers, name_filter="广州"
        )
        print(f"   广州券过滤: {len(guangzhou_vouchers)} 张")
        
        # 测试按券类型过滤
        tianjin_vouchers = self.voucher_service.filter_vouchers(
            vouchers, name_filter="天津"
        )
        print(f"   天津券过滤: {len(tianjin_vouchers)} 张")
        
        return valid_vouchers
    
    def test_voucher_statistics(self, vouchers):
        """测试券统计功能"""
        print("\n4. 测试券统计功能...")
        
        statistics = self.voucher_service.get_voucher_statistics(vouchers)
        
        print(f"   总券数: {statistics['total_count']}")
        print(f"   有效券: {statistics['valid_count']}")
        print(f"   已使用: {statistics['used_count']}")
        print(f"   已作废: {statistics['disabled_count']}")
        print(f"   有效率: {statistics['valid_rate']}%")
        
        # 显示按名称分组的统计
        print("\n   按券名称分组统计:")
        name_stats = statistics['name_statistics']
        for name, stats in name_stats.items():
            print(f"     {name}: 总数{stats['total']}, 有效{stats['valid']}, 作废{stats['disabled']}")
    
    def test_voucher_data_processing(self, vouchers):
        """测试券数据处理功能"""
        print("\n5. 测试券数据处理功能...")
        
        if not vouchers:
            print("   没有券数据可供测试")
            return
        
        # 测试券类型解析
        first_voucher = vouchers[0]
        voucher_type = self.voucher_processor.parse_voucher_type_from_code(first_voucher.voucher_code)
        print(f"   券类型解析: {first_voucher.voucher_code} -> {voucher_type}")
        
        # 测试过期状态
        status_text, color = self.voucher_processor.get_expire_status_text(first_voucher.expire_time)
        print(f"   过期状态: {status_text} (颜色: {color})")
        
        # 测试券分组
        grouped = self.voucher_processor.group_vouchers_by_type(vouchers)
        print(f"   券分组结果: {list(grouped.keys())}")
        
        # 测试券排序
        sorted_vouchers = self.voucher_processor.sort_vouchers_by_priority(vouchers[:10])
        print(f"   排序测试: 前10张券已按优先级排序")
        
        # 测试券摘要
        summary = self.voucher_processor.extract_voucher_summary(vouchers)
        print(f"   券摘要: 总数{summary['total']}, 有效{summary['valid']}, 即将过期{summary['expiring_soon']}")
    
    def test_voucher_display_formatting(self, vouchers):
        """测试券显示格式化"""
        print("\n6. 测试券显示格式化...")
        
        if not vouchers:
            print("   没有券数据可供测试")
            return
        
        # 测试卡片格式化
        first_voucher = vouchers[0]
        card_text = self.voucher_formatter.format_voucher_card_text(first_voucher)
        print("   券卡片格式:")
        for line in card_text.split('\n'):
            print(f"     {line}")
        
        # 测试列表项格式化
        list_item = self.voucher_formatter.format_voucher_list_item(first_voucher)
        print(f"   列表项格式: {list_item}")
    
    def test_api_endpoints(self):
        """测试API端点"""
        print("\n7. 测试API端点...")
        
        token = self.test_account['token']
        
        # 测试获取用户券列表API
        result = get_user_vouchers(self.cinema_id, token)
        if result['success']:
            voucher_count = len(result['data']['vouchers'])
            print(f"   ✅ 用户券列表API: 获取到 {voucher_count} 张券")
        else:
            print(f"   ❌ 用户券列表API失败: {result['message']}")
        
        # 测试获取有效券API
        result = get_valid_vouchers(self.cinema_id, token)
        if result['success']:
            valid_count = len(result['data']['vouchers'])
            print(f"   ✅ 有效券API: 获取到 {valid_count} 张有效券")
        else:
            print(f"   ❌ 有效券API失败: {result['message']}")
        
        # 测试搜索券API
        result = search_vouchers(self.cinema_id, token, "广州")
        if result['success']:
            search_count = result['data']['total_found']
            print(f"   ✅ 搜索券API: 找到 {search_count} 张包含'广州'的券")
        else:
            print(f"   ❌ 搜索券API失败: {result['message']}")
    
    def test_voucher_validation(self):
        """测试券验证功能"""
        print("\n8. 测试券验证功能...")
        
        token = self.test_account['token']
        
        # 先获取一张券进行验证测试
        vouchers, _ = self.voucher_service.get_all_vouchers(self.cinema_id, token)
        
        if vouchers:
            test_voucher = vouchers[0]
            from api.voucher_api import validate_voucher_for_order
            
            result = validate_voucher_for_order(self.cinema_id, token, test_voucher.voucher_code)
            
            if result['success']:
                validation_data = result['data']
                print(f"   ✅ 券验证成功")
                print(f"     券号: {validation_data['voucher_code']}")
                print(f"     券名: {validation_data['voucher_name']}")
                print(f"     状态: {validation_data['status']}")
                print(f"     有效: {'是' if validation_data['valid'] else '否'}")
                if validation_data['reasons']:
                    print(f"     失败原因: {', '.join(validation_data['reasons'])}")
            else:
                print(f"   ❌ 券验证失败: {result['message']}")
        else:
            print("   没有券可供验证测试")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始券管理系统测试")
        print(f"测试账号: {self.test_account['phone']}")
        print(f"测试影院: {self.cinema_id}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 基础API测试
            self.test_basic_voucher_api()
            
            # 获取所有券数据
            vouchers = self.test_all_vouchers_retrieval()
            
            # 过滤功能测试
            valid_vouchers = self.test_voucher_filtering(vouchers)
            
            # 统计功能测试
            self.test_voucher_statistics(vouchers)
            
            # 数据处理测试
            self.test_voucher_data_processing(vouchers)
            
            # 显示格式化测试
            self.test_voucher_display_formatting(valid_vouchers if valid_vouchers else vouchers)
            
            # API端点测试
            self.test_api_endpoints()
            
            # 券验证测试
            self.test_voucher_validation()
            
            print("\n" + "=" * 60)
            print("🎉 所有测试完成！")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    tester = VoucherSystemTester()
    tester.run_all_tests()
