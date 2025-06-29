#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的沃美券使用流程验证测试
基于HAR文件分析结果，验证券使用流程优化的可行性
"""

import requests
import json
import time
import urllib3
from typing import Dict, Any, Tuple
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompleteVoucherFlowTester:
    """完整券使用流程测试器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.cinema_id = "9934"  # 使用curl命令中的影院ID
        self.token = "afebc43f2b18da363fd78a6a10b01b72"  # 从curl命令中提取

        # 从HAR中提取的券码（使用第二张可用券）
        self.voucher_code = "GZJY01002948416827"

        # 使用curl命令中的座位和场次信息
        self.seat_info = "10013:5:7:33045901#04#06|10013:5:8:33045901#04#05"
        self.schedule_id = "16696816"
        
        # 当前订单ID（将在创建订单后更新）
        self.current_order_id = None
        
        # 请求头（与curl命令保持一致）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'token': self.token,
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
        
        # 测试结果记录
        self.test_results = {
            'order_creation': None,
            'dual_mode_test': None,
            'single_mode_test': None,
            'error_scenarios': None,
            'performance_comparison': None
        }
    
    def create_new_order(self) -> Dict[str, Any]:
        """创建新订单"""
        print("🎬 步骤1: 创建新订单")
        print("=" * 50)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/ticket/"
        
        # 使用HAR中第1个请求的参数
        data = {
            'seatlable': self.seat_info,
            'schedule_id': self.schedule_id
        }
        
        start_time = time.time()
        
        try:
            print(f"📤 请求URL: {url}")
            print(f"📤 请求参数: {data}")
            
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            print(f"📥 响应状态码: {response.status_code}")
            print(f"⏱️  响应时间: {response_time:.2f}ms")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    order_id = result.get('data', {}).get('order_id')
                    if order_id:
                        self.current_order_id = order_id
                        print(f"✅ 订单创建成功!")
                        print(f"   订单ID: {order_id}")
                        print(f"   服务器时间: {result.get('data', {}).get('server_time')}")
                        
                        self.test_results['order_creation'] = {
                            'success': True,
                            'order_id': order_id,
                            'response_time': response_time,
                            'data': result
                        }
                        return {'success': True, 'order_id': order_id, 'response_time': response_time}
                    else:
                        print(f"❌ 订单创建失败: 未获取到订单ID")
                        return {'success': False, 'error': '未获取到订单ID'}
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"❌ 订单创建失败: {error_msg}")
                    self.test_results['order_creation'] = {
                        'success': False,
                        'error': error_msg,
                        'response_time': response_time
                    }
                    return {'success': False, 'error': error_msg}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求异常: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return {'success': False, 'error': f'JSON decode error: {e}'}
    
    def test_dual_interface_mode(self) -> Dict[str, Any]:
        """测试双接口模式：先计算价格，再绑定券"""
        print("\n🔄 步骤2: 测试双接口模式")
        print("=" * 50)
        
        if not self.current_order_id:
            return {'success': False, 'error': '没有有效的订单ID'}
        
        # 第一步：计算券价格
        print("📋 第一步: 调用券价格计算接口")
        price_result = self._call_voucher_price_api()
        
        if not price_result['success']:
            return {
                'success': False,
                'error': '券价格计算失败',
                'price_result': price_result
            }
        
        # 等待一下，模拟用户查看价格的时间
        print("⏱️  等待2秒，模拟用户查看价格...")
        time.sleep(2)
        
        # 第二步：绑定券到订单
        print("📋 第二步: 调用订单修改接口绑定券")
        bind_result = self._call_order_change_api()
        
        total_time = price_result['response_time'] + bind_result.get('response_time', 0)
        
        result = {
            'success': bind_result['success'],
            'price_calculation': price_result,
            'voucher_binding': bind_result,
            'total_response_time': total_time,
            'request_count': 2
        }
        
        self.test_results['dual_mode_test'] = result
        
        print(f"📊 双接口模式结果:")
        print(f"   价格计算: {'✅ 成功' if price_result['success'] else '❌ 失败'}")
        print(f"   券绑定: {'✅ 成功' if bind_result['success'] else '❌ 失败'}")
        print(f"   总响应时间: {total_time:.2f}ms")
        print(f"   网络请求数: 2次")
        
        return result
    
    def test_single_interface_mode(self) -> Dict[str, Any]:
        """测试单接口模式：直接绑定券"""
        print("\n🚀 步骤3: 测试单接口模式")
        print("=" * 50)
        
        if not self.current_order_id:
            return {'success': False, 'error': '没有有效的订单ID'}
        
        print("📋 直接调用订单修改接口绑定券")
        bind_result = self._call_order_change_api()
        
        result = {
            'success': bind_result['success'],
            'voucher_binding': bind_result,
            'total_response_time': bind_result.get('response_time', 0),
            'request_count': 1
        }
        
        self.test_results['single_mode_test'] = result
        
        print(f"📊 单接口模式结果:")
        print(f"   券绑定: {'✅ 成功' if bind_result['success'] else '❌ 失败'}")
        print(f"   响应时间: {bind_result.get('response_time', 0):.2f}ms")
        print(f"   网络请求数: 1次")
        
        return result
    
    def _call_voucher_price_api(self) -> Dict[str, Any]:
        """调用券价格计算接口"""
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/voucher/price/"
        
        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.current_order_id
        }
        
        start_time = time.time()
        
        try:
            print(f"📤 券价格计算请求: {data}")
            
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"📥 响应状态码: {response.status_code}")
            print(f"⏱️  响应时间: {response_time:.2f}ms")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    data_info = result.get('data', {})
                    print(f"✅ 券价格计算成功:")
                    print(f"   手续费: {data_info.get('surcharge_price', 'N/A')}")
                    print(f"   支付金额: {data_info.get('pay_price', 'N/A')}")
                    print(f"   手续费说明: {data_info.get('surcharge_msg', 'N/A')}")
                    
                    return {
                        'success': True,
                        'response_time': response_time,
                        'data': result
                    }
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"❌ 券价格计算失败: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'response_time': response_time
                    }
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def _call_order_change_api(self) -> Dict[str, Any]:
        """调用订单修改接口"""
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/"
        
        # 使用HAR中第22个请求的参数
        data = {
            'order_id': self.current_order_id,
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'card_id': '',
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'use_rewards': 'Y',
            'use_limit_cards': 'N',
            'limit_cards': '[]',
            'voucher_code': self.voucher_code,
            'voucher_code_type': 'VGC_T',
            'ticket_pack_goods': ' '
        }
        
        start_time = time.time()
        
        try:
            print(f"📤 订单修改请求: {data}")
            
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"📥 响应状态码: {response.status_code}")
            print(f"⏱️  响应时间: {response_time:.2f}ms")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    data_info = result.get('data', {})
                    print(f"✅ 券绑定成功:")
                    print(f"   订单总价: {data_info.get('order_total_price', 'N/A')}")
                    print(f"   支付金额: {data_info.get('order_payment_price', 'N/A')}")
                    print(f"   券折扣: {data_info.get('voucher_discounts', 'N/A')}")
                    print(f"   券使用详情: {data_info.get('voucher_use', 'N/A')}")
                    
                    return {
                        'success': True,
                        'response_time': response_time,
                        'data': result
                    }
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"❌ 券绑定失败: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'response_time': response_time
                    }
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}

    def test_error_scenarios(self) -> Dict[str, Any]:
        """测试错误场景"""
        print("\n❌ 步骤4: 测试错误场景")
        print("=" * 50)

        if not self.current_order_id:
            return {'success': False, 'error': '没有有效的订单ID'}

        error_scenarios = [
            {'code': 'INVALID123456789', 'desc': '无效券码'},
            {'code': 'GZJY01002948425042', 'desc': '可能已使用的券码'},
            {'code': '', 'desc': '空券码'}
        ]

        results = []

        for scenario in error_scenarios:
            print(f"\n🧪 测试场景: {scenario['desc']}")

            url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/"

            data = {
                'order_id': self.current_order_id,
                'discount_id': '0',
                'discount_type': 'TP_VOUCHER' if scenario['code'] else '',
                'card_id': '',
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'use_rewards': 'Y',
                'use_limit_cards': 'N',
                'limit_cards': '[]',
                'voucher_code': scenario['code'],
                'voucher_code_type': 'VGC_T' if scenario['code'] else '',
                'ticket_pack_goods': ' '
            }

            start_time = time.time()

            try:
                response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)

                end_time = time.time()
                response_time = (end_time - start_time) * 1000

                if response.status_code == 200:
                    result = response.json()
                    print(f"📥 响应: ret={result.get('ret')}, msg={result.get('msg')}")

                    results.append({
                        'scenario': scenario['desc'],
                        'code': scenario['code'],
                        'success': result.get('ret') == 0,
                        'message': result.get('msg', ''),
                        'response_time': response_time,
                        'response': result
                    })
                else:
                    print(f"❌ HTTP请求失败: {response.status_code}")
                    results.append({
                        'scenario': scenario['desc'],
                        'code': scenario['code'],
                        'success': False,
                        'message': f'HTTP {response.status_code}',
                        'response_time': response_time,
                        'response': None
                    })

            except Exception as e:
                print(f"❌ 请求异常: {e}")
                results.append({
                    'scenario': scenario['desc'],
                    'code': scenario['code'],
                    'success': False,
                    'message': str(e),
                    'response_time': 0,
                    'response': None
                })

        self.test_results['error_scenarios'] = results
        return {'results': results}

    def analyze_performance_comparison(self):
        """分析性能对比"""
        print("\n📊 步骤5: 性能对比分析")
        print("=" * 50)

        dual_mode = self.test_results.get('dual_mode_test', {})
        single_mode = self.test_results.get('single_mode_test', {})

        if dual_mode and single_mode:
            dual_time = dual_mode.get('total_response_time', 0)
            single_time = single_mode.get('total_response_time', 0)

            time_saved = dual_time - single_time
            time_saved_percent = (time_saved / dual_time * 100) if dual_time > 0 else 0

            print(f"⏱️  响应时间对比:")
            print(f"   双接口模式: {dual_time:.2f}ms (2次请求)")
            print(f"   单接口模式: {single_time:.2f}ms (1次请求)")
            print(f"   时间节省: {time_saved:.2f}ms ({time_saved_percent:.1f}%)")

            print(f"\n🌐 网络请求对比:")
            print(f"   双接口模式: 2次请求")
            print(f"   单接口模式: 1次请求")
            print(f"   请求减少: 50%")

            # 数据完整性对比
            dual_has_price_preview = dual_mode.get('price_calculation', {}).get('success', False)
            single_has_complete_data = single_mode.get('voucher_binding', {}).get('success', False)

            print(f"\n📋 功能完整性对比:")
            print(f"   双接口模式:")
            print(f"     - 价格预览: {'✅ 支持' if dual_has_price_preview else '❌ 不支持'}")
            print(f"     - 用户确认: ✅ 支持")
            print(f"     - 错误处理: ✅ 分步处理")

            print(f"   单接口模式:")
            print(f"     - 价格预览: ❌ 不支持")
            print(f"     - 直接绑定: {'✅ 支持' if single_has_complete_data else '❌ 不支持'}")
            print(f"     - 错误处理: ✅ 统一处理")

            comparison_result = {
                'dual_mode_time': dual_time,
                'single_mode_time': single_time,
                'time_saved': time_saved,
                'time_saved_percent': time_saved_percent,
                'request_reduction': 50,
                'dual_mode_features': {
                    'price_preview': dual_has_price_preview,
                    'user_confirmation': True,
                    'step_by_step_error': True
                },
                'single_mode_features': {
                    'direct_binding': single_has_complete_data,
                    'unified_error_handling': True,
                    'faster_response': True
                }
            }

            self.test_results['performance_comparison'] = comparison_result
            return comparison_result
        else:
            print("❌ 无法进行性能对比，缺少测试数据")
            return None

    def generate_final_report(self):
        """生成最终报告"""
        print("\n📋 最终测试报告")
        print("=" * 60)

        # 测试概况
        order_success = self.test_results.get('order_creation', {}).get('success', False)
        dual_success = self.test_results.get('dual_mode_test', {}).get('success', False)
        single_success = self.test_results.get('single_mode_test', {}).get('success', False)

        print(f"🎯 测试概况:")
        print(f"   订单创建: {'✅ 成功' if order_success else '❌ 失败'}")
        print(f"   双接口模式: {'✅ 成功' if dual_success else '❌ 失败'}")
        print(f"   单接口模式: {'✅ 成功' if single_success else '❌ 失败'}")

        # 关键发现
        print(f"\n🔍 关键发现:")

        if single_success:
            single_data = self.test_results['single_mode_test']['voucher_binding']['data']['data']
            has_price_info = 'order_payment_price' in single_data
            has_voucher_info = 'voucher_use' in single_data

            print(f"   ✅ 单接口模式完全可行")
            print(f"   ✅ 包含完整价格信息: {'是' if has_price_info else '否'}")
            print(f"   ✅ 包含券使用详情: {'是' if has_voucher_info else '否'}")
            print(f"   ✅ 一次调用完成券绑定和价格计算")

        if dual_success and single_success:
            print(f"   ✅ 两种模式都可行，可根据需求选择")
        elif single_success:
            print(f"   💡 推荐使用单接口模式")
        elif dual_success:
            print(f"   💡 推荐使用双接口模式")
        else:
            print(f"   ❌ 两种模式都存在问题")

        # 性能分析
        perf_data = self.test_results.get('performance_comparison')
        if perf_data:
            print(f"\n⚡ 性能优势:")
            print(f"   响应时间节省: {perf_data['time_saved']:.2f}ms ({perf_data['time_saved_percent']:.1f}%)")
            print(f"   网络请求减少: {perf_data['request_reduction']}%")

        # 实施建议
        print(f"\n🚀 实施建议:")

        if single_success and dual_success:
            print(f"   📋 采用渐进式双模式方案:")
            print(f"     - 实现快速模式（单接口）提升性能")
            print(f"     - 保留预览模式（双接口）提升体验")
            print(f"     - 用户可选择偏好模式")
        elif single_success:
            print(f"   🚀 直接采用单接口模式:")
            print(f"     - 减少网络请求，提升响应速度")
            print(f"     - 简化错误处理逻辑")
            print(f"     - 降低实现复杂度")

        print(f"\n⚠️  注意事项:")
        print(f"   - 完善错误处理和用户反馈")
        print(f"   - 添加操作撤销机制")
        print(f"   - 进行充分的测试验证")

        return self.test_results

def main():
    """主函数"""
    print("🎬 沃美券使用流程完整验证测试")
    print("🎯 基于HAR文件分析结果，验证流程优化可行性")
    print("=" * 60)

    tester = CompleteVoucherFlowTester()

    print(f"🔧 测试配置:")
    print(f"   影院ID: {tester.cinema_id}")
    print(f"   券码: {tester.voucher_code}")
    print(f"   座位信息: {tester.seat_info}")
    print(f"   场次ID: {tester.schedule_id}")
    print(f"   Token: {tester.token[:20]}...")

    try:
        # 步骤1: 创建新订单
        order_result = tester.create_new_order()
        if not order_result['success']:
            print(f"❌ 订单创建失败，无法继续测试: {order_result['error']}")
            return

        # 步骤2: 测试双接口模式
        dual_result = tester.test_dual_interface_mode()

        # 步骤3: 测试单接口模式
        single_result = tester.test_single_interface_mode()

        # 步骤4: 测试错误场景
        error_result = tester.test_error_scenarios()

        # 步骤5: 性能对比分析
        tester.analyze_performance_comparison()

        # 生成最终报告
        final_report = tester.generate_final_report()

        # 保存测试结果
        with open('voucher_flow_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 测试结果已保存到: voucher_flow_test_results.json")

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
