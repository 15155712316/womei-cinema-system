#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码生成工具
用于根据取票码生成二维码图片
"""

import qrcode
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

def get_cinema_name_by_id(cinema_id: str) -> str:
    """
    根据影院ID获取影院名称
    :param cinema_id: 影院ID
    :return: 影院名称
    """
    try:
        # 导入影院管理器
        from services.cinema_manager import CinemaManager

        # 获取影院管理器实例
        cinema_manager = CinemaManager()

        # 获取所有影院数据
        cinemas = cinema_manager.load_cinema_list()

        # 查找匹配的影院
        for cinema in cinemas:
            if cinema.get('cinemaid') == cinema_id or cinema.get('id') == cinema_id:
                # 🔧 修复：使用正确的字段名 cinemaShortName
                cinema_name = (cinema.get('cinemaShortName') or
                              cinema.get('cinemaname') or
                              cinema.get('name', '未知影院'))
                print(f"[影院名称] 找到影院: {cinema_id} -> {cinema_name}")
                return cinema_name

        print(f"[影院名称] 未找到影院ID {cinema_id}，使用默认名称")
        return "未知影院"

    except Exception as e:
        print(f"[影院名称] 获取影院名称错误: {e}")
        # 降级使用硬编码映射
        cinema_name_map = {
            "35fec8259e74": "华夏优加荟大都荟",
            "b8e8b8b8b8b8": "其他影院1",
            "c9f9c9f9c9f9": "其他影院2"
        }
        return cinema_name_map.get(cinema_id, "未知影院")

def generate_ticket_qrcode(ticket_code: str, order_info: dict = None) -> bytes:
    """
    生成取票码二维码
    :param ticket_code: 取票码内容
    :param order_info: 订单信息（用于添加文字说明）
    :return: 二维码图片的字节数据
    """
    try:
        print(f"[二维码生成] 🎯 开始生成取票码二维码")
        print(f"[二维码生成] 📋 取票码: {ticket_code}")
        
        if not ticket_code:
            print(f"[二维码生成] ❌ 取票码为空")
            return None
        
        # 🎯 创建二维码对象
        qr = qrcode.QRCode(
            version=1,  # 控制二维码大小，1是最小的
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # 中等错误纠正
            box_size=8,  # 每个小方块的像素数
            border=2,   # 边框大小
        )
        
        # 添加取票码数据
        qr.add_data(ticket_code)
        qr.make(fit=True)
        
        # 🎯 生成二维码图片
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        print(f"[二维码生成] ✅ 基础二维码生成成功: {qr_img.size}")
        
        # 🎯 如果有订单信息，创建带文字说明的二维码
        if order_info:
            final_img = create_qrcode_with_info(qr_img, ticket_code, order_info)
        else:
            final_img = qr_img
        
        # 🎯 转换为字节数据
        img_bytes = io.BytesIO()
        final_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result_bytes = img_bytes.getvalue()
        print(f"[二维码生成] ✅ 二维码生成完成: {len(result_bytes)} bytes")
        
        return result_bytes
        
    except Exception as e:
        print(f"[二维码生成] ❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_qrcode_with_info(qr_img, ticket_code: str, order_info: dict) -> Image.Image:
    """
    创建带订单信息的二维码图片
    :param qr_img: 基础二维码图片
    :param ticket_code: 取票码
    :param order_info: 订单信息
    :return: 带信息的二维码图片
    """
    try:
        # 🎯 获取订单信息
        film_name = order_info.get('filmName', '未知影片')
        cinema_name = order_info.get('cinemaName', '未知影院')
        show_time = order_info.get('showTime', '未知时间')
        seat_info = order_info.get('seatInfo', '未知座位')
        
        # 🎯 计算画布大小
        qr_width, qr_height = qr_img.size
        text_height = 120  # 文字区域高度
        canvas_width = max(qr_width, 300)  # 最小宽度300
        canvas_height = qr_height + text_height
        
        # 🎯 创建画布
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        
        # 🎯 粘贴二维码（居中）
        qr_x = (canvas_width - qr_width) // 2
        canvas.paste(qr_img, (qr_x, 0))
        
        # 🎯 添加文字信息
        draw = ImageDraw.Draw(canvas)
        
        try:
            # 尝试使用系统字体
            font_large = ImageFont.truetype("msyh.ttc", 14)  # 微软雅黑
            font_small = ImageFont.truetype("msyh.ttc", 12)
        except:
            # 如果没有系统字体，使用默认字体
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # 🎯 绘制文字信息
        y_offset = qr_height + 10
        line_height = 18
        
        # 取票码（重点显示）
        ticket_text = f"取票码: {ticket_code}"
        text_width = draw.textlength(ticket_text, font=font_large)
        text_x = (canvas_width - text_width) // 2
        draw.text((text_x, y_offset), ticket_text, fill='red', font=font_large)
        y_offset += line_height + 5
        
        # 其他信息
        info_lines = [
            f"影片: {film_name[:15]}..." if len(film_name) > 15 else f"影片: {film_name}",
            f"影院: {cinema_name[:15]}..." if len(cinema_name) > 15 else f"影院: {cinema_name}",
            f"时间: {show_time}",
            f"座位: {seat_info}"
        ]
        
        for line in info_lines:
            if line.strip() and not line.endswith(': '):  # 跳过空信息
                text_width = draw.textlength(line, font=font_small)
                text_x = (canvas_width - text_width) // 2
                draw.text((text_x, y_offset), line, fill='black', font=font_small)
                y_offset += line_height
        
        print(f"[二维码生成] ✅ 带信息的二维码创建完成: {canvas.size}")
        return canvas
        
    except Exception as e:
        print(f"[二维码生成] ⚠️ 创建带信息二维码失败，返回基础二维码: {e}")
        return qr_img

def save_qrcode_image(qr_bytes: bytes, order_no: str, cinema_id: str) -> str:
    """
    保存二维码图片到本地
    :param qr_bytes: 二维码图片字节数据
    :param order_no: 订单号
    :param cinema_id: 影院ID
    :return: 保存的文件路径
    """
    try:
        # 🎯 获取影院名称 - 从影院管理器中获取真实名称
        cinema_name = get_cinema_name_by_id(cinema_id)
        
        # 🎯 生成日期字符串 (MMDD格式)
        current_date = datetime.now().strftime("%m%d")
        
        # 🎯 构建文件名：影院+日期+订单号.png
        filename = f"{cinema_name}_{current_date}_{order_no}_取票码.png"
        
        # 🎯 确保data/img目录存在
        img_dir = os.path.join("data", "img")
        os.makedirs(img_dir, exist_ok=True)
        
        # 🎯 完整文件路径
        file_path = os.path.join(img_dir, filename)
        
        # 🎯 保存图片
        with open(file_path, 'wb') as f:
            f.write(qr_bytes)
        
        print(f"[图片保存] ✅ 取票码二维码保存成功:")
        print(f"[图片保存] 📁 路径: {file_path}")
        print(f"[图片保存] 📏 大小: {len(qr_bytes)} bytes")
        
        return file_path
        
    except Exception as e:
        print(f"[图片保存] ❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_qrcode_generation():
    """测试二维码生成功能"""
    print("🧪 测试二维码生成功能")
    
    # 测试数据
    test_ticket_code = "ABC123456789"
    test_order_info = {
        'filmName': '测试影片名称',
        'cinemaName': '华夏优加荟大都荟',
        'showTime': '2025-06-02 19:30',
        'seatInfo': '5排7座'
    }
    
    # 生成二维码
    qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
    
    if qr_bytes:
        # 保存测试图片
        save_path = save_qrcode_image(qr_bytes, "TEST123", "35fec8259e74")
        print(f"✅ 测试成功，图片保存到: {save_path}")
    else:
        print("❌ 测试失败")

if __name__ == "__main__":
    test_qrcode_generation()
