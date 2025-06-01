#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 独立测试影片API
"""

import requests
import json

def test_film_api():
    """测试影片API"""
    
    # 测试参数（请替换为真实值）
    params = {
        'userid': '15155712316',
        'openid': 'your_real_openid_here',
        'token': 'your_real_token_here',
        'cinemaid': '35fec8259e74'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'xweb_xhr': '1',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx1234567890123456/1/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    url = 'https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniFilm/getFilms'
    
    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"解析结果: {data}")
        
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_film_api()
