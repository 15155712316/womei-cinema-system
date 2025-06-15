#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美影院系统的城市和影院自动选择功能
验证六级联动的自动选择机制
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import Qt, QTimer

def main():
    """主函数"""
    print("🚀 沃美影院系统自动选择功能测试")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 导入主窗口
    from main_modular import MainWindow
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    print(f"\n✅ 主窗口已启动")
    print(f"🎯 测试要点:")
    print(f"  1. 城市数据加载后自动选择第一个城市")
    print(f"  2. 影院数据加载后自动选择第一个影院")
    print(f"  3. 电影数据加载后自动选择第一个电影")
    print(f"  4. 日期数据加载后自动选择第一个日期")
    print(f"  5. 验证六级联动的顺序执行")
    
    print(f"\n📋 预期流程:")
    print(f"  启动 → 加载城市 → 自动选择城市 → 加载影院 → 自动选择影院")
    print(f"       → 加载电影 → 自动选择电影 → 加载日期 → 自动选择日期")
    print(f"       → 加载场次 → 等待用户选择场次 → 加载座位图")
    
    print(f"\n🔍 观察要点:")
    print(f"  - 查看控制台输出中的自动选择日志")
    print(f"  - 观察下拉框的自动更新和选择")
    print(f"  - 验证联动的时序是否正确")
    print(f"  - 确认最终能够正常加载座位图")
    
    # 创建一个简单的状态监控窗口
    class AutoSelectionMonitor(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("自动选择功能监控")
            self.setGeometry(1200, 100, 400, 600)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout(central_widget)
            
            # 标题
            title = QLabel("🔍 自动选择功能监控")
            title.setStyleSheet("""
                QLabel {
                    font: bold 16px "Microsoft YaHei";
                    color: #333;
                    padding: 10px;
                    background-color: #f0f8ff;
                    border-radius: 6px;
                    margin: 5px;
                }
            """)
            layout.addWidget(title)
            
            # 状态显示
            self.status_text = QTextEdit()
            self.status_text.setStyleSheet("""
                QTextEdit {
                    font: 10px "Consolas";
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
            """)
            layout.addWidget(self.status_text)
            
            # 控制按钮
            self.refresh_btn = QPushButton("刷新状态")
            self.refresh_btn.clicked.connect(self.refresh_status)
            self.refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font: bold 11px "Microsoft YaHei";
                }
                QPushButton:hover {
                    background-color: #1976d2;
                }
            """)
            layout.addWidget(self.refresh_btn)
            
            # 定时刷新状态
            self.timer = QTimer()
            self.timer.timeout.connect(self.refresh_status)
            self.timer.start(2000)  # 每2秒刷新一次
            
            self.main_window = window
            self.refresh_status()
        
        def refresh_status(self):
            """刷新状态显示"""
            try:
                status_info = []
                current_time = time.strftime("%H:%M:%S")
                status_info.append(f"[{current_time}] 状态检查")
                status_info.append("=" * 40)
                
                # 检查Tab管理器状态
                if hasattr(self.main_window, 'tab_manager_widget'):
                    tab_manager = self.main_window.tab_manager_widget
                    
                    # 城市状态
                    if hasattr(tab_manager, 'city_combo'):
                        city_count = tab_manager.city_combo.count()
                        city_current = tab_manager.city_combo.currentText()
                        city_enabled = tab_manager.city_combo.isEnabled()
                        status_info.append(f"🏙️ 城市: {city_current}")
                        status_info.append(f"   选项数: {city_count}, 启用: {city_enabled}")
                    
                    # 影院状态
                    if hasattr(tab_manager, 'cinema_combo'):
                        cinema_count = tab_manager.cinema_combo.count()
                        cinema_current = tab_manager.cinema_combo.currentText()
                        cinema_enabled = tab_manager.cinema_combo.isEnabled()
                        status_info.append(f"🏢 影院: {cinema_current}")
                        status_info.append(f"   选项数: {cinema_count}, 启用: {cinema_enabled}")
                    
                    # 电影状态
                    if hasattr(tab_manager, 'movie_combo'):
                        movie_count = tab_manager.movie_combo.count()
                        movie_current = tab_manager.movie_combo.currentText()
                        movie_enabled = tab_manager.movie_combo.isEnabled()
                        status_info.append(f"🎬 电影: {movie_current}")
                        status_info.append(f"   选项数: {movie_count}, 启用: {movie_enabled}")
                    
                    # 日期状态
                    if hasattr(tab_manager, 'date_combo'):
                        date_count = tab_manager.date_combo.count()
                        date_current = tab_manager.date_combo.currentText()
                        date_enabled = tab_manager.date_combo.isEnabled()
                        status_info.append(f"📅 日期: {date_current}")
                        status_info.append(f"   选项数: {date_count}, 启用: {date_enabled}")
                    
                    # 场次状态
                    if hasattr(tab_manager, 'session_combo'):
                        session_count = tab_manager.session_combo.count()
                        session_current = tab_manager.session_combo.currentText()
                        session_enabled = tab_manager.session_combo.isEnabled()
                        status_info.append(f"🎭 场次: {session_current}")
                        status_info.append(f"   选项数: {session_count}, 启用: {session_enabled}")
                    
                    # 数据状态
                    status_info.append("")
                    status_info.append("📊 数据状态:")
                    if hasattr(tab_manager, 'cities_data'):
                        cities_count = len(tab_manager.cities_data) if tab_manager.cities_data else 0
                        status_info.append(f"   城市数据: {cities_count} 个")
                    
                    if hasattr(tab_manager, 'cinemas_data'):
                        cinemas_count = len(tab_manager.cinemas_data) if tab_manager.cinemas_data else 0
                        status_info.append(f"   影院数据: {cinemas_count} 个")
                    
                    if hasattr(tab_manager, 'current_movies'):
                        movies_count = len(tab_manager.current_movies) if tab_manager.current_movies else 0
                        status_info.append(f"   电影数据: {movies_count} 个")
                
                else:
                    status_info.append("❌ Tab管理器未找到")
                
                # 更新显示
                self.status_text.clear()
                self.status_text.append("\n".join(status_info))
                
                # 自动滚动到底部
                cursor = self.status_text.textCursor()
                cursor.movePosition(cursor.End)
                self.status_text.setTextCursor(cursor)
                
            except Exception as e:
                self.status_text.append(f"❌ 状态检查错误: {e}")
    
    # 创建监控窗口
    monitor = AutoSelectionMonitor()
    monitor.show()
    
    print(f"\n📊 监控窗口已启动")
    print(f"💡 使用说明:")
    print(f"  - 主窗口：正常的沃美影院系统界面")
    print(f"  - 监控窗口：实时显示各级选择状态")
    print(f"  - 控制台：查看详细的自动选择日志")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
