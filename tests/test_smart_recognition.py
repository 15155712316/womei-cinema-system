"""
智能订单识别功能测试

测试智能识别功能的各个组件：
1. 文本解析功能
2. 影院匹配功能
3. 影片匹配功能
4. 场次匹配功能
5. 座位匹配功能
6. 整体识别流程
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.smart_recognition import SmartOrderRecognition, OrderInfo, MatchResult


class TestSmartRecognition(unittest.TestCase):
    """智能识别测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.recognition = SmartOrderRecognition()
        
        # 测试用的订单文本
        self.test_order_text = """
订单：2025060712563719961
城市：福州
影院：苏宁影城（CGS中国巨幕店）
地址：台江区工业路233号苏宁广场C区三楼 苏宁影城
影片：碟中谍8：最终清算
场次：2025-06-07 19:10:00
影厅：2号CGS中国巨幕厅（儿童需购票）
座位：10排13座 10排12座
市价：51.90
"""
    
    def test_parse_order_text(self):
        """测试订单文本解析"""
        print("\n=== 测试订单文本解析 ===")
        
        order_info = self.recognition.parse_order_text(self.test_order_text)
        
        # 验证解析结果
        self.assertEqual(order_info.order_id, "2025060712563719961")
        self.assertEqual(order_info.city, "福州")
        self.assertEqual(order_info.cinema_name, "苏宁影城（CGS中国巨幕店）")
        self.assertEqual(order_info.movie_name, "碟中谍8：最终清算")
        self.assertEqual(order_info.session_time, "2025-06-07 19:10:00")
        self.assertEqual(order_info.hall_name, "2号CGS中国巨幕厅（儿童需购票）")
        self.assertEqual(len(order_info.seats), 2)
        self.assertIn("10排13座", order_info.seats)
        self.assertIn("10排12座", order_info.seats)
        self.assertEqual(order_info.price, 51.90)
        
        print(f"✅ 订单号: {order_info.order_id}")
        print(f"✅ 城市: {order_info.city}")
        print(f"✅ 影院: {order_info.cinema_name}")
        print(f"✅ 影片: {order_info.movie_name}")
        print(f"✅ 场次: {order_info.session_time}")
        print(f"✅ 影厅: {order_info.hall_name}")
        print(f"✅ 座位: {order_info.seats}")
        print(f"✅ 价格: {order_info.price}")
    
    def test_extract_keywords(self):
        """测试关键词提取"""
        print("\n=== 测试关键词提取 ===")
        
        # 测试影院名称关键词提取
        cinema_keywords = self.recognition._extract_keywords("苏宁影城（CGS中国巨幕店）")
        print(f"影院关键词: {cinema_keywords}")
        self.assertIn("苏宁", cinema_keywords)
        self.assertIn("CGS", cinema_keywords)
        
        # 测试影片名称关键词提取
        movie_keywords = self.recognition._extract_keywords("碟中谍8：最终清算")
        print(f"影片关键词: {movie_keywords}")
        self.assertIn("碟中谍", movie_keywords)
        self.assertIn("最终清算", movie_keywords)
    
    def test_match_seats(self):
        """测试座位匹配"""
        print("\n=== 测试座位匹配 ===")
        
        order_info = OrderInfo()
        order_info.seats = ["10排13座", "10排12座", "5排8座"]
        
        seat_matches = self.recognition.match_seats(order_info)
        
        self.assertEqual(len(seat_matches), 3)
        
        # 验证第一个座位
        seat1 = seat_matches[0]
        self.assertEqual(seat1['row'], 10)
        self.assertEqual(seat1['col'], 13)
        self.assertEqual(seat1['seat_str'], "10排13座")
        
        # 验证第二个座位
        seat2 = seat_matches[1]
        self.assertEqual(seat2['row'], 10)
        self.assertEqual(seat2['col'], 12)
        
        # 验证第三个座位
        seat3 = seat_matches[2]
        self.assertEqual(seat3['row'], 5)
        self.assertEqual(seat3['col'], 8)
        
        print(f"✅ 座位匹配成功: {len(seat_matches)}个座位")
        for seat in seat_matches:
            print(f"   - {seat['row']}排{seat['col']}座")
    
    def test_calculate_confidence(self):
        """测试置信度计算"""
        print("\n=== 测试置信度计算 ===")
        
        order_info = OrderInfo()
        
        # 测试完全匹配的情况
        match_result = MatchResult()
        match_result.cinema_match = {"name": "test_cinema"}
        match_result.movie_match = {"name": "test_movie"}
        match_result.session_match = {"time": "test_time"}
        match_result.seat_matches = [{"row": 1, "col": 1}]
        
        confidence = self.recognition.calculate_confidence(order_info, match_result)
        self.assertEqual(confidence, 1.0)
        print(f"✅ 完全匹配置信度: {confidence:.2f}")
        
        # 测试部分匹配的情况
        match_result2 = MatchResult()
        match_result2.cinema_match = {"name": "test_cinema"}
        match_result2.movie_match = None
        match_result2.session_match = None
        match_result2.seat_matches = []
        
        confidence2 = self.recognition.calculate_confidence(order_info, match_result2)
        self.assertEqual(confidence2, 0.3)
        print(f"✅ 部分匹配置信度: {confidence2:.2f}")
    
    def test_generate_suggestions(self):
        """测试建议生成"""
        print("\n=== 测试建议生成 ===")
        
        order_info = OrderInfo()
        order_info.cinema_name = "测试影院"
        order_info.movie_name = "测试影片"
        order_info.session_time = "2025-06-07 19:10:00"
        order_info.seats = ["10排13座"]
        
        # 测试无匹配的情况
        match_result = MatchResult()
        match_result.confidence_score = 0.2
        
        suggestions = self.recognition._generate_suggestions(order_info, match_result)
        
        self.assertGreater(len(suggestions), 0)
        print(f"✅ 生成建议数量: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    
    def test_different_text_formats(self):
        """测试不同的文本格式"""
        print("\n=== 测试不同文本格式 ===")

        # 测试简化格式
        simple_text = """
订单号: 2025060712563719961
影院: 万达影城
影片: 阿凡达3
时间: 2025-06-07 20:30
座位: 8排5座 8排6座
"""

        order_info = self.recognition.parse_order_text(simple_text)
        self.assertEqual(order_info.order_id, "2025060712563719961")
        self.assertEqual(order_info.cinema_name, "万达影城")
        self.assertEqual(order_info.movie_name, "阿凡达3")
        print(f"✅ 简化格式解析成功")

        # 测试不规范格式
        irregular_text = """
订单：2025060712563719961，城市：北京，影院：CGV影城（朝阳大悦城店），影片：速度与激情11，场次：2025-06-08 14:30:00，座位：6排10座
"""

        order_info2 = self.recognition.parse_order_text(irregular_text)
        self.assertEqual(order_info2.order_id, "2025060712563719961")
        self.assertEqual(order_info2.city, "北京")
        print(f"✅ 不规范格式解析成功")

    def test_problematic_text_format(self):
        """测试问题文本格式 - 连续文本中的字段边界处理"""
        print("\n=== 测试问题文本格式 ===")

        # 测试用户提供的问题文本
        problematic_text = "订单：2025060712563719961 城市：福州 影院：华夏 地址：台江区工业路233号苏宁广场C区三楼 苏宁影城 影片：侦探 场次：2025-06-08 23:35:00 影厅：2号CGS中国巨幕厅（儿童需购票） 座位：10排13座 10排12座 市价：51.90"

        order_info = self.recognition.parse_order_text(problematic_text)

        # 验证解析结果
        print(f"订单号: {order_info.order_id}")
        print(f"城市: {order_info.city}")
        print(f"影院: {order_info.cinema_name}")
        print(f"地址: {order_info.cinema_address}")
        print(f"影片: {order_info.movie_name}")
        print(f"场次: {order_info.session_time}")
        print(f"影厅: {order_info.hall_name}")
        print(f"座位: {order_info.seats}")
        print(f"价格: {order_info.price}")

        # 关键验证：影院名称应该只是"华夏"，不包含"地址"
        self.assertEqual(order_info.order_id, "2025060712563719961")
        self.assertEqual(order_info.city, "福州")
        self.assertEqual(order_info.cinema_name, "华夏")  # 关键测试点
        self.assertEqual(order_info.cinema_address, "台江区工业路233号苏宁广场C区三楼 苏宁影城")
        self.assertEqual(order_info.movie_name, "侦探")
        self.assertEqual(order_info.session_time, "2025-06-08 23:35:00")
        self.assertEqual(order_info.hall_name, "2号CGS中国巨幕厅（儿童需购票）")
        self.assertEqual(len(order_info.seats), 2)
        self.assertIn("10排13座", order_info.seats)
        self.assertIn("10排12座", order_info.seats)
        self.assertEqual(order_info.price, 51.90)

        print(f"✅ 问题文本格式解析成功")
        print(f"✅ 影院名称正确识别为: '{order_info.cinema_name}'")
        print(f"✅ 地址信息正确识别为: '{order_info.cinema_address}'")


class TestOrderInfoDataClass(unittest.TestCase):
    """测试OrderInfo数据类"""
    
    def test_order_info_creation(self):
        """测试OrderInfo创建"""
        print("\n=== 测试OrderInfo数据类 ===")
        
        # 测试默认创建
        order_info = OrderInfo()
        self.assertEqual(order_info.order_id, "")
        self.assertEqual(order_info.seats, [])
        print(f"✅ 默认创建成功")
        
        # 测试带参数创建
        order_info2 = OrderInfo(
            order_id="123456",
            cinema_name="测试影院",
            movie_name="测试影片",
            seats=["1排1座", "1排2座"]
        )
        self.assertEqual(order_info2.order_id, "123456")
        self.assertEqual(order_info2.cinema_name, "测试影院")
        self.assertEqual(len(order_info2.seats), 2)
        print(f"✅ 带参数创建成功")


class TestMatchResultDataClass(unittest.TestCase):
    """测试MatchResult数据类"""
    
    def test_match_result_creation(self):
        """测试MatchResult创建"""
        print("\n=== 测试MatchResult数据类 ===")
        
        # 测试默认创建
        match_result = MatchResult()
        self.assertIsNone(match_result.cinema_match)
        self.assertEqual(match_result.seat_matches, [])
        self.assertEqual(match_result.suggestions, [])
        self.assertEqual(match_result.confidence_score, 0.0)
        print(f"✅ 默认创建成功")
        
        # 测试带参数创建
        match_result2 = MatchResult(
            cinema_match={"name": "test"},
            confidence_score=0.8,
            suggestions=["建议1", "建议2"]
        )
        self.assertIsNotNone(match_result2.cinema_match)
        self.assertEqual(match_result2.confidence_score, 0.8)
        self.assertEqual(len(match_result2.suggestions), 2)
        print(f"✅ 带参数创建成功")


def run_tests():
    """运行所有测试"""
    print("🤖 智能订单识别功能测试开始")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestSmartRecognition))
    test_suite.addTest(unittest.makeSuite(TestOrderInfoDataClass))
    test_suite.addTest(unittest.makeSuite(TestMatchResultDataClass))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 所有测试通过！智能识别功能正常工作。")
    else:
        print("❌ 部分测试失败，请检查代码。")
        print(f"失败数量: {len(result.failures)}")
        print(f"错误数量: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
