#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美绑券服务
基于绑券.py的接口实现，集成到沃美电影票务系统中
"""

import requests
import json
import re
from typing import Dict, Optional, Tuple, List


class WomeiVoucherService:
    """沃美绑券服务类"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn/ticket/wmyc/cinema"
        self.headers_template = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
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
            'priority': 'u=1, i',
        }
    
    def decode_unicode_message(self, response_text: str) -> Optional[Dict]:
        """解码响应中的Unicode字符，特别是msg字段"""
        try:
            # 解析JSON响应
            data = json.loads(response_text)
            
            # 解码msg字段中的Unicode字符
            if 'msg' in data and isinstance(data['msg'], str):
                # 将Unicode编码转换为中文
                try:
                    # 方法1：直接使用json.loads再次解析（推荐）
                    unicode_str = f'"{data["msg"]}"'
                    data['msg'] = json.loads(unicode_str)
                except:
                    # 方法2：手动替换Unicode编码
                    import codecs
                    data['msg'] = codecs.decode(data['msg'], 'unicode_escape')
            
            return data
        except Exception as e:
            print(f"❌ 解码失败: {e}")
            print(f"原始响应: {response_text}")
            return None
    
    def parse_voucher_input(self, input_text: str) -> List[Tuple[str, str]]:
        """
        解析用户输入的券码和密码
        
        支持格式：
        - 卡号：GZJY01002948416827;密码：2034
        - 卡号：GZJY01002948425042;密码：3594
        
        Args:
            input_text: 用户输入的文本
            
        Returns:
            List[Tuple[str, str]]: [(voucher_code, voucher_password), ...]
        """
        vouchers = []
        lines = input_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 使用正则表达式解析格式：卡号：xxx;密码：xxx
            pattern = r'卡号[：:]\s*([^;；]+)[;；]\s*密码[：:]\s*(.+)'
            match = re.match(pattern, line)
            
            if match:
                voucher_code = match.group(1).strip()
                voucher_password = match.group(2).strip()
                vouchers.append((voucher_code, voucher_password))
            else:
                print(f"[沃美绑券] ⚠️ 无法解析行: {line}")
        
        return vouchers
    
    def bind_voucher(self, cinema_id: str, token: str, voucher_code: str, voucher_password: str) -> Dict:
        """
        绑定单张券
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            voucher_code: 券码
            voucher_password: 券密码
            
        Returns:
            Dict: 绑券结果
        """
        try:
            # 构建请求头
            headers = self.headers_template.copy()
            headers['token'] = token
            
            # 构建请求数据
            data = {
                'voucher_code': voucher_code,
                'voucher_password': voucher_password,
                'voucher_type': 'VOUCHER',
            }
            
            # 构建URL
            url = f"{self.base_url}/{cinema_id}/user/voucher/add/"
            
            print(f"[沃美绑券] 🚀 绑定券: {voucher_code}")
            print(f"[沃美绑券] 📡 URL: {url}")
            
            # 发送请求
            response = requests.post(url, headers=headers, data=data, verify=False)
            
            print(f"[沃美绑券] 📥 响应状态: {response.status_code}")
            print(f"[沃美绑券] 📥 原始响应: {response.text}")
            
            # 解码Unicode字符
            decoded_data = self.decode_unicode_message(response.text)
            
            if decoded_data:
                print(f"[沃美绑券] 📋 解码后响应: {json.dumps(decoded_data, ensure_ascii=False, indent=2)}")
                return decoded_data
            else:
                return {
                    'ret': -1,
                    'sub': -1,
                    'msg': '响应解析失败',
                    'data': {}
                }
                
        except Exception as e:
            print(f"[沃美绑券] ❌ 绑券异常: {e}")
            return {
                'ret': -1,
                'sub': -1,
                'msg': f'请求异常: {str(e)}',
                'data': {}
            }
    
    def bind_vouchers_batch(self, cinema_id: str, token: str, vouchers: List[Tuple[str, str]]) -> List[Dict]:
        """
        批量绑定券
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            vouchers: 券列表 [(voucher_code, voucher_password), ...]
            
        Returns:
            List[Dict]: 绑券结果列表
        """
        results = []
        
        for i, (voucher_code, voucher_password) in enumerate(vouchers, 1):
            print(f"[沃美绑券] 📋 绑定进度: {i}/{len(vouchers)}")
            
            result = self.bind_voucher(cinema_id, token, voucher_code, voucher_password)
            result['voucher_code'] = voucher_code
            result['voucher_password'] = voucher_password
            results.append(result)
            
            # 添加延迟避免请求过快
            if i < len(vouchers):
                import time
                time.sleep(0.3)
        
        return results
    
    def format_bind_result(self, result: Dict) -> Tuple[bool, str]:
        """
        格式化绑券结果
        
        Args:
            result: 绑券API返回结果
            
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        voucher_code = result.get('voucher_code', '未知券码')
        
        if result.get('ret') == 0:
            if result.get('sub') == 0:
                return True, f"券 {voucher_code} 绑定成功"
            else:
                msg = result.get('msg', '未知错误')
                return False, f"券 {voucher_code} 绑定失败: {msg}"
        else:
            msg = result.get('msg', '未知错误')
            return False, f"券 {voucher_code} 请求失败: {msg}"


# 全局服务实例
_womei_voucher_service = None

def get_womei_voucher_service() -> WomeiVoucherService:
    """获取沃美绑券服务实例"""
    global _womei_voucher_service
    if _womei_voucher_service is None:
        _womei_voucher_service = WomeiVoucherService()
    return _womei_voucher_service
