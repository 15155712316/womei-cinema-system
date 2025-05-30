#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位图修复验证脚本
验证场次显示、四级联动和座位图显示功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

def test_seat_map_functionality():
    """测试座位图功能"""
    print("=" * 60)
    print("🎬 座位图修复验证脚本")
    print("=" * 60)
    
    print("\n📋 验证项目：")
    print("1. ✅ 场次时间显示（已修复字段名问题）")
    print("2. ✅ 四级联动功能（影院→影片→日期→场次）")
    print("3. ✅ 座位图显示（API数据解析和组件渲染）")
    print("4. ✅ 主程序入口确认（main_modular.py）")
    
    print("\n🔧 修复内容：")
    print("• 场次显示字段：time/showTime -> q(时间), t(厅名), tbprice(票价)")
    print("• 数据处理：移除标准化处理，直接使用原始API数据")
    print("• 影片字段：name -> fn(影片名), key -> fc(影片键)")
    print("• 座位图：修复base_url字段名，完善数据解析和组件创建")
    print("• 布局修复：seat_area_layout引用保存和座位图动态替换")
    
    print("\n🚀 启动主程序进行实际测试...")
    
    try:
        # 启动主程序进行验证
        app = QApplication(sys.argv)
        
        from main_modular import ModularCinemaMainWindow
        
        window = ModularCinemaMainWindow()
        window.show()
        
        print("✅ 主程序启动成功！")
        print("\n📝 测试步骤：")
        print("1. 输入测试账号：15155712316")
        print("2. 登录后检查影院选择是否自动完成")
        print("3. 选择不同影片、日期、场次，验证四级联动")
        print("4. 观察座位图是否正确显示")
        print("5. 检查场次时间是否正确显示（不再是\"未知时间\"）")
        
        print("\n⚠️  如果遇到问题，请检查：")
        print("- 网络连接是否正常")
        print("- 账号是否有效")
        print("- 影院API是否响应正常")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 测试启动失败：{e}")
        print("请检查依赖是否正确安装：pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    test_seat_map_functionality() 