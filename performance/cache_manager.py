#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理器 - 提升API调用和数据处理性能
自动生成，用于第三阶段D性能优化
"""

import time
import threading
from typing import Any, Dict, Optional, Callable
from functools import wraps

class CacheManager:
    """缓存管理器"""
    
    def __init__(self, default_ttl: int = 300):  # 默认5分钟过期
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        with self._lock:
            if key in self._cache:
                cache_item = self._cache[key]
                if time.time() < cache_item['expires']:
                    cache_item['hits'] += 1
                    return cache_item['data']
                else:
                    # 缓存过期，删除
                    del self._cache[key]
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        """设置缓存数据"""
        with self._lock:
            expires = time.time() + (ttl or self.default_ttl)
            self._cache[key] = {
                'data': data,
                'expires': expires,
                'created': time.time(),
                'hits': 0
            }
    
    def delete(self, key: str) -> bool:
        """删除缓存数据"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, item in self._cache.items()
                if current_time >= item['expires']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_items = len(self._cache)
            total_hits = sum(item['hits'] for item in self._cache.values())
            
            return {
                'total_items': total_items,
                'total_hits': total_hits,
                'memory_usage': self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> int:
        """估算内存使用量（字节）"""
        # 简单估算，实际使用中可以更精确
        import sys
        total_size = 0
        for key, item in self._cache.items():
            total_size += sys.getsizeof(key)
            total_size += sys.getsizeof(item['data'])
            total_size += sys.getsizeof(item)
        return total_size

def cache_result(ttl: int = 300, key_func: Optional[Callable] = None):
    """缓存结果装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 尝试从缓存获取
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 全局缓存管理器实例
cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """获取缓存管理器实例"""
    return cache_manager

def clear_all_cache():
    """清空所有缓存"""
    cache_manager.clear()

def cleanup_expired_cache() -> int:
    """清理过期缓存"""
    return cache_manager.cleanup_expired()
