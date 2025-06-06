#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
curl命令解析器
自动从curl命令中提取影院API参数
"""

import re
import json
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional, Tuple

class CurlParser:
    """curl命令解析器"""
    
    @staticmethod
    def parse_curl_command(curl_command: str) -> Dict[str, str]:
        """
        解析curl命令，提取影院API参数
        
        Args:
            curl_command: curl命令字符串
            
        Returns:
            包含提取参数的字典
        """
        params = {}
        
        try:
            # 1. 提取URL
            url = CurlParser.extract_url(curl_command)
            if url:
                # 提取基础URL
                parsed_url = urlparse(url)
                if parsed_url.scheme and parsed_url.netloc:
                    params['base_url'] = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # 提取URL参数
                url_params = CurlParser.extract_url_params(url)
                params.update(url_params)
            
            # 2. 提取请求头中的参数
            header_params = CurlParser.extract_header_params(curl_command)
            params.update(header_params)
            
            # 3. 验证和清理参数
            params = CurlParser.validate_and_clean_params(params)
            
        except Exception as e:
            print(f"[curl解析] 解析错误: {e}")
        
        return params
    
    @staticmethod
    def extract_url(curl_command: str) -> Optional[str]:
        """提取URL"""
        # 匹配curl命令中的URL
        patterns = [
            r"curl\s+[^'\"]*['\"]([^'\"]+)['\"]",  # curl 'url'
            r"curl\s+[^'\"]*([https?://[^\s]+)",   # curl url
            r"-X\s+\w+\s+['\"]([^'\"]+)['\"]",     # -X GET 'url'
            r"--url\s+['\"]([^'\"]+)['\"]",        # --url 'url'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, curl_command, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def extract_url_params(url: str) -> Dict[str, str]:
        """从URL中提取参数"""
        params = {}
        
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # 影院相关参数映射
            param_mapping = {
                'cinemaid': 'cinema_id',
                'cinema_id': 'cinema_id',
                'cinemaId': 'cinema_id',
                'cid': 'cinema_id',
                'groupid': 'group_id',
                'group_id': 'group_id',
                'openid': 'openid',
                'userid': 'user_id',
                'user_id': 'user_id',
                'token': 'token',
                'access_token': 'token',
                'cardno': 'card_no',
                'card_no': 'card_no'
            }
            
            for key, values in query_params.items():
                if values and values[0]:  # 确保有值
                    value = values[0]
                    
                    # 映射参数名
                    mapped_key = param_mapping.get(key.lower(), key)
                    params[mapped_key] = value
                    
                    # 特殊处理：如果是影院ID，确保长度合理
                    if mapped_key == 'cinema_id' and len(value) >= 3:
                        params['cinema_id'] = value
            
        except Exception as e:
            print(f"[curl解析] URL参数提取错误: {e}")
        
        return params
    
    @staticmethod
    def extract_header_params(curl_command: str) -> Dict[str, str]:
        """从请求头中提取参数"""
        params = {}
        
        try:
            # 提取所有-H参数
            header_pattern = r"-H\s+['\"]([^'\"]+)['\"]"
            headers = re.findall(header_pattern, curl_command, re.IGNORECASE)
            
            for header in headers:
                if ':' in header:
                    key, value = header.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    # 从特定请求头中提取参数
                    if key == 'authorization':
                        # 提取Bearer token
                        if 'bearer' in value.lower():
                            token = value.replace('Bearer ', '').replace('bearer ', '')
                            if len(token) > 10:
                                params['token'] = token
                    
                    elif key == 'x-openid' or key == 'openid':
                        if len(value) > 10:
                            params['openid'] = value
                    
                    elif key == 'x-user-id' or key == 'userid':
                        if len(value) > 3:
                            params['user_id'] = value
                    
                    elif key == 'x-cinema-id' or key == 'cinemaid':
                        if len(value) >= 3:
                            params['cinema_id'] = value
        
        except Exception as e:
            print(f"[curl解析] 请求头参数提取错误: {e}")
        
        return params
    
    @staticmethod
    def validate_and_clean_params(params: Dict[str, str]) -> Dict[str, str]:
        """验证和清理参数"""
        cleaned_params = {}
        
        for key, value in params.items():
            if not value or value.strip() == '':
                continue
            
            value = value.strip()
            
            # 验证参数有效性
            if key == 'cinema_id':
                # 影院ID应该是字母数字组合，长度3-20
                if re.match(r'^[a-zA-Z0-9]{3,20}$', value):
                    cleaned_params[key] = value
            
            elif key == 'openid':
                # OpenID通常以特定前缀开始，长度较长
                if len(value) > 15 and re.match(r'^[a-zA-Z0-9_-]+$', value):
                    cleaned_params[key] = value
            
            elif key == 'token':
                # Token通常是长字符串
                if len(value) > 10 and re.match(r'^[a-zA-Z0-9_-]+$', value):
                    cleaned_params[key] = value
            
            elif key == 'user_id':
                # 用户ID可能是数字或字符串
                if len(value) > 3:
                    cleaned_params[key] = value
            
            elif key == 'base_url':
                # 验证URL格式
                if value.startswith(('http://', 'https://')):
                    cleaned_params[key] = value
            
            else:
                # 其他参数直接保留
                cleaned_params[key] = value
        
        return cleaned_params
    
    @staticmethod
    def analyze_curl_example(curl_command: str) -> Tuple[Dict[str, str], str]:
        """
        分析curl命令示例，返回参数和分析报告
        
        Returns:
            (参数字典, 分析报告)
        """
        params = CurlParser.parse_curl_command(curl_command)
        
        # 生成分析报告
        report = "🔍 curl命令解析结果:\n\n"
        
        if params:
            report += "✅ 成功提取的参数:\n"
            for key, value in params.items():
                if key in ['token', 'openid'] and len(value) > 12:
                    # 敏感信息部分隐藏
                    display_value = value[:8] + "..." + value[-4:]
                else:
                    display_value = value
                report += f"  • {key}: {display_value}\n"
            
            # 检查必要参数
            required_params = ['base_url', 'cinema_id']
            missing_params = [p for p in required_params if p not in params]
            
            if missing_params:
                report += f"\n⚠️ 缺少必要参数: {', '.join(missing_params)}\n"
            else:
                report += "\n🎉 所有必要参数都已提取！\n"
        
        else:
            report += "❌ 未能提取到任何参数\n"
            report += "请检查curl命令格式是否正确\n"
        
        return params, report


def test_curl_parser():
    """测试curl解析器"""
    test_curl = """curl -X GET 'https://www.heibaiyingye.cn/MiniTicket/index.php/MiniCommonSystem/getCinemaSettings?sortType=1&groupid&cinemaid=35fec8259e74&cardno&userid=15155712316&openid=oAOCp7VbeeoqMM4yC8e2i3G3lxI8&CVersion=3.9.12&OS=Windows&token=3a30b9e980892714&source=2' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639' -H 'Accept: application/json'"""
    
    params, report = CurlParser.analyze_curl_example(test_curl)
    print(report)
    print(f"提取的参数: {params}")

if __name__ == "__main__":
    test_curl_parser()
