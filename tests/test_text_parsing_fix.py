"""
智能订单识别文本解析修复验证测试

专门测试修复后的文本解析规则，验证边界处理问题的解决效果
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.smart_recognition import SmartOrderRecognition, OrderInfo


class TestTextParsingFix(unittest.TestCase):
    """文本解析修复验证测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.recognition = SmartOrderRecognition()
    
    def test_original_problem_text(self):
        """测试原始问题文本 - 用户报告的具体问题"""
        print("\n=== 测试原始问题文本 ===")
        
        # 用户报告的问题文本
        problem_text = "订单：2025060712563719961 城市：福州 影院：华夏 地址：台江区工业路233号苏宁广场C区三楼 苏宁影城 影片：侦探 场次：2025-06-08 23:35:00 影厅：2号CGS中国巨幕厅（儿童需购票） 座位：10排13座 10排12座 市价：51.90"
        
        order_info = self.recognition.parse_order_text(problem_text)
        
        print(f"解析结果:")
        print(f"  订单号: '{order_info.order_id}'")
        print(f"  城市: '{order_info.city}'")
        print(f"  影院: '{order_info.cinema_name}'")
        print(f"  地址: '{order_info.cinema_address}'")
        print(f"  影片: '{order_info.movie_name}'")
        print(f"  场次: '{order_info.session_time}'")
        print(f"  影厅: '{order_info.hall_name}'")
        print(f"  座位: {order_info.seats}")
        print(f"  价格: {order_info.price}")
        
        # 关键验证：影院名称应该只是"华夏"，不是"华夏地址"
        self.assertEqual(order_info.cinema_name, "华夏", "影院名称应该只包含'华夏'")
        self.assertNotEqual(order_info.cinema_name, "华夏地址", "影院名称不应该包含'地址'")
        
        # 验证其他字段
        self.assertEqual(order_info.order_id, "2025060712563719961")
        self.assertEqual(order_info.city, "福州")
        self.assertEqual(order_info.cinema_address, "台江区工业路233号苏宁广场C区三楼 苏宁影城")
        self.assertEqual(order_info.movie_name, "侦探")
        self.assertEqual(order_info.session_time, "2025-06-08 23:35:00")
        self.assertEqual(order_info.hall_name, "2号CGS中国巨幕厅（儿童需购票）")
        self.assertEqual(len(order_info.seats), 2)
        self.assertIn("10排13座", order_info.seats)
        self.assertIn("10排12座", order_info.seats)
        self.assertEqual(order_info.price, 51.90)
        
        print("✅ 原始问题文本解析修复成功！")
    
    def test_boundary_handling_variations(self):
        """测试各种边界处理变化"""
        print("\n=== 测试边界处理变化 ===")
        
        # 测试1：紧密连接的字段
        text1 = "订单：123456城市：北京影院：万达影片：阿凡达场次：2025-06-08 20:00:00座位：5排6座市价：45.00"
        order_info1 = self.recognition.parse_order_text(text1)
        
        self.assertEqual(order_info1.order_id, "123456")
        self.assertEqual(order_info1.city, "北京")
        self.assertEqual(order_info1.cinema_name, "万达")
        self.assertEqual(order_info1.movie_name, "阿凡达")
        print("✅ 紧密连接字段解析成功")
        
        # 测试2：带空格的字段
        text2 = "订单：123456 城市：上海 影院：CGV影城 影片：速度与激情 场次：2025-06-08 21:00:00 座位：8排9座 市价：55.00"
        order_info2 = self.recognition.parse_order_text(text2)
        
        self.assertEqual(order_info2.order_id, "123456")
        self.assertEqual(order_info2.city, "上海")
        self.assertEqual(order_info2.cinema_name, "CGV影城")
        self.assertEqual(order_info2.movie_name, "速度与激情")
        print("✅ 带空格字段解析成功")
        
        # 测试3：包含特殊字符的影片名
        text3 = "订单：123456 影院：华夏 影片：碟中谍8：最终清算 场次：2025-06-08 22:00:00"
        order_info3 = self.recognition.parse_order_text(text3)
        
        self.assertEqual(order_info3.cinema_name, "华夏")
        self.assertEqual(order_info3.movie_name, "碟中谍8：最终清算")
        print("✅ 包含冒号的影片名解析成功")
        
        # 测试4：逗号分隔的格式
        text4 = "订单：123456，城市：深圳，影院：万达影城，影片：阿凡达2，场次：2025-06-08 19:30:00，座位：6排7座"
        order_info4 = self.recognition.parse_order_text(text4)
        
        self.assertEqual(order_info4.order_id, "123456")
        self.assertEqual(order_info4.city, "深圳")
        self.assertEqual(order_info4.cinema_name, "万达影城")
        self.assertEqual(order_info4.movie_name, "阿凡达2")
        print("✅ 逗号分隔格式解析成功")
    
    def test_field_boundary_edge_cases(self):
        """测试字段边界的边缘情况"""
        print("\n=== 测试字段边界边缘情况 ===")
        
        # 测试1：影院名称后直接跟地址
        text1 = "影院：华夏地址：某某路123号影片：测试影片"
        order_info1 = self.recognition.parse_order_text(text1)
        
        self.assertEqual(order_info1.cinema_name, "华夏")
        self.assertEqual(order_info1.cinema_address, "某某路123号")
        self.assertEqual(order_info1.movie_name, "测试影片")
        print("✅ 影院名称后直接跟地址解析成功")
        
        # 测试2：字段顺序不同
        text2 = "影片：测试影片影院：万达城市：北京订单：123456"
        order_info2 = self.recognition.parse_order_text(text2)
        
        self.assertEqual(order_info2.movie_name, "测试影片")
        self.assertEqual(order_info2.cinema_name, "万达")
        self.assertEqual(order_info2.city, "北京")
        self.assertEqual(order_info2.order_id, "123456")
        print("✅ 不同字段顺序解析成功")
        
        # 测试3：缺少某些字段
        text3 = "订单：123456影院：华夏影片：测试影片"
        order_info3 = self.recognition.parse_order_text(text3)
        
        self.assertEqual(order_info3.order_id, "123456")
        self.assertEqual(order_info3.cinema_name, "华夏")
        self.assertEqual(order_info3.movie_name, "测试影片")
        self.assertEqual(order_info3.city, "")  # 缺少的字段应该为空
        print("✅ 缺少字段的情况解析成功")
    
    def test_compatibility_with_standard_format(self):
        """测试与标准格式的兼容性"""
        print("\n=== 测试标准格式兼容性 ===")
        
        # 标准换行格式
        standard_text = """
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
        
        order_info = self.recognition.parse_order_text(standard_text)
        
        # 验证所有字段都能正确解析
        self.assertEqual(order_info.order_id, "2025060712563719961")
        self.assertEqual(order_info.city, "福州")
        self.assertEqual(order_info.cinema_name, "苏宁影城（CGS中国巨幕店）")
        self.assertEqual(order_info.cinema_address, "台江区工业路233号苏宁广场C区三楼 苏宁影城")
        self.assertEqual(order_info.movie_name, "碟中谍8：最终清算")
        self.assertEqual(order_info.session_time, "2025-06-07 19:10:00")
        self.assertEqual(order_info.hall_name, "2号CGS中国巨幕厅（儿童需购票）")
        self.assertEqual(len(order_info.seats), 2)
        self.assertEqual(order_info.price, 51.90)
        
        print("✅ 标准换行格式兼容性验证成功")
    
    def test_regex_pattern_validation(self):
        """测试正则表达式模式验证"""
        print("\n=== 测试正则表达式模式验证 ===")
        
        patterns = self.recognition.order_patterns
        
        # 验证关键模式存在
        required_patterns = [
            'order_id', 'city', 'cinema_name', 'cinema_address',
            'movie_name', 'session_time', 'hall_name', 'seats', 'price'
        ]
        
        for pattern_name in required_patterns:
            self.assertIn(pattern_name, patterns, f"缺少必需的模式: {pattern_name}")
        
        print("✅ 正则表达式模式验证成功")
        
        # 验证模式能正确匹配
        test_cases = [
            ('order_id', '订单：123456', '123456'),
            ('city', '城市：北京', '北京'),
            ('cinema_name', '影院：万达', '万达'),
            ('movie_name', '影片：阿凡达', '阿凡达'),
            ('price', '市价：45.50', '45.50'),
        ]
        
        import re
        for pattern_name, test_text, expected in test_cases:
            pattern = patterns[pattern_name]
            match = re.search(pattern, test_text)
            self.assertIsNotNone(match, f"模式 {pattern_name} 无法匹配文本: {test_text}")
            self.assertEqual(match.group(1), expected, f"模式 {pattern_name} 匹配结果不正确")
        
        print("✅ 正则表达式匹配验证成功")


def run_fix_validation_tests():
    """运行修复验证测试"""
    print("🔧 智能订单识别文本解析修复验证测试开始")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestTextParsingFix))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 所有修复验证测试通过！文本解析问题已完全解决。")
        print("✅ 影院名称边界处理问题已修复")
        print("✅ 字段边界识别问题已修复")
        print("✅ 与标准格式的兼容性保持良好")
    else:
        print("❌ 部分修复验证测试失败，需要进一步检查。")
        print(f"失败数量: {len(result.failures)}")
        print(f"错误数量: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_fix_validation_tests()
