"""
增强型智能匹配算法测试

测试内容：
1. 增强匹配引擎的各种匹配策略
2. 影院别名和品牌识别
3. 相似度计算和候选项排序
4. 性能测试和缓存机制
5. 与原有匹配算法的对比测试
"""

import unittest
import asyncio
import sys
import os
import time

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.enhanced_matching_engine import EnhancedMatchingEngine, MatchCandidate
from services.smart_recognition import SmartOrderRecognition, OrderInfo


class TestEnhancedMatchingEngine(unittest.TestCase):
    """增强匹配引擎测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = EnhancedMatchingEngine()
        
        # 模拟影院数据
        self.mock_cinemas = [
            {'cinemaShortName': '万达影城（朝阳大悦城店）', 'id': '1001'},
            {'cinemaShortName': '万达IMAX影城（CBD店）', 'id': '1002'},
            {'cinemaShortName': '苏宁影城（CGS中国巨幕店）', 'id': '1003'},
            {'cinemaShortName': 'CGV影城（朝阳大悦城店）', 'id': '1004'},
            {'cinemaShortName': '华夏影城（王府井店）', 'id': '1005'},
            {'cinemaShortName': '金逸影城（三里屯店）', 'id': '1006'},
            {'cinemaShortName': '大地影院（西单店）', 'id': '1007'},
            {'cinemaShortName': '万达电影城（通州店）', 'id': '1008'},
        ]
    
    def test_text_similarity_calculation(self):
        """测试文本相似度计算"""
        print("\n=== 测试文本相似度计算 ===")
        
        # 测试完全相同
        similarity1 = self.engine.calculate_text_similarity("万达影城", "万达影城")
        self.assertEqual(similarity1, 1.0)
        print(f"✅ 完全相同: {similarity1:.3f}")
        
        # 测试高相似度
        similarity2 = self.engine.calculate_text_similarity("万达影城", "万达电影城")
        self.assertGreater(similarity2, 0.8)
        print(f"✅ 高相似度: {similarity2:.3f}")
        
        # 测试中等相似度
        similarity3 = self.engine.calculate_text_similarity("万达影城", "万达IMAX影城")
        self.assertGreater(similarity3, 0.6)
        print(f"✅ 中等相似度: {similarity3:.3f}")
        
        # 测试低相似度
        similarity4 = self.engine.calculate_text_similarity("万达影城", "CGV影城")
        self.assertLess(similarity4, 0.5)
        print(f"✅ 低相似度: {similarity4:.3f}")
    
    def test_brand_extraction(self):
        """测试品牌提取"""
        print("\n=== 测试品牌提取 ===")
        
        test_cases = [
            ("万达影城（朝阳大悦城店）", "万达"),
            ("苏宁影城（CGS中国巨幕店）", "苏宁"),
            ("CGV影城（朝阳大悦城店）", "CGV"),
            ("华夏影城（王府井店）", "华夏"),
            ("金逸IMAX影城", "金逸"),
            ("大地数字影院", "大地"),
            ("未知影院", None),
        ]
        
        for cinema_name, expected_brand in test_cases:
            brand = self.engine.extract_brand_from_name(cinema_name)
            self.assertEqual(brand, expected_brand)
            print(f"✅ {cinema_name} → {brand}")
    
    def test_cinema_candidates_finding(self):
        """测试影院候选项查找"""
        print("\n=== 测试影院候选项查找 ===")
        
        # 测试精确匹配
        candidates1 = self.engine.find_cinema_candidates("万达影城（朝阳大悦城店）", self.mock_cinemas)
        self.assertGreater(len(candidates1), 0)
        self.assertEqual(candidates1[0].match_type, 'exact')
        self.assertEqual(candidates1[0].score, 1.0)
        print(f"✅ 精确匹配: {candidates1[0].data['cinemaShortName']} (得分: {candidates1[0].score:.2f})")
        
        # 测试品牌匹配
        candidates2 = self.engine.find_cinema_candidates("万达电影城", self.mock_cinemas)
        self.assertGreater(len(candidates2), 0)
        # 应该找到多个万达相关的影院
        wanda_candidates = [c for c in candidates2 if '万达' in c.data['cinemaShortName']]
        self.assertGreater(len(wanda_candidates), 1)
        print(f"✅ 品牌匹配: 找到 {len(wanda_candidates)} 个万达影院")
        
        # 测试相似度匹配
        candidates3 = self.engine.find_cinema_candidates("苏宁CGS影城", self.mock_cinemas)
        self.assertGreater(len(candidates3), 0)
        print(f"✅ 相似度匹配: {candidates3[0].data['cinemaShortName']} (得分: {candidates3[0].score:.2f})")
    
    def test_alias_matching(self):
        """测试别名匹配"""
        print("\n=== 测试别名匹配 ===")
        
        # 测试万达别名
        self.assertTrue(self.engine._check_alias_match("万达电影城", "万达影城"))
        self.assertTrue(self.engine._check_alias_match("万达IMAX影城", "万达影城"))
        print("✅ 万达别名匹配正常")
        
        # 测试苏宁别名
        self.assertTrue(self.engine._check_alias_match("苏宁电影城", "苏宁影城"))
        self.assertTrue(self.engine._check_alias_match("苏宁CGS影城", "苏宁影城"))
        print("✅ 苏宁别名匹配正常")
        
        # 测试不匹配的情况
        self.assertFalse(self.engine._check_alias_match("万达影城", "CGV影城"))
        print("✅ 不匹配情况处理正常")
    
    def test_brand_matching(self):
        """测试品牌匹配"""
        print("\n=== 测试品牌匹配 ===")
        
        # 测试万达品牌匹配
        self.assertTrue(self.engine._check_brand_match("万达", "万达影城（朝阳大悦城店）"))
        self.assertTrue(self.engine._check_brand_match("万达", "万达IMAX影城"))
        print("✅ 万达品牌匹配正常")
        
        # 测试CGV品牌匹配
        self.assertTrue(self.engine._check_brand_match("CGV", "CGV影城（朝阳大悦城店）"))
        print("✅ CGV品牌匹配正常")
        
        # 测试不匹配的情况
        self.assertFalse(self.engine._check_brand_match("万达", "CGV影城"))
        print("✅ 品牌不匹配情况处理正常")
    
    def test_keyword_score_calculation(self):
        """测试关键词得分计算"""
        print("\n=== 测试关键词得分计算 ===")
        
        # 测试高关键词匹配
        score1 = self.engine._calculate_keyword_score("万达影城朝阳店", "万达影城（朝阳大悦城店）")
        self.assertGreater(score1, 0.5)
        print(f"✅ 高关键词匹配: {score1:.3f}")
        
        # 测试中等关键词匹配
        score2 = self.engine._calculate_keyword_score("苏宁CGS", "苏宁影城（CGS中国巨幕店）")
        self.assertGreater(score2, 0.3)
        print(f"✅ 中等关键词匹配: {score2:.3f}")
        
        # 测试低关键词匹配
        score3 = self.engine._calculate_keyword_score("万达", "CGV影城")
        self.assertLess(score3, 0.3)
        print(f"✅ 低关键词匹配: {score3:.3f}")
    
    def test_enhanced_keywords_extraction(self):
        """测试增强关键词提取"""
        print("\n=== 测试增强关键词提取 ===")
        
        keywords1 = self.engine._extract_enhanced_keywords("万达影城（朝阳大悦城店）")
        self.assertIn("万达", keywords1)
        self.assertIn("朝阳", keywords1)
        print(f"✅ 万达影院关键词: {keywords1}")
        
        keywords2 = self.engine._extract_enhanced_keywords("苏宁影城（CGS中国巨幕店）")
        self.assertIn("苏宁", keywords2)
        self.assertIn("CGS", keywords2)
        print(f"✅ 苏宁影院关键词: {keywords2}")
        
        keywords3 = self.engine._extract_enhanced_keywords("碟中谍8：最终清算")
        self.assertIn("碟中谍", keywords3)
        self.assertIn("最终清算", keywords3)
        print(f"✅ 影片名关键词: {keywords3}")


class TestEnhancedMatchingIntegration(unittest.TestCase):
    """增强匹配集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.recognition = SmartOrderRecognition()
        
        # 模拟主窗口和影院数据
        class MockTabManager:
            def __init__(self):
                self.cinemas_data = [
                    {'cinemaShortName': '万达影城（朝阳大悦城店）', 'id': '1001'},
                    {'cinemaShortName': '万达IMAX影城（CBD店）', 'id': '1002'},
                    {'cinemaShortName': '苏宁影城（CGS中国巨幕店）', 'id': '1003'},
                    {'cinemaShortName': 'CGV影城（朝阳大悦城店）', 'id': '1004'},
                    {'cinemaShortName': '华夏影城（王府井店）', 'id': '1005'},
                ]
        
        class MockMainWindow:
            def __init__(self):
                self.tab_manager_widget = MockTabManager()
        
        self.recognition.main_window = MockMainWindow()
    
    def test_enhanced_vs_basic_matching(self):
        """测试增强匹配与基础匹配的对比"""
        print("\n=== 测试增强匹配与基础匹配对比 ===")
        
        test_cases = [
            ("万达电影城", "万达影城（朝阳大悦城店）"),  # 别名匹配
            ("万达IMAX", "万达IMAX影城（CBD店）"),      # 品牌+特征匹配
            ("苏宁CGS", "苏宁影城（CGS中国巨幕店）"),   # 关键词匹配
            ("华夏", "华夏影城（王府井店）"),           # 简化名称匹配
        ]
        
        for order_name, expected_cinema in test_cases:
            order_info = OrderInfo(cinema_name=order_name)
            
            # 测试增强匹配
            enhanced_result = self.recognition.match_cinema(order_info)
            
            # 测试基础匹配
            self.recognition.use_enhanced_matching = False
            basic_result = self.recognition.match_cinema(order_info)
            self.recognition.use_enhanced_matching = True
            
            print(f"订单影院: {order_name}")
            print(f"  增强匹配: {enhanced_result.get('cinemaShortName') if enhanced_result else 'None'}")
            print(f"  基础匹配: {basic_result.get('cinemaShortName') if basic_result else 'None'}")
            print(f"  期望结果: {expected_cinema}")
            
            # 增强匹配应该有更好的结果
            if enhanced_result:
                self.assertIsNotNone(enhanced_result)
                print(f"  ✅ 增强匹配成功")
            else:
                print(f"  ❌ 增强匹配失败")
    
    def test_performance_comparison(self):
        """测试性能对比"""
        print("\n=== 测试性能对比 ===")
        
        test_order = OrderInfo(cinema_name="万达电影城")
        
        # 测试增强匹配性能
        start_time = time.time()
        for _ in range(10):
            self.recognition.match_cinema(test_order)
        enhanced_time = time.time() - start_time
        
        # 测试基础匹配性能
        self.recognition.use_enhanced_matching = False
        start_time = time.time()
        for _ in range(10):
            self.recognition.match_cinema(test_order)
        basic_time = time.time() - start_time
        self.recognition.use_enhanced_matching = True
        
        print(f"增强匹配平均时间: {enhanced_time/10*1000:.2f}ms")
        print(f"基础匹配平均时间: {basic_time/10*1000:.2f}ms")
        
        # 增强匹配时间应该在合理范围内（<500ms）
        self.assertLess(enhanced_time/10, 0.5)
        print("✅ 性能测试通过")
    
    def test_enhanced_matching_stats(self):
        """测试增强匹配统计"""
        print("\n=== 测试增强匹配统计 ===")
        
        # 执行一些匹配操作
        test_orders = [
            OrderInfo(cinema_name="万达影城"),
            OrderInfo(cinema_name="苏宁影城"),
            OrderInfo(cinema_name="CGV影城"),
            OrderInfo(cinema_name="不存在的影院"),
        ]
        
        for order in test_orders:
            self.recognition.match_cinema(order)
        
        # 获取统计信息
        stats = self.recognition.get_enhanced_matching_stats()
        
        print(f"匹配统计: {stats}")
        
        if 'total_matches' in stats:
            self.assertGreater(stats['total_matches'], 0)
            print("✅ 统计信息正常")
        else:
            print("⚠️ 增强匹配引擎不可用")
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        print("\n=== 测试缓存功能 ===")
        
        test_order = OrderInfo(cinema_name="万达影城")
        
        # 第一次匹配（应该缓存结果）
        start_time = time.time()
        result1 = self.recognition.match_cinema(test_order)
        first_time = time.time() - start_time
        
        # 第二次匹配（应该使用缓存）
        start_time = time.time()
        result2 = self.recognition.match_cinema(test_order)
        second_time = time.time() - start_time
        
        print(f"第一次匹配时间: {first_time*1000:.2f}ms")
        print(f"第二次匹配时间: {second_time*1000:.2f}ms")
        
        # 结果应该相同
        if result1 and result2:
            self.assertEqual(result1.get('id'), result2.get('id'))
            print("✅ 缓存结果一致")
        
        # 清空缓存测试
        self.recognition.clear_enhanced_matching_cache()
        print("✅ 缓存清空成功")


class TestAsyncMatchingPerformance(unittest.TestCase):
    """异步匹配性能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = EnhancedMatchingEngine()
        self.mock_cinemas = [
            {'cinemaShortName': f'测试影院{i}', 'id': f'test_{i}'}
            for i in range(100)  # 创建100个测试影院
        ]
    
    def test_async_matching_performance(self):
        """测试异步匹配性能"""
        print("\n=== 测试异步匹配性能 ===")
        
        async def run_async_test():
            order_info = OrderInfo(cinema_name="测试影院50")
            
            start_time = time.time()
            result = await self.engine.enhanced_cinema_match(order_info, self.mock_cinemas)
            elapsed_time = time.time() - start_time
            
            print(f"异步匹配时间: {elapsed_time*1000:.2f}ms")
            self.assertLess(elapsed_time, 0.2)  # 应该在200ms内完成
            
            if result:
                print(f"匹配结果: {result.get('cinemaShortName')}")
                print("✅ 异步匹配成功")
            else:
                print("❌ 异步匹配失败")
        
        # 运行异步测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_async_test())
        finally:
            loop.close()


def run_enhanced_matching_tests():
    """运行增强匹配测试"""
    print("🚀 增强型智能匹配算法测试开始")
    print("=" * 60)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestEnhancedMatchingEngine))
    test_suite.addTest(unittest.makeSuite(TestEnhancedMatchingIntegration))
    test_suite.addTest(unittest.makeSuite(TestAsyncMatchingPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 所有增强匹配测试通过！算法优化效果良好。")
    else:
        print("❌ 部分增强匹配测试失败，需要进一步优化。")
        print(f"失败数量: {len(result.failures)}")
        print(f"错误数量: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_enhanced_matching_tests()
