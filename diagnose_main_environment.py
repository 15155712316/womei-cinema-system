#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟主程序运行环境，诊断qrcode导入问题
"""

import sys
import os

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def simulate_main_imports():
    """模拟主程序的导入过程"""
    print_separator("模拟主程序导入过程")
    
    print("📋 开始模拟main_modular.py的导入...")
    
    # 模拟主程序中的关键导入
    imports_to_test = [
        "sys",
        "os", 
        "time",
        "PyQt5.QtWidgets",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "services.cinema_api",
        "services.order_api",
        "utils.signals",
        "ui.widgets.account_widget",
        "ui.widgets.tab_manager_widget",
        "utils.qrcode_generator"
    ]
    
    for module_name in imports_to_test:
        try:
            if module_name == "utils.qrcode_generator":
                print(f"\n🎯 重点测试: {module_name}")
                # 详细测试这个模块
                from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image
                print(f"✅ {module_name}: 导入成功")
                
                # 测试内部的qrcode导入
                print("   🔍 检查内部qrcode模块状态...")
                import utils.qrcode_generator as qg
                if hasattr(qg, 'QRCODE_AVAILABLE'):
                    print(f"   📋 QRCODE_AVAILABLE: {qg.QRCODE_AVAILABLE}")
                else:
                    print(f"   ❌ 未找到QRCODE_AVAILABLE属性")
                    
            else:
                __import__(module_name)
                print(f"✅ {module_name}: 导入成功")
        except ImportError as e:
            print(f"❌ {module_name}: 导入失败 - {e}")
        except Exception as e:
            print(f"⚠️ {module_name}: 其他错误 - {e}")

def test_qrcode_in_context():
    """在模拟的主程序上下文中测试qrcode"""
    print_separator("主程序上下文中的qrcode测试")
    
    # 模拟主程序中可能影响导入的操作
    print("📋 模拟主程序环境设置...")
    
    # 1. 检查当前的sys.path
    print(f"📋 当前sys.path长度: {len(sys.path)}")
    
    # 2. 尝试在不同的导入上下文中测试qrcode
    contexts = [
        "直接导入",
        "在函数中导入", 
        "在类中导入",
        "在异常处理中导入"
    ]
    
    for context in contexts:
        print(f"\n🔍 测试上下文: {context}")
        try:
            if context == "直接导入":
                import qrcode
                print(f"✅ {context}: 成功")
                
            elif context == "在函数中导入":
                def test_func():
                    import qrcode
                    return qrcode
                result = test_func()
                print(f"✅ {context}: 成功")
                
            elif context == "在类中导入":
                class TestClass:
                    def test_method(self):
                        import qrcode
                        return qrcode
                obj = TestClass()
                result = obj.test_method()
                print(f"✅ {context}: 成功")
                
            elif context == "在异常处理中导入":
                try:
                    raise Exception("测试")
                except:
                    import qrcode
                    print(f"✅ {context}: 成功")
                    
        except ImportError as e:
            print(f"❌ {context}: 失败 - {e}")
        except Exception as e:
            print(f"⚠️ {context}: 其他错误 - {e}")

def test_qrcode_generation():
    """测试二维码生成功能"""
    print_separator("二维码生成功能测试")
    
    try:
        from utils.qrcode_generator import generate_ticket_qrcode
        
        # 测试数据
        test_ticket_code = "TEST123456789"
        test_order_info = {
            'filmName': '测试影片',
            'cinemaName': '测试影院',
            'showTime': '2025-06-03 10:00',
            'hallName': '测试影厅',
            'seatInfo': '1排1座',
            'dsValidateCode': test_ticket_code
        }
        
        print(f"📋 测试生成二维码...")
        print(f"📋 取票码: {test_ticket_code}")
        
        qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
        
        if qr_bytes:
            print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
        else:
            print(f"❌ 二维码生成失败: 返回None")
            
    except Exception as e:
        print(f"❌ 二维码生成测试失败: {e}")
        import traceback
        traceback.print_exc()

def check_module_loading_order():
    """检查模块加载顺序的影响"""
    print_separator("模块加载顺序影响分析")
    
    print("📋 检查已加载的模块...")
    loaded_modules = list(sys.modules.keys())
    
    qrcode_related = [name for name in loaded_modules if 'qrcode' in name.lower()]
    pil_related = [name for name in loaded_modules if 'pil' in name.lower()]
    
    print(f"📋 已加载的qrcode相关模块: {qrcode_related}")
    print(f"📋 已加载的PIL相关模块: {pil_related}")
    
    # 检查是否有模块冲突
    if 'qrcode' in sys.modules:
        qrcode_module = sys.modules['qrcode']
        print(f"📋 qrcode模块来源: {qrcode_module.__file__}")
    
    # 检查utils.qrcode_generator的状态
    if 'utils.qrcode_generator' in sys.modules:
        qg_module = sys.modules['utils.qrcode_generator']
        print(f"📋 utils.qrcode_generator已加载")
        if hasattr(qg_module, 'QRCODE_AVAILABLE'):
            print(f"📋 QRCODE_AVAILABLE状态: {qg_module.QRCODE_AVAILABLE}")

def main():
    """主函数"""
    print("🔍 开始主程序环境模拟诊断")
    print(f"⏰ 诊断时间: {__import__('datetime').datetime.now()}")
    print(f"📋 Python解释器: {sys.executable}")
    print(f"📋 工作目录: {os.getcwd()}")
    
    simulate_main_imports()
    test_qrcode_in_context()
    test_qrcode_generation()
    check_module_loading_order()
    
    print_separator("模拟诊断完成")
    print("📋 如果此处所有测试都成功，说明问题可能出现在主程序的特定运行时刻")

if __name__ == "__main__":
    main()
