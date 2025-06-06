#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 代码重构工具包
提供自动化重构脚本和工具类
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class CodeRefactoringToolkit:
    """代码重构工具包"""
    
    def __init__(self):
        self.backup_dir = f"backup_refactoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.refactoring_log = []
    
    def create_backup(self):
        """创建完整备份"""
        print("📦 创建项目备份...")
        
        try:
            # 创建备份目录
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 备份所有Python文件
            for file_path in Path(".").rglob("*.py"):
                if "backup_" not in str(file_path):
                    relative_path = file_path.relative_to(".")
                    backup_path = Path(self.backup_dir) / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)
            
            print(f"✅ 备份创建成功: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return False
    
    def remove_unused_imports(self, file_path: str):
        """移除未使用的导入"""
        print(f"🔧 处理文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 定义可能未使用的导入模式
            unused_imports = [
                r'from typing import Dict\n',
                r'import traceback\n',
                r'from PyQt5\.QtCore import QByteArray\n',
                r'from PyQt5\.QtGui import QPixmap\n(?!.*QPixmap)',
                r'import json\n(?!.*json\.)',
                r'import re\n(?!.*re\.)',
            ]
            
            removed_count = 0
            for pattern in unused_imports:
                if re.search(pattern, content, re.DOTALL):
                    # 检查是否真的未使用
                    import_match = re.search(r'(from .+ import |import )(.+)', pattern.replace('\\n', '').replace('\\', ''))
                    if import_match:
                        imported_item = import_match.group(2).strip()
                        # 简单检查：如果在导入语句后面没有使用，则删除
                        usage_pattern = rf'\b{imported_item}\b'
                        import_pos = content.find(import_match.group(0))
                        if import_pos != -1:
                            after_import = content[import_pos + len(import_match.group(0)):]
                            if not re.search(usage_pattern, after_import):
                                content = re.sub(pattern, '', content)
                                removed_count += 1
            
            if removed_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.refactoring_log.append({
                    'file': file_path,
                    'action': 'remove_unused_imports',
                    'count': removed_count,
                    'status': 'success'
                })
                print(f"  ✅ 移除 {removed_count} 个未使用导入")
            else:
                print(f"  ℹ️ 未发现需要移除的导入")
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            self.refactoring_log.append({
                'file': file_path,
                'action': 'remove_unused_imports',
                'error': str(e),
                'status': 'failed'
            })
    
    def create_ui_component_factory(self):
        """创建UI组件工厂类"""
        print("🏭 创建UI组件工厂...")
        
        factory_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件工厂类 - 统一UI组件创建
自动生成，用于减少UI组件创建的重复代码
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UIComponentFactory:
    """UI组件工厂类"""
    
    # 统一样式定义
    BUTTON_STYLE = """
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            font-size: 14px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """
    
    LABEL_STYLE = """
        QLabel {
            color: #333;
            font-size: 14px;
            padding: 4px;
        }
    """
    
    @staticmethod
    def create_styled_button(text: str, callback=None, style=None):
        """创建带样式的按钮"""
        button = QPushButton(text)
        button.setStyleSheet(style or UIComponentFactory.BUTTON_STYLE)
        if callback:
            button.clicked.connect(callback)
        return button
    
    @staticmethod
    def create_styled_label(text: str, alignment=Qt.AlignLeft, style=None):
        """创建带样式的标签"""
        label = QLabel(text)
        label.setAlignment(alignment)
        label.setStyleSheet(style or UIComponentFactory.LABEL_STYLE)
        return label
    
    @staticmethod
    def create_vertical_layout(widget=None, spacing=5, margins=(5, 5, 5, 5)):
        """创建垂直布局"""
        layout = QVBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        if widget:
            widget.setLayout(layout)
        return layout
    
    @staticmethod
    def create_horizontal_layout(widget=None, spacing=5, margins=(5, 5, 5, 5)):
        """创建水平布局"""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        if widget:
            widget.setLayout(layout)
        return layout
    
    @staticmethod
    def add_widgets_to_layout(layout, widgets, stretch_factors=None):
        """批量添加组件到布局"""
        for i, widget in enumerate(widgets):
            if stretch_factors and i < len(stretch_factors):
                layout.addWidget(widget, stretch_factors[i])
            else:
                layout.addWidget(widget)
    
    @staticmethod
    def create_group_box(title: str, layout_type='vertical'):
        """创建分组框"""
        group_box = QGroupBox(title)
        if layout_type == 'vertical':
            layout = UIComponentFactory.create_vertical_layout()
        else:
            layout = UIComponentFactory.create_horizontal_layout()
        group_box.setLayout(layout)
        return group_box, layout
'''
        
        try:
            with open('ui/ui_component_factory.py', 'w', encoding='utf-8') as f:
                f.write(factory_code)
            
            print("✅ UI组件工厂创建成功: ui/ui_component_factory.py")
            self.refactoring_log.append({
                'action': 'create_ui_factory',
                'file': 'ui/ui_component_factory.py',
                'status': 'success'
            })
            
        except Exception as e:
            print(f"❌ UI组件工厂创建失败: {e}")
            self.refactoring_log.append({
                'action': 'create_ui_factory',
                'error': str(e),
                'status': 'failed'
            })
    
    def create_data_utils(self):
        """创建数据处理工具类"""
        print("🛠️ 创建数据处理工具...")
        
        utils_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理工具类 - 统一数据处理逻辑
自动生成，用于减少数据处理的重复代码
"""

import json
from typing import Any, Dict, List, Optional, Union

class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def safe_get(data: Dict, key: str, default: Any = None, required_type: type = None) -> Any:
        """安全获取字典数据"""
        if not isinstance(data, dict) or key not in data:
            return default
        
        value = data[key]
        if value is None:
            return default
        
        if required_type and not isinstance(value, required_type):
            try:
                # 尝试类型转换
                if required_type == int:
                    return int(value)
                elif required_type == float:
                    return float(value)
                elif required_type == str:
                    return str(value)
                elif required_type == bool:
                    return bool(value)
                else:
                    return default
            except (ValueError, TypeError):
                return default
        
        return value
    
    @staticmethod
    def safe_get_nested(data: Dict, keys: List[str], default: Any = None) -> Any:
        """安全获取嵌套字典数据"""
        current = data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
    
    @staticmethod
    def parse_json_response(response_text: str, success_key: str = 'success') -> Optional[Dict]:
        """解析JSON响应"""
        try:
            result = json.loads(response_text)
            if isinstance(result, dict) and result.get(success_key):
                return result
            return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, List[str]]:
        """验证必需字段"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    def clean_dict(data: Dict, remove_none: bool = True, remove_empty: bool = True) -> Dict:
        """清理字典数据"""
        cleaned = {}
        for key, value in data.items():
            if remove_none and value is None:
                continue
            if remove_empty and value == '':
                continue
            cleaned[key] = value
        return cleaned
    
    @staticmethod
    def merge_dicts(*dicts: Dict) -> Dict:
        """合并多个字典"""
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result
    
    @staticmethod
    def format_price(price: Union[int, float, str], currency: str = '¥') -> str:
        """格式化价格显示"""
        try:
            if isinstance(price, str):
                price = float(price)
            return f"{currency}{price:.2f}"
        except (ValueError, TypeError):
            return f"{currency}0.00"
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """安全转换为整数"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
'''
        
        try:
            os.makedirs('utils', exist_ok=True)
            with open('utils/data_utils.py', 'w', encoding='utf-8') as f:
                f.write(utils_code)
            
            print("✅ 数据处理工具创建成功: utils/data_utils.py")
            self.refactoring_log.append({
                'action': 'create_data_utils',
                'file': 'utils/data_utils.py',
                'status': 'success'
            })
            
        except Exception as e:
            print(f"❌ 数据处理工具创建失败: {e}")
            self.refactoring_log.append({
                'action': 'create_data_utils',
                'error': str(e),
                'status': 'failed'
            })
    
    def create_error_handler(self):
        """创建错误处理装饰器"""
        print("🛡️ 创建错误处理工具...")
        
        error_handler_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理工具 - 统一错误处理逻辑
自动生成，用于减少错误处理的重复代码
"""

import functools
import traceback
from typing import Callable, Any, Optional
from PyQt5.QtWidgets import QMessageBox

class ErrorHandler:
    """错误处理工具类"""
    
    @staticmethod
    def show_error_message(title: str, message: str, parent=None):
        """显示错误消息"""
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def show_warning_message(title: str, message: str, parent=None):
        """显示警告消息"""
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_info_message(title: str, message: str, parent=None):
        """显示信息消息"""
        QMessageBox.information(parent, title, message)

def handle_exceptions(
    show_message: bool = True,
    message_title: str = "错误",
    default_return: Any = None,
    log_error: bool = True
):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    print(f"函数 {func.__name__} 发生异常: {e}")
                    print(f"异常详情: {traceback.format_exc()}")
                
                if show_message:
                    error_msg = f"操作失败: {str(e)}"
                    ErrorHandler.show_error_message(message_title, error_msg)
                
                return default_return
        return wrapper
    return decorator

def handle_api_errors(
    show_message: bool = True,
    default_return: Any = None
):
    """API错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ConnectionError as e:
                if show_message:
                    ErrorHandler.show_error_message("网络错误", f"网络连接失败: {e}")
                return default_return
            except TimeoutError as e:
                if show_message:
                    ErrorHandler.show_error_message("超时错误", f"请求超时: {e}")
                return default_return
            except Exception as e:
                if show_message:
                    ErrorHandler.show_error_message("API错误", f"API调用失败: {e}")
                return default_return
        return wrapper
    return decorator

def validate_data(required_fields: list = None):
    """数据验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 假设第一个参数是self，第二个是data
            if len(args) >= 2 and isinstance(args[1], dict):
                data = args[1]
                if required_fields:
                    missing_fields = [field for field in required_fields 
                                    if field not in data or data[field] is None]
                    if missing_fields:
                        error_msg = f"缺少必需字段: {', '.join(missing_fields)}"
                        ErrorHandler.show_warning_message("数据验证失败", error_msg)
                        return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
'''
        
        try:
            with open('utils/error_handler.py', 'w', encoding='utf-8') as f:
                f.write(error_handler_code)
            
            print("✅ 错误处理工具创建成功: utils/error_handler.py")
            self.refactoring_log.append({
                'action': 'create_error_handler',
                'file': 'utils/error_handler.py',
                'status': 'success'
            })
            
        except Exception as e:
            print(f"❌ 错误处理工具创建失败: {e}")
            self.refactoring_log.append({
                'action': 'create_error_handler',
                'error': str(e),
                'status': 'failed'
            })
    
    def generate_refactoring_report(self):
        """生成重构报告"""
        print("📊 生成重构报告...")
        
        report = f"""# 代码重构执行报告

## 执行时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 备份信息
- 备份目录: {self.backup_dir}
- 备份状态: {'✅ 成功' if os.path.exists(self.backup_dir) else '❌ 失败'}

## 重构操作记录
"""
        
        success_count = 0
        failed_count = 0
        
        for log_entry in self.refactoring_log:
            status_icon = "✅" if log_entry['status'] == 'success' else "❌"
            report += f"\n### {status_icon} {log_entry['action']}\n"
            
            if 'file' in log_entry:
                report += f"- 文件: {log_entry['file']}\n"
            
            if log_entry['status'] == 'success':
                success_count += 1
                if 'count' in log_entry:
                    report += f"- 处理数量: {log_entry['count']}\n"
            else:
                failed_count += 1
                if 'error' in log_entry:
                    report += f"- 错误信息: {log_entry['error']}\n"
        
        report += f"""
## 执行总结
- 成功操作: {success_count}
- 失败操作: {failed_count}
- 总体状态: {'✅ 成功' if failed_count == 0 else '⚠️ 部分成功' if success_count > 0 else '❌ 失败'}

## 后续建议
1. 验证核心功能是否正常
2. 运行完整测试套件
3. 检查新创建的工具类是否可用
4. 如有问题，可从备份目录恢复

## 回滚命令
```bash
# 完整回滚
rm -rf ./*.py
cp -r {self.backup_dir}/* .

# 部分回滚特定文件
cp {self.backup_dir}/specific_file.py .
```
"""
        
        try:
            with open('refactoring_report.md', 'w', encoding='utf-8') as f:
                f.write(report)
            
            print("✅ 重构报告生成成功: refactoring_report.md")
            
        except Exception as e:
            print(f"❌ 重构报告生成失败: {e}")
    
    def run_phase1_refactoring(self):
        """执行第一阶段重构：快速清理"""
        print("🚀 开始第一阶段重构：快速清理")
        print("=" * 50)
        
        # 创建备份
        if not self.create_backup():
            print("❌ 备份失败，停止重构")
            return False
        
        # 移除未使用导入
        main_file = "main_modular.py"
        if os.path.exists(main_file):
            self.remove_unused_imports(main_file)
        
        # 创建工具类
        self.create_ui_component_factory()
        self.create_data_utils()
        self.create_error_handler()
        
        # 生成报告
        self.generate_refactoring_report()
        
        print("\n🎉 第一阶段重构完成！")
        print("📋 请检查以下内容：")
        print("1. 主程序是否正常启动")
        print("2. 核心功能是否正常工作")
        print("3. 新创建的工具类是否可用")
        print("4. 查看 refactoring_report.md 了解详细信息")
        
        return True

def main():
    """主函数"""
    toolkit = CodeRefactoringToolkit()
    
    print("🎬 PyQt5电影票务管理系统 - 代码重构工具包")
    print("=" * 60)
    print("⚠️ 重要提醒：")
    print("1. 重构前请确保代码已提交到版本控制")
    print("2. 重构过程中会自动创建备份")
    print("3. 重构后请立即测试核心功能")
    print("4. 如有问题可使用备份快速回滚")
    print()
    
    confirm = input("确认开始重构？(输入 'yes' 继续): ")
    if confirm.lower() == 'yes':
        success = toolkit.run_phase1_refactoring()
        if success:
            print("\n✅ 重构工具包执行完成！")
        else:
            print("\n❌ 重构工具包执行失败！")
    else:
        print("❌ 重构已取消")

if __name__ == "__main__":
    main()
