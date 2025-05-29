#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器码生成工具
"""

import hashlib
import platform
import subprocess
import os


def get_machine_code():
    """
    获取当前机器的唯一标识码
    
    Returns:
        str: 机器码
    """
    try:
        # 获取CPU序列号
        cpu_info = _get_cpu_serial()
        
        # 获取主板序列号
        motherboard_info = _get_motherboard_serial()
        
        # 获取网卡MAC地址
        mac_info = _get_mac_address()
        
        # 获取硬盘序列号
        disk_info = _get_disk_serial()
        
        # 组合所有硬件信息
        hardware_info = f"{cpu_info}|{motherboard_info}|{mac_info}|{disk_info}"
        
        # 生成MD5哈希
        machine_code = hashlib.md5(hardware_info.encode()).hexdigest()
        
        return machine_code.upper()
        
    except Exception as e:
        print(f"获取机器码失败: {e}")
        # 返回备用机器码
        return "DEFAULT_MACHINE_CODE"


def _get_cpu_serial():
    """获取CPU序列号"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'cpu', 'get', 'ProcessorId'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line != "ProcessorId":
                        return line
        elif platform.system() == "Linux":
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'serial' in line.lower():
                        return line.split(':')[1].strip()
        
        return platform.processor()
        
    except Exception:
        return "UNKNOWN_CPU"


def _get_motherboard_serial():
    """获取主板序列号"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'baseboard', 'get', 'SerialNumber'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line != "SerialNumber" and line != "To be filled by O.E.M.":
                        return line
        
        return "UNKNOWN_MOTHERBOARD"
        
    except Exception:
        return "UNKNOWN_MOTHERBOARD"


def _get_mac_address():
    """获取网卡MAC地址"""
    try:
        import uuid
        mac = uuid.getnode()
        mac_address = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
        return mac_address
        
    except Exception:
        return "UNKNOWN_MAC"


def _get_disk_serial():
    """获取硬盘序列号"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['wmic', 'diskdrive', 'get', 'SerialNumber'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line != "SerialNumber":
                        return line
        elif platform.system() == "Linux":
            result = subprocess.run(
                ['lsblk', '-d', '-o', 'SERIAL'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    return lines[1].strip()
        
        return "UNKNOWN_DISK"
        
    except Exception:
        return "UNKNOWN_DISK"


if __name__ == "__main__":
    # 测试机器码生成
    code = get_machine_code()
    print(f"当前机器码: {code}") 