#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美影院服务
专门处理沃美系统的影院数据，替代旧的cinema_manager
"""

class WomeiCinemaService:
    """沃美影院服务"""
    
    def __init__(self):
        self.current_cinema = None
        self.cinemas_cache = []
    
    def set_current_cinema(self, cinema_data):
        """设置当前选择的影院"""
        self.current_cinema = cinema_data
        print(f"[沃美影院] 设置当前影院: {cinema_data.get('cinema_name', '未知')}")
    
    def get_current_cinema_id(self):
        """获取当前影院ID"""
        if self.current_cinema:
            return self.current_cinema.get('cinema_id', '')
        return ''
    
    def get_current_cinema_name(self):
        """获取当前影院名称"""
        if self.current_cinema:
            return self.current_cinema.get('cinema_name', '未知影院')
        return '未知影院'
    
    def validate_cinema_id(self, cinema_id):
        """验证影院ID是否有效"""
        return bool(cinema_id and len(cinema_id) > 0)

# 全局实例
womei_cinema_service = WomeiCinemaService()

def get_womei_cinema_service():
    """获取沃美影院服务实例"""
    return womei_cinema_service
