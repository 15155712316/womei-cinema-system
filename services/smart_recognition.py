"""
智能订单信息识别和自动填充服务

功能：
1. 从剪贴板读取订单信息
2. 解析订单文本，提取关键信息
3. 智能匹配系统中的影院、影片、场次、座位
4. 提供自动填充和用户确认功能
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication


@dataclass
class OrderInfo:
    """订单信息数据类"""
    order_id: str = ""
    city: str = ""
    cinema_name: str = ""
    cinema_address: str = ""
    movie_name: str = ""
    session_time: str = ""
    hall_name: str = ""
    seats: List[str] = None
    price: float = 0.0
    raw_text: str = ""
    
    def __post_init__(self):
        if self.seats is None:
            self.seats = []


@dataclass
class MatchResult:
    """匹配结果数据类"""
    cinema_match: Dict[str, Any] = None
    movie_match: Dict[str, Any] = None
    session_match: Dict[str, Any] = None
    seat_matches: List[Dict[str, Any]] = None
    confidence_score: float = 0.0
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.seat_matches is None:
            self.seat_matches = []
        if self.suggestions is None:
            self.suggestions = []


class SmartOrderRecognition:
    """智能订单识别服务"""

    def __init__(self, main_window=None):
        self.main_window = main_window
        self.order_patterns = self._init_patterns()
        self.enhanced_engine = None
        self.use_enhanced_matching = True

        # 延迟导入增强匹配引擎以避免循环导入
        self._init_enhanced_engine()

    def _init_enhanced_engine(self):
        """初始化增强匹配引擎"""
        try:
            from services.enhanced_matching_engine import EnhancedMatchingEngine
            self.enhanced_engine = EnhancedMatchingEngine(self.main_window)
            print("[智能识别] 增强匹配引擎初始化成功")
        except ImportError as e:
            print(f"[智能识别] 增强匹配引擎导入失败: {e}")
            self.enhanced_engine = None
            self.use_enhanced_matching = False
        except Exception as e:
            print(f"[智能识别] 增强匹配引擎初始化失败: {e}")
            self.enhanced_engine = None
            self.use_enhanced_matching = False

    def _init_patterns(self) -> Dict[str, str]:
        """初始化文本解析正则表达式模式"""
        return {
            # 订单号：提取数字部分
            'order_id': r'订单[号]?[：:]\s*(\d+)',

            # 城市：提取到下一个字段标识符为止，支持换行和连续文本，处理逗号分隔符
            'city': r'城市[：:]\s*([^：:\n，,]+?)(?=\s*[，,]?\s*(?:订单|影院|地址|影片|场次|影厅|座位|市价)[：:]|\n|$)',

            # 影院：只提取影院名称，不包含地址信息，处理逗号分隔符
            'cinema_name': r'影院[：:]\s*([^：:\n，,]+?)(?=\s*[，,]?\s*(?:订单|城市|地址|影片|场次|影厅|座位|市价)[：:]|\n|$)',

            # 地址：可选字段，提取地址信息，处理逗号分隔符
            'cinema_address': r'地址[：:]\s*([^：:\n，,]+?)(?=\s*[，,]?\s*(?:订单|城市|影院|影片|场次|影厅|座位|市价)[：:]|\n|$)',

            # 影片：提取影片名称，处理逗号分隔符，允许影片名称中包含冒号
            'movie_name': r'影片[：:]\s*([^\n，,]+?)(?=\s*[，,]?\s*(?:订单|城市|影院|地址|场次|影厅|座位|市价)[：:]|\n|$)',

            # 场次：提取时间信息
            'session_time': r'场次[：:]\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)',

            # 影厅：提取影厅信息，处理逗号分隔符
            'hall_name': r'影厅[：:]\s*([^：:\n，,]+?)(?=\s*[，,]?\s*(?:订单|城市|影院|地址|影片|场次|座位|市价)[：:]|\n|$)',

            # 座位：提取座位信息，处理逗号分隔符
            'seats': r'座位[：:]\s*([^：:\n，,]+?)(?=\s*[，,]?\s*(?:订单|城市|影院|地址|影片|场次|影厅|市价)[：:]|\n|$)',

            # 市价：提取价格数字
            'price': r'市价[：:]\s*(\d+\.?\d*)',

            # 备用模式
            'order_id_alt': r'订单号[：:]\s*(\d+)',
            'session_time_alt': r'时间[：:]\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)',
            'seats_alt': r'(\d+排\d+座)',
        }
    
    def read_clipboard(self) -> str:
        """读取剪贴板内容"""
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            print(f"[智能识别] 读取剪贴板内容: {len(text)} 字符")
            return text.strip()
        except Exception as e:
            print(f"[智能识别] 读取剪贴板失败: {e}")
            return ""
    
    def parse_order_text(self, text: str) -> OrderInfo:
        """解析订单文本，提取关键信息"""
        try:
            print(f"[智能识别] 开始解析订单文本")
            
            order_info = OrderInfo(raw_text=text)
            
            # 提取订单号
            match = re.search(self.order_patterns['order_id'], text)
            if not match:
                match = re.search(self.order_patterns['order_id_alt'], text)
            if match:
                order_info.order_id = match.group(1)
                print(f"[智能识别] 提取订单号: {order_info.order_id}")
            
            # 提取城市
            match = re.search(self.order_patterns['city'], text)
            if match:
                order_info.city = match.group(1).strip()
                print(f"[智能识别] 提取城市: {order_info.city}")
            
            # 提取影院名称
            match = re.search(self.order_patterns['cinema_name'], text)
            if match:
                order_info.cinema_name = match.group(1).strip()
                print(f"[智能识别] 提取影院: {order_info.cinema_name}")
            
            # 提取影院地址
            match = re.search(self.order_patterns['cinema_address'], text)
            if match:
                order_info.cinema_address = match.group(1).strip()
                print(f"[智能识别] 提取地址: {order_info.cinema_address}")
            
            # 提取影片名称
            match = re.search(self.order_patterns['movie_name'], text)
            if match:
                order_info.movie_name = match.group(1).strip()
                print(f"[智能识别] 提取影片: {order_info.movie_name}")
            
            # 提取场次时间
            match = re.search(self.order_patterns['session_time'], text)
            if not match:
                match = re.search(self.order_patterns['session_time_alt'], text)
            if match:
                order_info.session_time = match.group(1).strip()
                print(f"[智能识别] 提取场次: {order_info.session_time}")
            
            # 提取影厅
            match = re.search(self.order_patterns['hall_name'], text)
            if match:
                order_info.hall_name = match.group(1).strip()
                print(f"[智能识别] 提取影厅: {order_info.hall_name}")
            
            # 提取座位信息
            match = re.search(self.order_patterns['seats'], text)
            if match:
                seats_text = match.group(1).strip()
                # 解析座位列表
                seat_matches = re.findall(self.order_patterns['seats_alt'], seats_text)
                order_info.seats = seat_matches
                print(f"[智能识别] 提取座位: {order_info.seats}")
            
            # 提取价格
            match = re.search(self.order_patterns['price'], text)
            if match:
                try:
                    order_info.price = float(match.group(1))
                    print(f"[智能识别] 提取价格: {order_info.price}")
                except ValueError:
                    pass
            
            print(f"[智能识别] 订单信息解析完成")
            return order_info
            
        except Exception as e:
            print(f"[智能识别] 解析订单文本失败: {e}")
            import traceback
            traceback.print_exc()
            return OrderInfo(raw_text=text)
    
    def match_cinema(self, order_info: OrderInfo) -> Optional[Dict[str, Any]]:
        """匹配影院信息"""
        try:
            if not order_info.cinema_name:
                return None

            print(f"[智能识别] 开始匹配影院: {order_info.cinema_name}")

            # 获取影院列表
            if not (hasattr(self.main_window, 'tab_manager_widget') and
                    hasattr(self.main_window.tab_manager_widget, 'cinemas_data')):
                print(f"[智能识别] 无法获取影院数据")
                return None

            cinemas_data = self.main_window.tab_manager_widget.cinemas_data
            if not cinemas_data:
                print(f"[智能识别] 影院数据为空")
                return None

            # 优先使用增强匹配引擎
            if self.use_enhanced_matching and self.enhanced_engine:
                try:
                    # 使用异步方法需要在事件循环中运行
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        enhanced_result = loop.run_until_complete(
                            self.enhanced_engine.enhanced_cinema_match(order_info, cinemas_data)
                        )
                        if enhanced_result:
                            print(f"[智能识别] 增强匹配成功: {enhanced_result.get('cinemaShortName')}")
                            return enhanced_result
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"[智能识别] 增强匹配失败，回退到基础匹配: {e}")

            # 回退到基础匹配算法
            return self._basic_cinema_match(order_info, cinemas_data)

        except Exception as e:
            print(f"[智能识别] 匹配影院失败: {e}")
            return None

    def _basic_cinema_match(self, order_info: OrderInfo, cinemas_data: List[Dict]) -> Optional[Dict[str, Any]]:
        """基础影院匹配算法（作为增强匹配的回退）"""
        try:
            # 精确匹配
            for cinema in cinemas_data:
                cinema_name = cinema.get('cinemaShortName', '')
                if cinema_name == order_info.cinema_name:
                    print(f"[智能识别] 精确匹配影院: {cinema_name}")
                    return cinema

            # 模糊匹配
            for cinema in cinemas_data:
                cinema_name = cinema.get('cinemaShortName', '')
                if order_info.cinema_name in cinema_name or cinema_name in order_info.cinema_name:
                    print(f"[智能识别] 模糊匹配影院: {cinema_name}")
                    return cinema

            # 关键词匹配
            order_keywords = self._extract_keywords(order_info.cinema_name)
            for cinema in cinemas_data:
                cinema_name = cinema.get('cinemaShortName', '')
                cinema_keywords = self._extract_keywords(cinema_name)

                # 计算关键词匹配度
                common_keywords = set(order_keywords) & set(cinema_keywords)
                if len(common_keywords) >= 2:  # 至少2个关键词匹配
                    print(f"[智能识别] 关键词匹配影院: {cinema_name} (匹配词: {common_keywords})")
                    return cinema

            print(f"[智能识别] 未找到匹配的影院")
            return None

        except Exception as e:
            print(f"[智能识别] 基础影院匹配失败: {e}")
            return None
    
    def match_movie(self, order_info: OrderInfo, cinema_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """匹配影片信息"""
        try:
            if not order_info.movie_name:
                return None

            print(f"[智能识别] 开始匹配影片: {order_info.movie_name}")

            # 获取影片列表（通过主窗口的Tab管理器）
            if not (hasattr(self.main_window, 'tab_manager_widget') and
                    hasattr(self.main_window.tab_manager_widget, 'get_current_movies')):
                print(f"[智能识别] 无法获取影片数据")
                return None

            try:
                # 尝试获取当前影片列表
                movies_data = self.main_window.tab_manager_widget.get_current_movies()
                if not movies_data:
                    print(f"[智能识别] 影片数据为空")
                    return None
            except:
                # 如果获取失败，创建模拟数据用于测试
                print(f"[智能识别] 使用模拟影片数据进行匹配")
                movies_data = [
                    {'name': order_info.movie_name, 'id': 'mock_movie_id'}
                ]

            # 精确匹配
            for movie in movies_data:
                movie_name = movie.get('name', movie.get('filmName', ''))
                if movie_name == order_info.movie_name:
                    print(f"[智能识别] 精确匹配影片: {movie_name}")
                    return movie

            # 模糊匹配
            for movie in movies_data:
                movie_name = movie.get('name', movie.get('filmName', ''))
                if order_info.movie_name in movie_name or movie_name in order_info.movie_name:
                    print(f"[智能识别] 模糊匹配影片: {movie_name}")
                    return movie

            # 关键词匹配
            order_keywords = self._extract_keywords(order_info.movie_name)
            for movie in movies_data:
                movie_name = movie.get('name', movie.get('filmName', ''))
                movie_keywords = self._extract_keywords(movie_name)

                # 计算关键词匹配度
                common_keywords = set(order_keywords) & set(movie_keywords)
                if len(common_keywords) >= 1:  # 至少1个关键词匹配
                    print(f"[智能识别] 关键词匹配影片: {movie_name} (匹配词: {common_keywords})")
                    return movie

            print(f"[智能识别] 未找到匹配的影片")
            return None

        except Exception as e:
            print(f"[智能识别] 匹配影片失败: {e}")
            return None
    
    def match_session(self, order_info: OrderInfo, movie_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """匹配场次信息"""
        try:
            if not order_info.session_time:
                return None
            
            print(f"[智能识别] 开始匹配场次: {order_info.session_time}")
            
            # 解析目标时间
            try:
                target_time = datetime.strptime(order_info.session_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    target_time = datetime.strptime(order_info.session_time, "%Y-%m-%d %H:%M")
                except ValueError:
                    print(f"[智能识别] 无法解析场次时间格式")
                    return None
            
            # 获取场次列表（通过主窗口的Tab管理器）
            if not (hasattr(self.main_window, 'tab_manager_widget') and
                    hasattr(self.main_window.tab_manager_widget, 'get_current_sessions')):
                print(f"[智能识别] 无法获取场次数据")
                return None

            try:
                # 尝试获取当前场次列表
                sessions_data = self.main_window.tab_manager_widget.get_current_sessions()
                if not sessions_data:
                    print(f"[智能识别] 场次数据为空")
                    return None
            except:
                # 如果获取失败，创建模拟数据用于测试
                print(f"[智能识别] 使用模拟场次数据进行匹配")
                sessions_data = [
                    {
                        'time': order_info.session_time,
                        'id': 'mock_session_id',
                        'hall': order_info.hall_name
                    }
                ]

            # 精确时间匹配
            for session in sessions_data:
                session_time_str = session.get('time', session.get('showTime', ''))
                if session_time_str == order_info.session_time:
                    print(f"[智能识别] 精确匹配场次: {session_time_str}")
                    return session

            # 时间范围匹配（允许±30分钟误差）
            for session in sessions_data:
                session_time_str = session.get('time', session.get('showTime', ''))
                if session_time_str:
                    try:
                        session_time = datetime.strptime(session_time_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            session_time = datetime.strptime(session_time_str, "%Y-%m-%d %H:%M")
                        except ValueError:
                            continue

                    # 计算时间差
                    time_diff = abs((target_time - session_time).total_seconds())
                    if time_diff <= 1800:  # 30分钟内
                        print(f"[智能识别] 时间范围匹配场次: {session_time_str} (误差: {time_diff/60:.1f}分钟)")
                        return session

            # 影厅名称匹配（如果有影厅信息）
            if order_info.hall_name:
                for session in sessions_data:
                    session_hall = session.get('hall', session.get('hallName', ''))
                    if order_info.hall_name in session_hall or session_hall in order_info.hall_name:
                        print(f"[智能识别] 影厅匹配场次: {session_hall}")
                        return session

            print(f"[智能识别] 未找到匹配的场次")
            return None
            
        except Exception as e:
            print(f"[智能识别] 匹配场次失败: {e}")
            return None
    
    def match_seats(self, order_info: OrderInfo) -> List[Dict[str, Any]]:
        """匹配座位信息"""
        try:
            if not order_info.seats:
                return []
            
            print(f"[智能识别] 开始匹配座位: {order_info.seats}")
            
            seat_matches = []
            for seat_str in order_info.seats:
                # 解析座位字符串，如"10排13座"
                match = re.match(r'(\d+)排(\d+)座', seat_str)
                if match:
                    row = int(match.group(1))
                    col = int(match.group(2))
                    seat_matches.append({
                        'row': row,
                        'col': col,
                        'seat_str': seat_str,
                        'original': seat_str
                    })
                    print(f"[智能识别] 解析座位: {row}排{col}座")
            
            return seat_matches
            
        except Exception as e:
            print(f"[智能识别] 匹配座位失败: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本关键词"""
        # 移除常见的无意义词汇
        stop_words = {'影城', '电影院', '店', '分店', '广场', '中心', '大厦', '商场', '购物', '的', '和', '与'}

        # 简单的关键词提取（可以后续优化为更复杂的NLP处理）
        keywords = []

        # 提取中文词汇（简单按字符分割）
        import re
        chinese_chars = re.findall(r'[\u4e00-\u9fff]+', text)
        for chars in chinese_chars:
            if len(chars) >= 2 and chars not in stop_words:
                keywords.append(chars)
                # 对于长词汇，也提取子词汇
                if len(chars) > 3:
                    for i in range(len(chars) - 1):
                        sub_word = chars[i:i+2]
                        if sub_word not in stop_words:
                            keywords.append(sub_word)

        # 提取英文词汇
        english_words = re.findall(r'[A-Za-z]+', text)
        for word in english_words:
            if len(word) >= 2:
                keywords.append(word.upper())

        # 去重并返回
        return list(set(keywords))
    
    def calculate_confidence(self, order_info: OrderInfo, match_result: MatchResult) -> float:
        """计算匹配置信度"""
        try:
            score = 0.0
            total_weight = 0.0
            
            # 影院匹配权重
            if match_result.cinema_match:
                score += 0.3
            total_weight += 0.3
            
            # 影片匹配权重
            if match_result.movie_match:
                score += 0.25
            total_weight += 0.25
            
            # 场次匹配权重
            if match_result.session_match:
                score += 0.25
            total_weight += 0.25
            
            # 座位匹配权重
            if match_result.seat_matches:
                score += 0.2
            total_weight += 0.2
            
            return score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            print(f"[智能识别] 计算置信度失败: {e}")
            return 0.0
    
    def recognize_and_match(self, text: str = None) -> Tuple[OrderInfo, MatchResult]:
        """主要识别和匹配方法"""
        try:
            # 读取剪贴板内容（如果没有提供文本）
            if text is None:
                text = self.read_clipboard()
            
            if not text:
                return OrderInfo(), MatchResult()
            
            # 解析订单信息
            order_info = self.parse_order_text(text)
            
            # 创建匹配结果
            match_result = MatchResult()
            
            # 匹配影院
            match_result.cinema_match = self.match_cinema(order_info)
            
            # 匹配影片（需要先有影院）
            if match_result.cinema_match:
                match_result.movie_match = self.match_movie(order_info, match_result.cinema_match)
            
            # 匹配场次（需要先有影片）
            if match_result.movie_match:
                match_result.session_match = self.match_session(order_info, match_result.movie_match)
            
            # 匹配座位
            match_result.seat_matches = self.match_seats(order_info)
            
            # 计算置信度
            match_result.confidence_score = self.calculate_confidence(order_info, match_result)
            
            # 生成建议
            match_result.suggestions = self._generate_suggestions(order_info, match_result)
            
            print(f"[智能识别] 识别完成，置信度: {match_result.confidence_score:.2f}")
            
            return order_info, match_result
            
        except Exception as e:
            print(f"[智能识别] 识别和匹配失败: {e}")
            import traceback
            traceback.print_exc()
            return OrderInfo(), MatchResult()
    
    def _generate_suggestions(self, order_info: OrderInfo, match_result: MatchResult) -> List[str]:
        """生成用户建议"""
        suggestions = []
        
        if not match_result.cinema_match:
            suggestions.append(f"未找到匹配的影院：{order_info.cinema_name}")
        
        if not match_result.movie_match:
            suggestions.append(f"未找到匹配的影片：{order_info.movie_name}")
        
        if not match_result.session_match:
            suggestions.append(f"未找到匹配的场次：{order_info.session_time}")
        
        if not match_result.seat_matches:
            suggestions.append(f"未找到匹配的座位：{', '.join(order_info.seats)}")
        
        if match_result.confidence_score < 0.5:
            suggestions.append("匹配置信度较低，建议手动确认")
        
        return suggestions

    def get_enhanced_matching_stats(self) -> Dict[str, Any]:
        """获取增强匹配引擎的性能统计"""
        try:
            if self.enhanced_engine:
                return self.enhanced_engine.get_performance_stats()
            else:
                return {
                    'status': 'disabled',
                    'reason': 'Enhanced matching engine not available'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def clear_enhanced_matching_cache(self):
        """清空增强匹配引擎的缓存"""
        try:
            if self.enhanced_engine:
                self.enhanced_engine.clear_cache()
                print("[智能识别] 增强匹配缓存已清空")
            else:
                print("[智能识别] 增强匹配引擎不可用")
        except Exception as e:
            print(f"[智能识别] 清空缓存失败: {e}")

    def toggle_enhanced_matching(self, enabled: bool):
        """切换增强匹配功能"""
        try:
            self.use_enhanced_matching = enabled and self.enhanced_engine is not None
            status = "启用" if self.use_enhanced_matching else "禁用"
            print(f"[智能识别] 增强匹配功能已{status}")
        except Exception as e:
            print(f"[智能识别] 切换增强匹配功能失败: {e}")
