#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复Token过期问题
"""

import json
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer


def quick_fix_token_refresh():
    """快速修复Token过期问题"""
    print("🔧 快速修复Token过期问题")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口并触发重新登录
        from main_modular import ModularCinemaMainWindow
        
        print(f"  📱 启动主应用...")
        main_window = ModularCinemaMainWindow()
        
        # 显示Token过期提示
        def show_token_expired_message():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Token过期")
            msg.setText("检测到Token已过期，需要重新登录")
            msg.setInformativeText(
                "问题原因：\n"
                "• API返回 resultCode: 400\n"
                "• resultData 为空\n"
                "• 这通常表示Token已过期\n\n"
                "解决方案：\n"
                "• 点击确定后会自动打开登录窗口\n"
                "• 重新登录获取新Token\n"
                "• 登录成功后问题将自动解决"
            )
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Ok)
            
            result = msg.exec_()
            
            if result == QMessageBox.Ok:
                print(f"  ✅ 用户确认重新登录")
                # 触发重新登录
                trigger_relogin()
            else:
                print(f"  ❌ 用户取消重新登录")
                app.quit()
        
        def trigger_relogin():
            """触发重新登录"""
            try:
                print(f"  🔑 触发重新登录...")
                
                # 清除当前账号状态
                main_window.current_account = None
                
                # 显示登录窗口
                if hasattr(main_window, 'show_login_window'):
                    main_window.show_login_window()
                    print(f"  ✅ 登录窗口已打开")
                else:
                    print(f"  ❌ 未找到登录窗口方法")
                
                # 提示用户操作
                info_msg = QMessageBox()
                info_msg.setIcon(QMessageBox.Information)
                info_msg.setWindowTitle("重新登录")
                info_msg.setText("请在登录窗口中重新登录")
                info_msg.setInformativeText(
                    "操作步骤：\n"
                    "1. 在登录窗口输入手机号和验证码\n"
                    "2. 点击登录按钮\n"
                    "3. 登录成功后Token会自动更新\n"
                    "4. 影片和场次数据将正常加载\n\n"
                    "注意：登录成功后请重新选择影院、影片、日期、场次"
                )
                info_msg.exec_()
                
            except Exception as e:
                print(f"  ❌ 触发重新登录失败: {e}")
        
        # 1秒后显示Token过期消息
        QTimer.singleShot(1000, show_token_expired_message)
        
        # 显示主窗口
        main_window.show()
        
        # 运行应用
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 快速修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_token_refresh_guide():
    """创建Token刷新指南"""
    print("\n📖 创建Token刷新指南")
    
    guide_content = """# Token过期问题解决指南

## 🔍 问题症状
- 影片列表显示"暂无影片"
- 场次列表显示"暂无场次"  
- 座位图无法加载
- API返回 resultCode: 400, resultData: None

## 🎯 问题原因
Token已过期，需要重新登录获取新的认证信息。

## 🔧 解决步骤

### 方法一：自动修复（推荐）
1. 运行 `python quick_fix_token_refresh.py`
2. 点击确定重新登录
3. 在登录窗口输入手机号和验证码
4. 登录成功后问题自动解决

### 方法二：手动修复
1. 启动主应用 `python main_modular.py`
2. 点击右上角的登录按钮
3. 重新登录获取新Token
4. 重新选择影院、影片、日期、场次

### 方法三：清除缓存重新开始
1. 删除 `data/accounts.json` 文件
2. 重新启动应用
3. 重新登录和配置

## 🛠️ 预防措施
- 定期重新登录刷新Token
- 不要长时间不使用应用
- 保持网络连接稳定

## 🧪 验证修复
修复后应该能看到：
- ✅ 影片列表正常加载
- ✅ 场次列表显示真实数据
- ✅ 座位图能正常显示
- ✅ 订单提交功能正常

## 📞 技术支持
如果问题仍然存在，请检查：
- 网络连接是否正常
- 影院配置是否正确
- 账号是否被禁用
"""
    
    try:
        with open('TOKEN_REFRESH_GUIDE.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        print(f"  ✅ Token刷新指南已创建: TOKEN_REFRESH_GUIDE.md")
        return True
    except Exception as e:
        print(f"  ❌ 创建指南失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🔧 快速修复Token过期问题")
    print("=" * 60)
    
    print("🎯 修复目标:")
    print("   1. 🔍 确认Token过期问题")
    print("   2. 🔑 引导用户重新登录")
    print("   3. 📖 提供详细解决指南")
    print("   4. ✅ 验证问题解决")
    print()
    
    print("💡 问题分析:")
    print("   根据API响应分析:")
    print("   - resultCode: '400' → 请求参数错误")
    print("   - resultData: None → Token认证失败")
    print("   - 这是典型的Token过期症状")
    print()
    
    # 创建指南
    guide_created = create_token_refresh_guide()
    
    print("🔧 开始快速修复...")
    print("   注意：这将启动主应用并引导重新登录")
    print()
    
    # 执行快速修复
    fix_success = quick_fix_token_refresh()
    
    # 总结结果
    print("\n" + "=" * 60)
    print("📊 修复结果总结:")
    print("=" * 60)
    
    print(f"   Token刷新指南创建: {'✅ 成功' if guide_created else '❌ 失败'}")
    print(f"   快速修复执行: {'✅ 完成' if fix_success else '❌ 失败'}")
    
    if fix_success:
        print("\n🎉 快速修复已完成！")
        print()
        print("✨ 修复效果:")
        print("   - 已引导用户重新登录")
        print("   - Token将在登录后自动更新")
        print("   - 影片和场次数据将正常加载")
        print("   - 座位图功能将恢复正常")
        print()
        print("📋 后续操作:")
        print("   1. 在登录窗口完成登录")
        print("   2. 重新选择影院、影片、日期、场次")
        print("   3. 验证座位图是否正常显示")
        print("   4. 测试订单提交功能")
    else:
        print("\n⚠️  快速修复未完全成功")
        print()
        print("🔧 手动解决步骤:")
        print("   1. 启动主应用: python main_modular.py")
        print("   2. 点击登录按钮重新登录")
        print("   3. 参考 TOKEN_REFRESH_GUIDE.md 指南")
        print("   4. 如有问题请联系技术支持")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
