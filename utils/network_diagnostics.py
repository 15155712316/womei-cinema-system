import socket
import requests
import subprocess
import platform
import time
from typing import Dict, List, Tuple

class NetworkDiagnostics:
    """网络诊断工具类"""
    
    @staticmethod
    def run_diagnostics(target_host: str, target_port: int = 5000) -> Dict:
        """运行完整的网络诊断"""
        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target": f"{target_host}:{target_port}",
            "tests": []
        }
        
        # 1. DNS解析测试
        dns_result = NetworkDiagnostics.check_dns(target_host)
        results["tests"].append(dns_result)
        
        # 如果DNS解析失败，后续测试无法进行
        if not dns_result["success"]:
            return results
        
        # 2. ICMP Ping测试
        ping_result = NetworkDiagnostics.check_ping(target_host)
        results["tests"].append(ping_result)
        
        # 3. TCP连接测试
        tcp_result = NetworkDiagnostics.check_tcp_connection(target_host, target_port)
        results["tests"].append(tcp_result)
        
        # 4. HTTP连接测试
        http_result = NetworkDiagnostics.check_http_connection(f"http://{target_host}:{target_port}")
        results["tests"].append(http_result)
        
        # 5. 路由跟踪
        traceroute_result = NetworkDiagnostics.run_traceroute(target_host)
        results["tests"].append(traceroute_result)
        
        return results
    
    @staticmethod
    def check_dns(hostname: str) -> Dict:
        """检查DNS解析"""
        try:
            ip_address = socket.gethostbyname(hostname)
            return {
                "test": "DNS解析",
                "success": True,
                "message": f"成功解析到IP: {ip_address}"
            }
        except socket.gaierror as e:
            return {
                "test": "DNS解析",
                "success": False,
                "message": f"DNS解析失败: {str(e)}"
            }
    
    @staticmethod
    def check_ping(hostname: str, count: int = 4) -> Dict:
        """检查ICMP Ping连通性"""
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, str(count), hostname]
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                return {
                    "test": "ICMP Ping",
                    "success": True,
                    "message": "Ping测试成功"
                }
            else:
                return {
                    "test": "ICMP Ping",
                    "success": False,
                    "message": f"Ping测试失败: {stderr.decode('utf-8', errors='ignore')}"
                }
        except Exception as e:
            return {
                "test": "ICMP Ping",
                "success": False,
                "message": f"Ping测试异常: {str(e)}"
            }
    
    @staticmethod
    def check_tcp_connection(hostname: str, port: int, timeout: int = 5) -> Dict:
        """检查TCP连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            start_time = time.time()
            result = sock.connect_ex((hostname, port))
            connection_time = time.time() - start_time
            
            sock.close()
            
            if result == 0:
                return {
                    "test": "TCP连接",
                    "success": True,
                    "message": f"TCP连接成功，耗时: {connection_time:.2f}秒"
                }
            else:
                return {
                    "test": "TCP连接",
                    "success": False,
                    "message": f"TCP连接失败，错误码: {result}"
                }
        except Exception as e:
            return {
                "test": "TCP连接",
                "success": False,
                "message": f"TCP连接异常: {str(e)}"
            }
    
    @staticmethod
    def check_http_connection(url: str, timeout: int = 5) -> Dict:
        """检查HTTP连接"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, verify=False)
            request_time = time.time() - start_time
            
            return {
                "test": "HTTP连接",
                "success": response.status_code < 400,
                "message": f"HTTP状态码: {response.status_code}，耗时: {request_time:.2f}秒"
            }
        except requests.exceptions.ConnectionError:
            return {
                "test": "HTTP连接",
                "success": False,
                "message": "HTTP连接被拒绝"
            }
        except requests.exceptions.Timeout:
            return {
                "test": "HTTP连接",
                "success": False,
                "message": "HTTP连接超时"
            }
        except Exception as e:
            return {
                "test": "HTTP连接",
                "success": False,
                "message": f"HTTP连接异常: {str(e)}"
            }
    
    @staticmethod
    def run_traceroute(hostname: str) -> Dict:
        """运行路由跟踪"""
        try:
            command = ["tracert" if platform.system().lower() == "windows" else "traceroute", hostname]
            
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            return {
                "test": "路由跟踪",
                "success": process.returncode == 0,
                "message": stdout.decode('utf-8', errors='ignore')
            }
        except Exception as e:
            return {
                "test": "路由跟踪",
                "success": False,
                "message": f"路由跟踪异常: {str(e)}"
            }