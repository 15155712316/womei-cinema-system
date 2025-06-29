#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美电影院项目配置管理模块
用于安全地管理API地址、认证信息等敏感配置
"""

import os
from typing import Optional
from pathlib import Path

class Config:
    """配置管理类 - 统一管理所有敏感配置信息"""
    
    def __init__(self):
        # 尝试加载 .env 文件
        self._load_env_file()
    
    def _load_env_file(self):
        """加载 .env 文件中的环境变量"""
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception as e:
                print(f"⚠️ 加载 .env 文件失败: {e}")
    
    # API配置
    @property
    def API_BASE_URL(self) -> str:
        """API基础URL"""
        return os.getenv('WOMEI_API_BASE_URL', 'https://ct.womovie.cn')
    
    @property
    def DEFAULT_CINEMA_ID(self) -> str:
        """默认影院ID"""
        return os.getenv('WOMEI_CINEMA_ID', '400303')
    
    # 认证配置
    @property
    def DEFAULT_TOKEN(self) -> Optional[str]:
        """默认认证Token"""
        return os.getenv('WOMEI_TOKEN')
    
    @property
    def TEST_PHONE(self) -> str:
        """测试手机号"""
        return os.getenv('WOMEI_TEST_PHONE', '13800138000')
    
    # 调试配置
    @property
    def DEBUG(self) -> bool:
        """调试模式"""
        return os.getenv('DEBUG', 'false').lower() == 'true'
    
    @property
    def LOG_LEVEL(self) -> str:
        """日志级别"""
        return os.getenv('LOG_LEVEL', 'info')
    
    @property
    def DISABLE_SSL_VERIFY(self) -> bool:
        """是否禁用SSL验证（仅用于测试）"""
        return os.getenv('DISABLE_SSL_VERIFY', 'false').lower() == 'true'
    
    # 数据库配置（如果需要）
    @property
    def DB_HOST(self) -> str:
        """数据库主机"""
        return os.getenv('DB_HOST', 'localhost')
    
    @property
    def DB_PORT(self) -> int:
        """数据库端口"""
        return int(os.getenv('DB_PORT', '5432'))
    
    @property
    def DB_NAME(self) -> str:
        """数据库名称"""
        return os.getenv('DB_NAME', 'womei_cinema')
    
    @property
    def DB_USER(self) -> str:
        """数据库用户"""
        return os.getenv('DB_USER', 'postgres')
    
    @property
    def DB_PASSWORD(self) -> Optional[str]:
        """数据库密码"""
        return os.getenv('DB_PASSWORD')
    
    def validate(self) -> bool:
        """验证必要配置是否存在"""
        required_configs = [
            ('WOMEI_TOKEN', self.DEFAULT_TOKEN, '沃美API认证Token'),
        ]
        
        missing_configs = []
        for env_name, value, description in required_configs:
            if not value:
                missing_configs.append(f"{env_name} ({description})")
        
        if missing_configs:
            print(f"❌ 缺少必要配置:")
            for config in missing_configs:
                print(f"   • {config}")
            print(f"\n💡 解决方案:")
            print(f"   1. 复制环境变量模板: cp .env.example .env")
            print(f"   2. 编辑 .env 文件，填入真实配置值")
            print(f"   3. 重新运行程序")
            return False
        
        return True
    
    def get_api_url(self, path: str) -> str:
        """构建完整的API URL"""
        base_url = self.API_BASE_URL.rstrip('/')
        path = path.lstrip('/')
        return f"{base_url}/{path}"
    
    def get_cinema_api_url(self, cinema_id: str, path: str) -> str:
        """构建影院相关的API URL"""
        base_path = f"ticket/wmyc/cinema/{cinema_id}"
        full_path = f"{base_path}/{path.lstrip('/')}"
        return self.get_api_url(full_path)
    
    def get_headers_template(self) -> dict:
        """获取标准请求头模板"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
    
    def get_headers_with_token(self, token: Optional[str] = None) -> dict:
        """获取包含Token的请求头"""
        headers = self.get_headers_template()
        token_to_use = token or self.DEFAULT_TOKEN
        if token_to_use:
            headers['token'] = token_to_use
        return headers
    
    def print_config_summary(self):
        """打印配置摘要（隐藏敏感信息）"""
        print("📋 当前配置摘要:")
        print(f"   API地址: {self.API_BASE_URL}")
        print(f"   默认影院: {self.DEFAULT_CINEMA_ID}")
        print(f"   测试手机: {self.TEST_PHONE}")
        print(f"   调试模式: {self.DEBUG}")
        print(f"   Token状态: {'✅ 已配置' if self.DEFAULT_TOKEN else '❌ 未配置'}")
        print(f"   SSL验证: {'❌ 已禁用' if self.DISABLE_SSL_VERIFY else '✅ 已启用'}")

# 全局配置实例
config = Config()

# 测试配置类
class TestConfig:
    """测试专用配置类"""
    
    @staticmethod
    def get_test_token() -> str:
        """获取测试Token"""
        if not config.DEFAULT_TOKEN:
            raise ValueError(
                "❌ 未配置测试Token\n"
                "请在 .env 文件中设置 WOMEI_TOKEN=your_token_here"
            )
        return config.DEFAULT_TOKEN
    
    @staticmethod
    def get_test_phone() -> str:
        """获取测试手机号"""
        return config.TEST_PHONE
    
    @staticmethod
    def get_test_cinema_id() -> str:
        """获取测试影院ID"""
        return config.DEFAULT_CINEMA_ID
    
    @staticmethod
    def get_test_account() -> dict:
        """获取测试账号信息"""
        return {
            'phone': config.TEST_PHONE,
            'token': config.DEFAULT_TOKEN,
            'cinema_id': config.DEFAULT_CINEMA_ID
        }

def main():
    """配置验证和测试"""
    print("🔧 沃美电影院项目配置验证")
    print("=" * 50)
    
    # 打印配置摘要
    config.print_config_summary()
    
    # 验证配置
    print(f"\n🔍 配置验证:")
    is_valid = config.validate()
    
    if is_valid:
        print("✅ 配置验证通过")
        
        # 测试API URL构建
        print(f"\n🔗 API URL测试:")
        print(f"   基础URL: {config.get_api_url('test/path')}")
        print(f"   影院URL: {config.get_cinema_api_url('400303', 'order/info')}")
        
        # 测试请求头
        print(f"\n📋 请求头测试:")
        headers = config.get_headers_with_token()
        print(f"   User-Agent: {headers['User-Agent'][:50]}...")
        print(f"   Token: {'✅ 已设置' if 'token' in headers else '❌ 未设置'}")
        
    else:
        print("❌ 配置验证失败")
        return False
    
    return True

if __name__ == "__main__":
    main()
