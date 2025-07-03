"""
增强型智能匹配引擎

功能：
1. 高级影院名称匹配算法（相似度计算、别名映射、品牌识别）
2. 智能级联选择机制（影院→影片→场次→座位）
3. 多候选项评分和排序
4. 容错和降级处理
5. 性能优化和异步处理
"""

import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import threading
import time

from services.smart_recognition import OrderInfo, MatchResult


@dataclass
class MatchCandidate:
    """匹配候选项"""
    data: Dict[str, Any]
    score: float
    match_type: str  # 'exact', 'fuzzy', 'keyword', 'brand', 'alias'
    confidence: float
    reasons: List[str]


@dataclass
class CinemaAlias:
    """影院别名映射"""
    standard_name: str
    aliases: List[str]
    brand: str
    keywords: Set[str]


class EnhancedMatchingEngine:
    """增强型匹配引擎"""
    
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.cinema_aliases = self._init_cinema_aliases()
        self.brand_keywords = self._init_brand_keywords()
        self.match_cache = {}
        self.performance_stats = {
            'total_matches': 0,
            'successful_matches': 0,
            'average_time': 0.0
        }
    
    def _init_cinema_aliases(self) -> Dict[str, CinemaAlias]:
        """初始化影院别名映射表"""
        aliases = {
            '万达': CinemaAlias(
                standard_name='万达影城',
                aliases=['万达电影城', '万达IMAX影城', '万达国际影城', '万达影院', '万达'],
                brand='万达',
                keywords={'万达', 'WANDA', 'IMAX'}
            ),
            '苏宁': CinemaAlias(
                standard_name='苏宁影城',
                aliases=['苏宁电影城', '苏宁CGS影城', '苏宁国际影城', '苏宁'],
                brand='苏宁',
                keywords={'苏宁', 'SUNING', 'CGS', '中国巨幕'}
            ),
            'CGV': CinemaAlias(
                standard_name='CGV影城',
                aliases=['CGV电影城', 'CGV国际影城', 'CJ CGV'],
                brand='CGV',
                keywords={'CGV', 'CJ'}
            ),
            '华夏': CinemaAlias(
                standard_name='华夏影城',
                aliases=['华夏电影城', '华夏国际影城', '华夏影院'],
                brand='华夏',
                keywords={'华夏', 'HUAXIA'}
            ),
            '金逸': CinemaAlias(
                standard_name='金逸影城',
                aliases=['金逸电影城', '金逸国际影城', '金逸IMAX影城'],
                brand='金逸',
                keywords={'金逸', 'JINYI', 'IMAX'}
            ),
            '大地': CinemaAlias(
                standard_name='大地影院',
                aliases=['大地电影院', '大地数字影院', '大地影城'],
                brand='大地',
                keywords={'大地', 'DADI'}
            )
        }
        return aliases
    
    def _init_brand_keywords(self) -> Dict[str, Set[str]]:
        """初始化品牌关键词"""
        return {
            '万达': {'万达', 'WANDA', 'wanda'},
            '苏宁': {'苏宁', 'SUNING', 'suning', 'CGS', 'cgs'},
            'CGV': {'CGV', 'cgv', 'CJ'},
            '华夏': {'华夏', 'HUAXIA', 'huaxia'},
            '金逸': {'金逸', 'JINYI', 'jinyi'},
            '大地': {'大地', 'DADI', 'dadi'},
            'IMAX': {'IMAX', 'imax', '巨幕', '中国巨幕'},
            '4DX': {'4DX', '4dx', '4D'},
            'VIP': {'VIP', 'vip', '贵宾', '豪华'}
        }
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        try:
            # 使用SequenceMatcher计算相似度
            similarity = SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
            
            # 考虑长度差异的惩罚
            length_diff = abs(len(text1) - len(text2))
            max_length = max(len(text1), len(text2))
            length_penalty = length_diff / max_length if max_length > 0 else 0
            
            # 调整后的相似度
            adjusted_similarity = similarity * (1 - length_penalty * 0.3)
            
            return max(0.0, min(1.0, adjusted_similarity))
            
        except Exception as e:
            print(f"[增强匹配] 计算文本相似度失败: {e}")
            return 0.0
    
    def extract_brand_from_name(self, cinema_name: str) -> Optional[str]:
        """从影院名称中提取品牌"""
        try:
            cinema_name_lower = cinema_name.lower()
            
            for brand, keywords in self.brand_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in cinema_name_lower:
                        return brand
            
            return None
            
        except Exception as e:
            print(f"[增强匹配] 提取品牌失败: {e}")
            return None
    
    def find_cinema_candidates(self, order_cinema_name: str, cinemas_data: List[Dict]) -> List[MatchCandidate]:
        """查找影院候选项"""
        try:
            candidates = []
            order_name_lower = order_cinema_name.lower()
            order_brand = self.extract_brand_from_name(order_cinema_name)
            
            print(f"[增强匹配] 查找影院候选项: {order_cinema_name}, 识别品牌: {order_brand}")
            
            for cinema in cinemas_data:
                cinema_name = cinema.get('cinemaShortName', '')
                if not cinema_name:
                    continue
                
                cinema_name_lower = cinema_name.lower()
                reasons = []
                score = 0.0
                match_type = 'none'
                
                # 1. 精确匹配
                if cinema_name == order_cinema_name:
                    score = 1.0
                    match_type = 'exact'
                    reasons.append('精确匹配')
                
                # 2. 别名匹配
                elif self._check_alias_match(order_cinema_name, cinema_name):
                    score = 0.95
                    match_type = 'alias'
                    reasons.append('别名匹配')
                
                # 3. 品牌匹配
                elif order_brand and self._check_brand_match(order_brand, cinema_name):
                    brand_score = self._calculate_brand_score(order_cinema_name, cinema_name, order_brand)
                    if brand_score > 0.7:
                        score = brand_score
                        match_type = 'brand'
                        reasons.append(f'品牌匹配({order_brand})')
                
                # 4. 相似度匹配
                else:
                    similarity = self.calculate_text_similarity(order_cinema_name, cinema_name)
                    if similarity > 0.6:
                        score = similarity
                        match_type = 'fuzzy'
                        reasons.append(f'相似度匹配({similarity:.2f})')
                
                # 5. 关键词匹配
                if score < 0.6:
                    keyword_score = self._calculate_keyword_score(order_cinema_name, cinema_name)
                    if keyword_score > score:
                        score = keyword_score
                        match_type = 'keyword'
                        reasons.append(f'关键词匹配({keyword_score:.2f})')
                
                # 添加候选项
                if score > 0.5:  # 只保留得分较高的候选项
                    confidence = self._calculate_confidence(score, match_type, reasons)
                    candidates.append(MatchCandidate(
                        data=cinema,
                        score=score,
                        match_type=match_type,
                        confidence=confidence,
                        reasons=reasons
                    ))
            
            # 按得分排序
            candidates.sort(key=lambda x: x.score, reverse=True)
            
            print(f"[增强匹配] 找到 {len(candidates)} 个候选项")
            for i, candidate in enumerate(candidates[:3]):  # 只打印前3个
                print(f"  {i+1}. {candidate.data.get('cinemaShortName')} (得分: {candidate.score:.2f}, 类型: {candidate.match_type})")
            
            return candidates
            
        except Exception as e:
            print(f"[增强匹配] 查找影院候选项失败: {e}")
            return []
    
    def _check_alias_match(self, order_name: str, cinema_name: str) -> bool:
        """检查别名匹配"""
        try:
            for alias_info in self.cinema_aliases.values():
                if order_name in alias_info.aliases and cinema_name in alias_info.aliases:
                    return True
                if cinema_name == alias_info.standard_name and order_name in alias_info.aliases:
                    return True
                if order_name == alias_info.standard_name and cinema_name in alias_info.aliases:
                    return True
            return False
        except:
            return False
    
    def _check_brand_match(self, brand: str, cinema_name: str) -> bool:
        """检查品牌匹配"""
        try:
            if brand in self.brand_keywords:
                keywords = self.brand_keywords[brand]
                cinema_name_lower = cinema_name.lower()
                return any(keyword.lower() in cinema_name_lower for keyword in keywords)
            return False
        except:
            return False
    
    def _calculate_brand_score(self, order_name: str, cinema_name: str, brand: str) -> float:
        """计算品牌匹配得分"""
        try:
            base_score = 0.8  # 品牌匹配基础分
            
            # 检查地理位置信息匹配
            location_bonus = self._check_location_match(order_name, cinema_name)
            
            # 检查特殊标识匹配（如IMAX、VIP等）
            feature_bonus = self._check_feature_match(order_name, cinema_name)
            
            # 计算最终得分
            final_score = base_score + location_bonus + feature_bonus
            return min(1.0, final_score)
            
        except:
            return 0.8
    
    def _check_location_match(self, order_name: str, cinema_name: str) -> float:
        """检查地理位置匹配"""
        try:
            # 提取可能的地理位置信息
            location_keywords = ['店', '分店', '广场', '中心', '大厦', '商场', '购物', '区', '路', '街']
            
            order_locations = []
            cinema_locations = []
            
            for keyword in location_keywords:
                if keyword in order_name:
                    # 提取位置相关的词汇
                    parts = order_name.split(keyword)
                    if len(parts) > 1:
                        order_locations.extend([part.strip() for part in parts if part.strip()])
                
                if keyword in cinema_name:
                    parts = cinema_name.split(keyword)
                    if len(parts) > 1:
                        cinema_locations.extend([part.strip() for part in parts if part.strip()])
            
            # 计算位置匹配度
            if order_locations and cinema_locations:
                matches = 0
                for order_loc in order_locations:
                    for cinema_loc in cinema_locations:
                        if order_loc in cinema_loc or cinema_loc in order_loc:
                            matches += 1
                
                if matches > 0:
                    return 0.1  # 位置匹配奖励
            
            return 0.0
            
        except:
            return 0.0
    
    def _check_feature_match(self, order_name: str, cinema_name: str) -> float:
        """检查特殊功能匹配"""
        try:
            feature_keywords = ['IMAX', 'imax', '巨幕', '4DX', '4dx', 'VIP', 'vip', '贵宾', '豪华']
            
            order_features = set()
            cinema_features = set()
            
            for keyword in feature_keywords:
                if keyword.lower() in order_name.lower():
                    order_features.add(keyword.lower())
                if keyword.lower() in cinema_name.lower():
                    cinema_features.add(keyword.lower())
            
            # 计算特殊功能匹配度
            if order_features and cinema_features:
                common_features = order_features & cinema_features
                if common_features:
                    return 0.05 * len(common_features)  # 每个匹配的特殊功能加0.05分
            
            return 0.0
            
        except:
            return 0.0
    
    def _calculate_keyword_score(self, order_name: str, cinema_name: str) -> float:
        """计算关键词匹配得分"""
        try:
            # 提取关键词
            order_keywords = self._extract_enhanced_keywords(order_name)
            cinema_keywords = self._extract_enhanced_keywords(cinema_name)
            
            if not order_keywords or not cinema_keywords:
                return 0.0
            
            # 计算关键词匹配度
            common_keywords = set(order_keywords) & set(cinema_keywords)
            total_keywords = set(order_keywords) | set(cinema_keywords)
            
            if total_keywords:
                jaccard_similarity = len(common_keywords) / len(total_keywords)
                
                # 考虑重要关键词的权重
                important_matches = 0
                for keyword in common_keywords:
                    if len(keyword) >= 3:  # 长关键词更重要
                        important_matches += 1
                
                # 计算最终得分
                base_score = jaccard_similarity
                importance_bonus = important_matches * 0.1
                
                return min(0.9, base_score + importance_bonus)
            
            return 0.0
            
        except:
            return 0.0
    
    def _extract_enhanced_keywords(self, text: str) -> List[str]:
        """增强的关键词提取"""
        try:
            # 移除常见的无意义词汇
            stop_words = {'影城', '电影院', '店', '分店', '的', '和', '与', '及'}
            
            keywords = []
            
            # 提取中文词汇
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
            for chars in chinese_chars:
                if len(chars) >= 2 and chars not in stop_words:
                    keywords.append(chars)
                    
                    # 提取子词汇（但更智能）
                    if len(chars) > 3:
                        # 只提取可能有意义的子词汇
                        for i in range(len(chars) - 1):
                            sub_word = chars[i:i+2]
                            if sub_word not in stop_words and len(sub_word) >= 2:
                                keywords.append(sub_word)
            
            # 提取英文词汇
            english_words = re.findall(r'[A-Za-z]+', text)
            for word in english_words:
                if len(word) >= 2:
                    keywords.append(word.upper())
            
            # 提取数字（可能是店铺编号等）
            numbers = re.findall(r'\d+', text)
            keywords.extend(numbers)
            
            # 去重并返回
            return list(set(keywords))
            
        except:
            return []
    
    def _calculate_confidence(self, score: float, match_type: str, reasons: List[str]) -> float:
        """计算匹配置信度"""
        try:
            # 基础置信度
            base_confidence = score
            
            # 根据匹配类型调整置信度
            type_multipliers = {
                'exact': 1.0,
                'alias': 0.95,
                'brand': 0.85,
                'fuzzy': 0.75,
                'keyword': 0.65
            }
            
            type_multiplier = type_multipliers.get(match_type, 0.5)
            
            # 根据匹配原因数量调整
            reason_bonus = min(0.1, len(reasons) * 0.02)
            
            # 计算最终置信度
            confidence = base_confidence * type_multiplier + reason_bonus
            
            return min(1.0, max(0.0, confidence))
            
        except:
            return score * 0.8
    
    async def enhanced_cinema_match(self, order_info: OrderInfo, cinemas_data: List[Dict]) -> Optional[Dict[str, Any]]:
        """增强的影院匹配"""
        try:
            start_time = time.time()
            
            if not order_info.cinema_name or not cinemas_data:
                return None
            
            
            # 检查缓存
            cache_key = f"cinema_{order_info.cinema_name}"
            if cache_key in self.match_cache:
                print(f"[增强匹配] 使用缓存结果")
                return self.match_cache[cache_key]
            
            # 查找候选项
            candidates = self.find_cinema_candidates(order_info.cinema_name, cinemas_data)
            
            if not candidates:
                print(f"[增强匹配] 未找到任何候选项")
                return None
            
            # 选择最佳候选项
            best_candidate = candidates[0]
            
            # 如果最佳候选项得分太低，返回None
            if best_candidate.score < 0.6:
                print(f"[增强匹配] 最佳候选项得分过低: {best_candidate.score:.2f}")
                return None
            
            # 缓存结果
            self.match_cache[cache_key] = best_candidate.data
            
            # 更新性能统计
            elapsed_time = time.time() - start_time
            self._update_performance_stats(elapsed_time, True)
            
            print(f"[增强匹配] 匹配成功: {best_candidate.data.get('cinemaShortName')} (得分: {best_candidate.score:.2f})")
            
            return best_candidate.data
            
        except Exception as e:
            print(f"[增强匹配] 增强影院匹配失败: {e}")
            return None
    
    def _update_performance_stats(self, elapsed_time: float, success: bool):
        """更新性能统计"""
        try:
            self.performance_stats['total_matches'] += 1
            if success:
                self.performance_stats['successful_matches'] += 1
            
            # 更新平均时间
            total_time = self.performance_stats['average_time'] * (self.performance_stats['total_matches'] - 1)
            self.performance_stats['average_time'] = (total_time + elapsed_time) / self.performance_stats['total_matches']
            
        except:
            pass
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        try:
            total = self.performance_stats['total_matches']
            successful = self.performance_stats['successful_matches']
            
            return {
                'total_matches': total,
                'successful_matches': successful,
                'success_rate': successful / total if total > 0 else 0.0,
                'average_time': self.performance_stats['average_time'],
                'cache_size': len(self.match_cache)
            }
        except:
            return {}
    
    def clear_cache(self):
        """清空缓存"""
        self.match_cache.clear()
        print(f"[增强匹配] 缓存已清空")
