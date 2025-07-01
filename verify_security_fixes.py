#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证main_modular.py安全修复结果
"""

import re
import os

def check_main_modular_security():
    """检查main_modular.py的安全修复情况"""
    print("🔍 验证 main_modular.py 安全修复结果")
    print("=" * 60)
    
    file_path = "main_modular.py"
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查硬编码的敏感信息
        security_issues = []
        
        # 1. 检查硬编码手机号
        phone_pattern = r'15155712316'
        phone_matches = re.findall(phone_pattern, content)
        if phone_matches:
            security_issues.append(f"❌ 发现硬编码手机号: {len(phone_matches)} 处")
        else:
            print("✅ 硬编码手机号已清理")
        
        # 2. 检查硬编码token
        token_pattern = r'47794858a832916d8eda012e7cabd269'
        token_matches = re.findall(token_pattern, content)
        if token_matches:
            security_issues.append(f"❌ 发现硬编码token: {len(token_matches)} 处")
        else:
            print("✅ 硬编码token已清理")
        
        # 3. 检查不安全的token显示
        unsafe_token_patterns = [
            r'token\[:20\]',
            r'token\[-10:\]',
            r'token.*\[:20\].*\.\.\.'
        ]
        
        unsafe_token_count = 0
        for pattern in unsafe_token_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            unsafe_token_count += len(matches)
        
        if unsafe_token_count > 0:
            security_issues.append(f"❌ 发现不安全的token显示: {unsafe_token_count} 处")
        else:
            print("✅ Token显示已安全化")
        
        # 4. 检查是否使用了config模块
        config_import_pattern = r'from config import config'
        config_usage_pattern = r'config\.(TEST_PHONE|DEFAULT_TOKEN|DEBUG)'
        
        config_imports = re.findall(config_import_pattern, content)
        config_usages = re.findall(config_usage_pattern, content)
        
        if config_imports and config_usages:
            print(f"✅ 已使用config模块: {len(config_imports)} 次导入, {len(config_usages)} 次使用")
        else:
            security_issues.append("❌ 未正确使用config模块")
        
        # 5. 检查安全的token显示模式
        safe_token_patterns = [
            r'token\[:10\]\*\*\*',
            r'Token状态.*已配置',
            r'token_status.*已配置'
        ]
        
        safe_token_count = 0
        for pattern in safe_token_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            safe_token_count += len(matches)
        
        if safe_token_count > 0:
            print(f"✅ 发现安全的token显示: {safe_token_count} 处")
        
        # 输出结果
        print(f"\n📊 安全检查结果:")
        if security_issues:
            print(f"⚠️ 发现 {len(security_issues)} 个安全问题:")
            for issue in security_issues:
                print(f"  {issue}")
            return False
        else:
            print(f"🎉 所有安全检查通过！")
            return True
            
    except Exception as e:
        print(f"❌ 检查文件失败: {e}")
        return False

def check_config_usage():
    """检查config.py的使用情况"""
    print(f"\n" + "=" * 60)
    print("🔧 检查配置管理使用情况")
    print("=" * 60)
    
    # 检查config.py是否存在
    if os.path.exists("config.py"):
        print("✅ config.py 文件存在")
    else:
        print("❌ config.py 文件不存在")
        return False
    
    # 检查.env.example是否存在
    if os.path.exists(".env.example"):
        print("✅ .env.example 模板文件存在")
    else:
        print("❌ .env.example 模板文件不存在")
    
    # 检查.gitignore是否存在
    if os.path.exists(".gitignore"):
        print("✅ .gitignore 文件存在")
        
        # 检查.gitignore内容
        try:
            with open(".gitignore", 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            sensitive_patterns = ['.env', '*.har', 'accounts.json', 'test_*.py']
            protected_count = 0
            
            for pattern in sensitive_patterns:
                if pattern in gitignore_content:
                    protected_count += 1
            
            print(f"✅ .gitignore 保护了 {protected_count}/{len(sensitive_patterns)} 种敏感文件")
            
        except Exception as e:
            print(f"⚠️ 无法读取.gitignore: {e}")
    else:
        print("❌ .gitignore 文件不存在")
    
    return True

def main():
    """主函数"""
    print("🛡️ 沃美电影院项目安全修复验证")
    print("=" * 60)
    
    # 检查main_modular.py安全修复
    main_security_ok = check_main_modular_security()
    
    # 检查配置管理
    config_ok = check_config_usage()
    
    # 总结
    print(f"\n" + "=" * 60)
    print("📋 验证总结")
    print("=" * 60)
    
    if main_security_ok and config_ok:
        print("🎉 安全修复验证通过！")
        print("✅ 硬编码敏感信息已清理")
        print("✅ 配置管理已正确实施")
        print("✅ Token显示已安全化")
        print("\n💡 下一步:")
        print("  1. 创建 .env 文件并配置必要参数")
        print("  2. 测试应用程序功能")
        print("  3. 提交代码到GitHub")
    else:
        print("⚠️ 安全修复验证未完全通过")
        print("请检查上述问题并继续修复")
    
    return main_security_ok and config_ok

if __name__ == "__main__":
    main()
