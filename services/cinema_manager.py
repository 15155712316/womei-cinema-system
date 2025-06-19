import os
import json
from .cinema_info_api import validate_cinema, format_cinema_data

class CinemaManager:
    """影院信息管理器"""
    
    def __init__(self, cinema_file_path='data/cinema_info.json'):
        """
        初始化影院管理器
        参数：
            cinema_file_path: 影院信息存储文件路径
        """
        self.cinema_file_path = cinema_file_path
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(self.cinema_file_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def load_cinema_list(self):
        """
        加载影院信息列表
        返回：
            影院信息列表
        """
        if not os.path.exists(self.cinema_file_path):
            return []
        
        try:
            with open(self.cinema_file_path, 'r', encoding='utf-8') as f:
                cinemas = json.load(f)
            print(f"[影院管理] 加载影院信息成功，共 {len(cinemas)} 个影院")
            return cinemas
        except Exception as e:
            return []
    
    def save_cinema_list(self, cinemas):
        """
        保存影院信息列表
        参数：
            cinemas: 影院信息列表
        返回：
            是否保存成功
        """
        try:
            with open(self.cinema_file_path, 'w', encoding='utf-8') as f:
                json.dump(cinemas, f, ensure_ascii=False, indent=2)
            print(f"[影院管理] 保存影院信息成功，共 {len(cinemas)} 个影院")
            return True
        except Exception as e:
            return False
    
    def add_cinema_by_id(self, cinemaid):
        """
        通过影院ID添加影院
        参数：
            cinemaid: 影院ID
        返回：
            (是否成功, 错误信息或影院信息)
        """
        # 验证影院ID是否有效
        is_valid, cinema_info, base_url = validate_cinema(cinemaid)
        
        if not is_valid:
            return False, "影院ID无效或无法访问"
        
        # 格式化影院数据
        cinema_data = format_cinema_data(cinema_info, base_url, cinemaid)
        
        # 加载现有影院列表
        cinemas = self.load_cinema_list()
        
        # 检查是否已存在
        for existing_cinema in cinemas:
            if existing_cinema.get('cinemaid') == cinemaid:
                return False, f"影院ID {cinemaid} 已存在"
        
        # 添加新影院
        cinemas.append(cinema_data)
        
        # 保存影院列表
        if self.save_cinema_list(cinemas):
            return True, cinema_data
        else:
            return False, "保存影院信息失败"
    
    def delete_cinema_by_id(self, cinemaid):
        """
        通过影院ID删除影院
        参数：
            cinemaid: 影院ID
        返回：
            (是否成功, 错误信息)
        """
        cinemas = self.load_cinema_list()
        
        # 查找并删除影院
        original_count = len(cinemas)
        cinemas = [c for c in cinemas if c.get('cinemaid') != cinemaid]
        
        if len(cinemas) == original_count:
            return False, f"未找到影院ID: {cinemaid}"
        
        # 保存影院列表
        if self.save_cinema_list(cinemas):
            return True, "删除成功"
        else:
            return False, "保存影院信息失败"
    
    def update_cinema(self, cinemaid, updates):
        """
        更新影院信息
        参数：
            cinemaid: 影院ID
            updates: 要更新的字段字典
        返回：
            (是否成功, 错误信息或更新后的影院信息)
        """
        cinemas = self.load_cinema_list()
        
        # 查找并更新影院
        for i, cinema in enumerate(cinemas):
            if cinema.get('cinemaid') == cinemaid:
                cinemas[i].update(updates)
                
                # 保存影院列表
                if self.save_cinema_list(cinemas):
                    return True, cinemas[i]
                else:
                    return False, "保存影院信息失败"
        
        return False, f"未找到影院ID: {cinemaid}"
    
    def get_cinema_by_id(self, cinemaid):
        """
        通过影院ID获取影院信息
        参数：
            cinemaid: 影院ID
        返回：
            影院信息字典或None
        """
        cinemas = self.load_cinema_list()
        
        for cinema in cinemas:
            if cinema.get('cinemaid') == cinemaid:
                return cinema
        
        return None
    
    def refresh_cinema_info(self, cinemaid):
        """
        刷新指定影院的信息（从API重新获取）
        参数：
            cinemaid: 影院ID
        返回：
            (是否成功, 错误信息或更新后的影院信息)
        """
        # 获取现有影院信息
        existing_cinema = self.get_cinema_by_id(cinemaid)
        if not existing_cinema:
            return False, f"未找到影院ID: {cinemaid}"
        
        # 从API重新获取信息
        base_url = existing_cinema.get('base_url')
        if base_url:
            # 使用已知的base_url
            from .cinema_info_api import get_cinema_info
            cinema_info = get_cinema_info(base_url, cinemaid)
            
            if cinema_info:
                # 更新影院信息
                updated_data = format_cinema_data(cinema_info, base_url, cinemaid)
                return self.update_cinema(cinemaid, updated_data)
            else:
                return False, "无法从API获取最新影院信息"
        else:
            # 没有base_url，重新验证
            is_valid, cinema_info, new_base_url = validate_cinema(cinemaid)
            
            if is_valid:
                updated_data = format_cinema_data(cinema_info, new_base_url, cinemaid)
                return self.update_cinema(cinemaid, updated_data)
            else:
                return False, "影院ID已无效或无法访问"

# 创建全局影院管理器实例
cinema_manager = CinemaManager() 