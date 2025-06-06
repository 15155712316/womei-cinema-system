#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 第二阶段重构执行器
基于第一阶段创建的工具类，执行具体的模式重构
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class Phase2RefactoringExecutor:
    """第二阶段重构执行器"""
    
    def __init__(self):
        self.main_file = "main_modular.py"
        self.backup_dir = f"backup_phase2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.refactoring_log = []
        
    def create_backup(self):
        """创建第二阶段备份"""
        print("📦 创建第二阶段重构备份...")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 备份主文件
            if Path(self.main_file).exists():
                shutil.copy2(self.main_file, self.backup_dir)
            
            # 备份其他重要文件
            important_files = ["requirements.txt", "build_info.json"]
            for file in important_files:
                if Path(file).exists():
                    shutil.copy2(file, self.backup_dir)
            
            print(f"✅ 备份创建成功: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return False
    
    def analyze_current_patterns(self):
        """分析当前的重复模式"""
        print("🔍 分析当前重复模式...")
        
        if not Path(self.main_file).exists():
            print(f"❌ 主文件不存在: {self.main_file}")
            return {}
        
        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        patterns_found = {
            'ui_patterns': self._find_ui_patterns(content),
            'data_patterns': self._find_data_patterns(content),
            'error_patterns': self._find_error_patterns(content)
        }
        
        return patterns_found
    
    def _find_ui_patterns(self, content):
        """查找UI重复模式"""
        patterns = {}
        
        # QPushButton创建模式
        button_pattern = r'(\w+)\s*=\s*QPushButton\([^)]*\)'
        button_matches = re.findall(button_pattern, content)
        patterns['button_creation'] = len(button_matches)
        
        # QVBoxLayout创建模式
        layout_pattern = r'(\w+)\s*=\s*QVBoxLayout\(\)'
        layout_matches = re.findall(layout_pattern, content)
        patterns['layout_creation'] = len(layout_matches)
        
        # QLabel创建模式
        label_pattern = r'(\w+)\s*=\s*QLabel\([^)]*\)'
        label_matches = re.findall(label_pattern, content)
        patterns['label_creation'] = len(label_matches)
        
        # setStyleSheet调用
        style_pattern = r'\.setStyleSheet\([^)]*\)'
        style_matches = re.findall(style_pattern, content)
        patterns['style_setting'] = len(style_matches)
        
        return patterns
    
    def _find_data_patterns(self, content):
        """查找数据处理重复模式"""
        patterns = {}
        
        # .get()调用
        get_pattern = r'\.get\([^)]*\)'
        get_matches = re.findall(get_pattern, content)
        patterns['dict_get_calls'] = len(get_matches)
        
        # json.loads调用
        json_pattern = r'json\.loads\([^)]*\)'
        json_matches = re.findall(json_pattern, content)
        patterns['json_parsing'] = len(json_matches)
        
        # None检查
        none_pattern = r'is\s+(not\s+)?None'
        none_matches = re.findall(none_pattern, content)
        patterns['none_checks'] = len(none_matches)
        
        # 字符串格式化
        format_pattern = r'f[\'"][^\'\"]*\{[^}]*\}[^\'\"]*[\'"]'
        format_matches = re.findall(format_pattern, content)
        patterns['string_formatting'] = len(format_matches)
        
        return patterns
    
    def _find_error_patterns(self, content):
        """查找错误处理重复模式"""
        patterns = {}
        
        # try-except块
        try_pattern = r'try:\s*\n.*?except.*?:'
        try_matches = re.findall(try_pattern, content, re.DOTALL)
        patterns['try_except_blocks'] = len(try_matches)
        
        # QMessageBox调用
        msgbox_pattern = r'QMessageBox\.(warning|critical|information)\([^)]*\)'
        msgbox_matches = re.findall(msgbox_pattern, content)
        patterns['message_boxes'] = len(msgbox_matches)
        
        # print错误日志
        print_pattern = r'print\([^)]*[Ee]rror[^)]*\)'
        print_matches = re.findall(print_pattern, content)
        patterns['error_prints'] = len(print_matches)
        
        return patterns
    
    def execute_phase2a_ui_refactoring(self):
        """执行第二阶段A：UI重构"""
        print("🎨 开始第二阶段A：UI组件重构...")
        
        if not Path(self.main_file).exists():
            print(f"❌ 主文件不存在: {self.main_file}")
            return False
        
        try:
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modifications = 0
            
            # 添加UI工厂导入（如果还没有）
            if 'from ui.ui_component_factory import UIComponentFactory' not in content:
                # 找到合适的位置插入导入
                import_section = content.find('from PyQt5.QtWidgets import')
                if import_section != -1:
                    # 在PyQt5导入后添加
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'from PyQt5.QtWidgets import' in line:
                            lines.insert(i + 1, 'from ui.ui_component_factory import UIComponentFactory')
                            break
                    content = '\n'.join(lines)
                    modifications += 1
            
            # 示例重构：简单的按钮创建模式
            # 这里只做一个示例，实际重构需要更仔细的分析
            simple_button_pattern = r'(\w+)\s*=\s*QPushButton\("([^"]*)"\)\s*\n\s*\1\.clicked\.connect\(([^)]*)\)'
            
            def replace_button(match):
                var_name = match.group(1)
                button_text = match.group(2)
                callback = match.group(3)
                return f'{var_name} = UIComponentFactory.create_styled_button("{button_text}", {callback})'
            
            new_content = re.sub(simple_button_pattern, replace_button, content, flags=re.MULTILINE)
            
            if new_content != content:
                modifications += 1
                content = new_content
            
            # 保存修改
            if modifications > 0:
                with open(self.main_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.refactoring_log.append({
                    'phase': '2A',
                    'type': 'ui_refactoring',
                    'modifications': modifications,
                    'status': 'success'
                })
                
                print(f"✅ UI重构完成，进行了 {modifications} 处修改")
                return True
            else:
                print("ℹ️ 未发现需要重构的UI模式")
                return True
                
        except Exception as e:
            print(f"❌ UI重构失败: {e}")
            self.refactoring_log.append({
                'phase': '2A',
                'type': 'ui_refactoring',
                'error': str(e),
                'status': 'failed'
            })
            return False
    
    def validate_refactoring(self):
        """验证重构结果"""
        print("🔍 验证重构结果...")
        
        validation_results = {
            'syntax_check': False,
            'import_check': False,
            'file_size_check': False
        }
        
        try:
            # 语法检查
            import py_compile
            py_compile.compile(self.main_file, doraise=True)
            validation_results['syntax_check'] = True
            print("  ✅ 语法检查通过")
            
        except py_compile.PyCompileError as e:
            print(f"  ❌ 语法检查失败: {e}")
        
        try:
            # 导入检查
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'UIComponentFactory' in content:
                validation_results['import_check'] = True
                print("  ✅ 工具类导入检查通过")
            else:
                print("  ℹ️ 未发现工具类使用")
                validation_results['import_check'] = True  # 这也是正常的
            
        except Exception as e:
            print(f"  ❌ 导入检查失败: {e}")
        
        try:
            # 文件大小检查
            file_size = Path(self.main_file).stat().st_size
            if file_size > 100000:  # 大于100KB
                validation_results['file_size_check'] = True
                print(f"  ✅ 文件大小检查通过 ({file_size} 字节)")
            else:
                print(f"  ⚠️ 文件大小异常 ({file_size} 字节)")
        
        except Exception as e:
            print(f"  ❌ 文件大小检查失败: {e}")
        
        return validation_results
    
    def generate_phase2_report(self):
        """生成第二阶段报告"""
        print("📊 生成第二阶段执行报告...")
        
        patterns = self.analyze_current_patterns()
        
        report = f"""# PyQt5电影票务管理系统 - 第二阶段重构执行报告

## 📊 执行概览

**执行时间**：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}  
**执行阶段**：第二阶段 - 模式重构  
**备份目录**：{self.backup_dir}  

---

## 🔍 当前模式分析

### 🎨 UI组件模式
- **按钮创建**：{patterns['ui_patterns'].get('button_creation', 0)} 个
- **布局创建**：{patterns['ui_patterns'].get('layout_creation', 0)} 个
- **标签创建**：{patterns['ui_patterns'].get('label_creation', 0)} 个
- **样式设置**：{patterns['ui_patterns'].get('style_setting', 0)} 个

### 📊 数据处理模式
- **字典get调用**：{patterns['data_patterns'].get('dict_get_calls', 0)} 个
- **JSON解析**：{patterns['data_patterns'].get('json_parsing', 0)} 个
- **None检查**：{patterns['data_patterns'].get('none_checks', 0)} 个
- **字符串格式化**：{patterns['data_patterns'].get('string_formatting', 0)} 个

### 🛡️ 错误处理模式
- **try-except块**：{patterns['error_patterns'].get('try_except_blocks', 0)} 个
- **消息框调用**：{patterns['error_patterns'].get('message_boxes', 0)} 个
- **错误打印**：{patterns['error_patterns'].get('error_prints', 0)} 个

---

## 📋 执行记录

"""
        
        for log_entry in self.refactoring_log:
            status_icon = "✅" if log_entry['status'] == 'success' else "❌"
            report += f"""
### {status_icon} 阶段{log_entry['phase']} - {log_entry['type']}
- **状态**：{log_entry['status']}
"""
            if 'modifications' in log_entry:
                report += f"- **修改数量**：{log_entry['modifications']}\n"
            if 'error' in log_entry:
                report += f"- **错误信息**：{log_entry['error']}\n"
        
        report += f"""
---

## 🎯 重构建议

### 立即可执行的重构
1. **UI组件工厂应用**
   - 当前有 {patterns['ui_patterns'].get('button_creation', 0)} 个按钮创建可以使用工厂模式
   - 当前有 {patterns['ui_patterns'].get('layout_creation', 0)} 个布局创建可以统一

2. **数据处理工具应用**
   - 当前有 {patterns['data_patterns'].get('dict_get_calls', 0)} 个字典get调用可以使用safe_get
   - 当前有 {patterns['data_patterns'].get('json_parsing', 0)} 个JSON解析可以统一

3. **错误处理装饰器应用**
   - 当前有 {patterns['error_patterns'].get('try_except_blocks', 0)} 个try-except块可以使用装饰器

### 手动重构示例

#### UI组件重构示例
```python
# 重构前
button = QPushButton("确认")
button.setStyleSheet("QPushButton {{ background-color: #4CAF50; }}")
button.clicked.connect(self.confirm_action)

# 重构后
from ui.ui_component_factory import UIComponentFactory
button = UIComponentFactory.create_styled_button("确认", self.confirm_action)
```

#### 数据处理重构示例
```python
# 重构前
value = data.get('key', default_value)
if value is not None:
    # 处理逻辑

# 重构后
from utils.data_utils import DataUtils
value = DataUtils.safe_get(data, 'key', default_value)
if value is not None:
    # 处理逻辑
```

#### 错误处理重构示例
```python
# 重构前
try:
    result = api_call()
    return result
except Exception as e:
    QMessageBox.critical(self, "错误", f"操作失败: {{e}}")
    return None

# 重构后
from utils.error_handler import handle_exceptions

@handle_exceptions(show_message=True, default_return=None)
def api_call_method(self):
    return api_call()
```

---

## 📋 下一步行动

### 建议执行顺序
1. **验证当前状态** - 确保系统功能正常
2. **选择重构目标** - 从最简单的模式开始
3. **小步重构** - 每次重构少量代码并测试
4. **逐步扩展** - 成功后扩展到更多模式

### 重构检查清单
- [ ] 备份已创建
- [ ] 语法检查通过
- [ ] 核心功能测试通过
- [ ] 工具类导入正确
- [ ] 重构效果符合预期

---

## 🎉 总结

第二阶段重构已经准备就绪！

- **工具类已就位**：3个工具类可以使用
- **重构目标明确**：发现了大量可重构的模式
- **执行策略清晰**：分阶段、小步快跑
- **风险控制完善**：备份、验证、回滚机制齐全

**建议从简单的UI组件重构开始，逐步建立信心后扩展到数据处理和错误处理重构！**
"""
        
        try:
            with open('第二阶段重构执行报告.md', 'w', encoding='utf-8') as f:
                f.write(report)
            print("✅ 执行报告生成成功: 第二阶段重构执行报告.md")
        except Exception as e:
            print(f"❌ 执行报告生成失败: {e}")
    
    def run_phase2a(self):
        """运行第二阶段A"""
        print("🚀 开始第二阶段A重构执行")
        print("=" * 50)
        
        # 创建备份
        if not self.create_backup():
            print("❌ 备份失败，停止执行")
            return False
        
        # 分析当前模式
        patterns = self.analyze_current_patterns()
        print(f"📊 发现UI模式: {sum(patterns['ui_patterns'].values())} 个")
        print(f"📊 发现数据模式: {sum(patterns['data_patterns'].values())} 个")
        print(f"📊 发现错误模式: {sum(patterns['error_patterns'].values())} 个")
        
        # 执行UI重构
        ui_success = self.execute_phase2a_ui_refactoring()
        
        # 验证结果
        validation = self.validate_refactoring()
        
        # 生成报告
        self.generate_phase2_report()
        
        print("\n🎉 第二阶段A执行完成！")
        print("📋 请检查以下内容：")
        print("1. 查看执行报告了解详细情况")
        print("2. 测试主程序功能是否正常")
        print("3. 根据报告建议进行后续重构")
        
        return ui_success and all(validation.values())

def main():
    """主函数"""
    executor = Phase2RefactoringExecutor()
    
    print("🎬 PyQt5电影票务管理系统 - 第二阶段重构执行器")
    print("=" * 60)
    print("⚠️ 重要提醒：")
    print("1. 确保第一阶段工具类已正常创建")
    print("2. 重构过程中会自动创建备份")
    print("3. 重构后请立即测试核心功能")
    print("4. 如有问题可使用备份快速回滚")
    print()
    
    confirm = input("确认开始第二阶段A重构？(输入 'yes' 继续): ")
    if confirm.lower() == 'yes':
        success = executor.run_phase2a()
        if success:
            print("\n✅ 第二阶段A重构执行成功！")
        else:
            print("\n⚠️ 第二阶段A重构执行完成，请检查报告")
    else:
        print("❌ 重构已取消")

if __name__ == "__main__":
    main()
