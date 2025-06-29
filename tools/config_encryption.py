#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件加密工具
"""

import os
import json
import base64
from typing import Dict, Any

class ConfigEncryption:
    """配置文件加密类"""
    
    def __init__(self, key: str = None):
        """
        初始化加密器
        
        Args:
            key: 加密密钥，如果为None则生成新密钥
        """
        if key is None:
            # 生成基于机器特征的密钥
            self.key = self._generate_machine_key()
        else:
            self.key = key.encode() if isinstance(key, str) else key
    
    def _generate_machine_key(self) -> bytes:
        """生成基于机器特征的密钥"""
        try:
            import hashlib
            import platform
            import uuid
            
            # 收集机器特征
            machine_info = {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'node': platform.node(),
                'mac': hex(uuid.getnode())
            }
            
            # 生成密钥
            info_str = json.dumps(machine_info, sort_keys=True)
            key = hashlib.sha256(info_str.encode()).digest()
            
            return key
            
        except Exception:
            # 如果获取机器信息失败，使用默认密钥
            return b'default_encryption_key_32_bytes!'
    
    def _simple_encrypt(self, data: str) -> str:
        """简单的XOR加密"""
        key = self.key
        key_len = len(key)
        
        encrypted = bytearray()
        for i, char in enumerate(data.encode('utf-8')):
            encrypted.append(char ^ key[i % key_len])
        
        return base64.b64encode(encrypted).decode('ascii')
    
    def _simple_decrypt(self, encrypted_data: str) -> str:
        """简单的XOR解密"""
        try:
            key = self.key
            key_len = len(key)
            
            encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
            
            decrypted = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted.append(byte ^ key[i % key_len])
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"解密失败: {e}")
    
    def encrypt_config(self, config_data: Dict[str, Any]) -> str:
        """
        加密配置数据
        
        Args:
            config_data: 配置字典
            
        Returns:
            str: 加密后的字符串
        """
        json_str = json.dumps(config_data, ensure_ascii=False, separators=(',', ':'))
        return self._simple_encrypt(json_str)
    
    def decrypt_config(self, encrypted_data: str) -> Dict[str, Any]:
        """
        解密配置数据
        
        Args:
            encrypted_data: 加密的字符串
            
        Returns:
            Dict[str, Any]: 解密后的配置字典
        """
        json_str = self._simple_decrypt(encrypted_data)
        return json.loads(json_str)
    
    def encrypt_file(self, input_file: str, output_file: str = None):
        """
        加密配置文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径，如果为None则覆盖原文件
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"文件不存在: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        encrypted_data = self.encrypt_config(config_data)
        
        if output_file is None:
            output_file = input_file + '.encrypted'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(encrypted_data)
        
        print(f"✅ 文件加密完成: {input_file} -> {output_file}")
    
    def decrypt_file(self, input_file: str, output_file: str = None):
        """
        解密配置文件
        
        Args:
            input_file: 加密的文件路径
            output_file: 输出文件路径，如果为None则自动生成
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"文件不存在: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            encrypted_data = f.read()
        
        config_data = self.decrypt_config(encrypted_data)
        
        if output_file is None:
            if input_file.endswith('.encrypted'):
                output_file = input_file[:-10]  # 移除.encrypted后缀
            else:
                output_file = input_file + '.decrypted'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 文件解密完成: {input_file} -> {output_file}")

class SecureConfigLoader:
    """安全配置加载器 - 用于程序中加载加密配置"""
    
    def __init__(self):
        self.encryptor = ConfigEncryption()
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """
        加载配置文件（自动检测是否加密）
        
        Args:
            config_file: 配置文件路径
            
        Returns:
            Dict[str, Any]: 配置数据
        """
        if not os.path.exists(config_file):
            # 尝试加载加密版本
            encrypted_file = config_file + '.encrypted'
            if os.path.exists(encrypted_file):
                return self._load_encrypted_config(encrypted_file)
            else:
                raise FileNotFoundError(f"配置文件不存在: {config_file}")
        
        try:
            # 尝试作为普通JSON文件加载
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # 如果不是有效的JSON，尝试作为加密文件解密
            return self._load_encrypted_config(config_file)
    
    def _load_encrypted_config(self, encrypted_file: str) -> Dict[str, Any]:
        """加载加密的配置文件"""
        with open(encrypted_file, 'r', encoding='utf-8') as f:
            encrypted_data = f.read()
        
        return self.encryptor.decrypt_config(encrypted_data)

def main():
    """主函数 - 用于测试和批量加密"""
    import argparse
    
    parser = argparse.ArgumentParser(description='配置文件加密工具')
    parser.add_argument('action', choices=['encrypt', 'decrypt', 'test'], help='操作类型')
    parser.add_argument('--file', '-f', help='文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    
    args = parser.parse_args()
    
    encryptor = ConfigEncryption()
    
    if args.action == 'encrypt':
        if not args.file:
            print("❌ 请指定要加密的文件")
            return
        
        try:
            encryptor.encrypt_file(args.file, args.output)
        except Exception as e:
            print(f"❌ 加密失败: {e}")
    
    elif args.action == 'decrypt':
        if not args.file:
            print("❌ 请指定要解密的文件")
            return
        
        try:
            encryptor.decrypt_file(args.file, args.output)
        except Exception as e:
            print(f"❌ 解密失败: {e}")
    
    elif args.action == 'test':
        # 测试加密解密功能
        test_config = {
            "server_url": "http://localhost:5000",
            "timeout": 10,
            "debug": False,
            "api_key": "secret_key_12345"
        }
        
        print("🧪 测试配置加密...")
        
        # 加密
        encrypted = encryptor.encrypt_config(test_config)
        print(f"加密结果: {encrypted[:50]}...")
        
        # 解密
        decrypted = encryptor.decrypt_config(encrypted)
        print(f"解密结果: {decrypted}")
        
        # 验证
        if test_config == decrypted:
            print("✅ 加密解密测试通过")
        else:
            print("❌ 加密解密测试失败")

if __name__ == "__main__":
    main()
