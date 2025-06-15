#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Tab管理器初始化和城市加载
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from ui.widgets.tab_manager_widget import TabManagerWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab管理器测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建Tab管理器
        print("🚀 创建Tab管理器...")
        self.tab_manager = TabManagerWidget()
        layout.addWidget(self.tab_manager)
        
        # 延迟检查城市下拉框状态
        QTimer.singleShot(2000, self.check_city_combo_state)
        QTimer.singleShot(5000, self.check_city_combo_final_state)
    
    def check_city_combo_state(self):
        """检查城市下拉框状态（2秒后）"""
        try:
            print("\n🔍 检查城市下拉框状态（2秒后）:")
            
            if hasattr(self.tab_manager, 'city_combo'):
                combo = self.tab_manager.city_combo
                print(f"  - 下拉框项目数: {combo.count()}")
                print(f"  - 启用状态: {combo.isEnabled()}")
                print(f"  - 当前文本: '{combo.currentText()}'")
                
                # 显示所有项目
                for i in range(combo.count()):
                    item_text = combo.itemText(i)
                    print(f"  - 项目 {i}: '{item_text}'")
                    
                # 检查城市数据
                if hasattr(self.tab_manager, 'cities_data'):
                    cities_count = len(self.tab_manager.cities_data)
                    print(f"  - 城市数据数量: {cities_count}")
                    
                    if cities_count > 0:
                        first_city = self.tab_manager.cities_data[0]
                        city_name = first_city.get('city_name', '未知')
                        print(f"  - 第一个城市: {city_name}")
                else:
                    print(f"  - 城市数据: 未找到cities_data属性")
            else:
                print("  - ❌ 未找到city_combo属性")
                
        except Exception as e:
            print(f"❌ 检查城市下拉框状态失败: {e}")
            import traceback
            traceback.print_exc()
    
    def check_city_combo_final_state(self):
        """检查城市下拉框最终状态（5秒后）"""
        try:
            print("\n🎯 检查城市下拉框最终状态（5秒后）:")
            
            if hasattr(self.tab_manager, 'city_combo'):
                combo = self.tab_manager.city_combo
                print(f"  - 最终项目数: {combo.count()}")
                print(f"  - 最终启用状态: {combo.isEnabled()}")
                print(f"  - 最终当前文本: '{combo.currentText()}'")
                
                if combo.count() > 1:
                    print("✅ 城市下拉框加载成功！")
                    
                    # 尝试选择第一个城市进行测试
                    if combo.count() > 1:
                        print("🧪 测试选择第一个城市...")
                        combo.setCurrentIndex(1)  # 选择第一个城市（索引0是"请选择城市"）
                        print(f"  - 选择的城市: '{combo.currentText()}'")
                else:
                    print("❌ 城市下拉框加载失败！")
                    
                    # 诊断问题
                    print("\n🔍 问题诊断:")
                    print("  - 检查控制台是否有'[Tab管理器] 🚀 初始化沃美影院联动系统'")
                    print("  - 检查控制台是否有'[城市调试] ==================== 开始加载沃美城市列表'")
                    print("  - 检查控制台是否有API响应成功的日志")
                    print("  - 检查控制台是否有'[城市调试] ✅ 城市下拉框更新完成'")
            else:
                print("  - ❌ 未找到city_combo属性")
                
        except Exception as e:
            print(f"❌ 检查城市下拉框最终状态失败: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("🚀 开始Tab管理器初始化测试")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("✅ 测试窗口已显示")
    print("⏳ 等待Tab管理器初始化...")
    print("📋 观察控制台输出，查找城市加载相关日志")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
