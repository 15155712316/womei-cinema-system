import requests
import urllib3
import json

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class APIBase:
    """API基础服务类 - 提供动态base_url的API调用功能"""
    
    def __init__(self):
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'xweb_xhr': '1',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
    
    def get_base_url_for_cinema(self, cinemaid):
        """
        根据影院ID获取对应的base_url
        参数：
            cinemaid: 影院ID
        返回：
            base_url字符串，找不到则返回None
        """
        try:
            from .film_service import load_cinemas
            cinemas = load_cinemas()
            
            for cinema in cinemas:
                if cinema.get('cinemaid') == cinemaid:
                    base_url = cinema.get('base_url')
                    if not base_url:
                        # 尝试其他可能的字段名
                        base_url = cinema.get('baseUrl')
                    if base_url:
                        print(f"[API基础] 找到影院 {cinemaid} 的base_url: {base_url}")
                        return base_url
            
            print(f"[API基础] 未找到影院 {cinemaid} 的base_url，使用默认")
            return 'zcxzs7.cityfilms.cn'  # 默认使用万友影城域名
            
        except Exception as e:
            print(f"[API基础] 获取base_url异常: {e}")
            return 'zcxzs7.cityfilms.cn'  # 异常时使用默认域名
    
    def build_url(self, base_url, path):
        """
        构建完整的API URL
        参数：
            base_url: 基础域名
            path: API路径
        返回：
            完整的URL
        """
        if base_url.startswith('http'):
            return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        else:
            return f"https://{base_url.rstrip('/')}/{path.lstrip('/')}"
    
    def make_request(self, method, base_url, path, params=None, data=None, headers=None, timeout=10):
        """
        统一的API请求方法
        参数：
            method: 请求方法 ('GET' 或 'POST')
            base_url: 基础域名
            path: API路径
            params: GET参数
            data: POST数据
            headers: 自定义请求头
            timeout: 超时时间
        返回：
            响应的JSON数据
        """
        url = self.build_url(base_url, path)
        
        # 合并请求头
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
        
        print(f"[API请求] {method} {url}")
        print(f"[API请求] 参数: {params if method == 'GET' else data}")
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=request_headers, timeout=timeout, verify=False)
            else:  # POST
                response = requests.post(url, data=data, headers=request_headers, timeout=timeout, verify=False)
            
            print(f"[API响应] 状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    # 处理BOM编码
                    content = response.content.decode('utf-8-sig')
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    print(f"[API响应] JSON解析失败: {e}")
                    return {"resultCode": "-1", "resultDesc": f"JSON解析失败: {e}", "resultData": None}
            else:
                return {"resultCode": "-1", "resultDesc": f"HTTP错误: {response.status_code}", "resultData": None}
                
        except requests.exceptions.RequestException as e:
            print(f"[API请求] 网络异常: {e}")
            return {"resultCode": "-1", "resultDesc": f"网络异常: {e}", "resultData": None}
        except Exception as e:
            print(f"[API请求] 未知异常: {e}")
            return {"resultCode": "-1", "resultDesc": f"未知异常: {e}", "resultData": None}

# 创建全局API基础服务实例
api_base = APIBase()

# 便捷函数：根据影院ID自动选择base_url并发送请求
def api_request(method, path, cinemaid, params=None, data=None, headers=None, timeout=10):
    """
    便捷的API请求函数 - 自动根据影院ID选择base_url
    参数：
        method: 请求方法
        path: API路径
        cinemaid: 影院ID
        params: GET参数
        data: POST数据
        headers: 自定义请求头
        timeout: 超时时间
    返回：
        响应的JSON数据
    """
    base_url = api_base.get_base_url_for_cinema(cinemaid)
    return api_base.make_request(method, base_url, path, params, data, headers, timeout)

def api_get(path, cinemaid, params=None, headers=None, timeout=10):
    """GET请求的便捷函数"""
    return api_request('GET', path, cinemaid, params=params, headers=headers, timeout=timeout)

def api_post(path, cinemaid, data=None, headers=None, timeout=10):
    """POST请求的便捷函数"""
    return api_request('POST', path, cinemaid, data=data, headers=headers, timeout=timeout) 