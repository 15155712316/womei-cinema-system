#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的二维码生成器
不依赖外部qrcode库，使用内置方法生成
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

def generate_simple_ticket_image(ticket_code: str, order_info: dict = None) -> bytes:
    """
    生成简化的取票码图片（不是真正的二维码，而是包含取票码信息的图片）
    """
    try:
        print(f"[简化二维码] 🎯 开始生成取票码图片")
        print(f"[简化二维码] 📋 取票码: {ticket_code}")
        
        if not ticket_code:
            print(f"[简化二维码] ❌ 取票码为空")
            return None
        
        # 🎯 获取订单信息
        film_name = order_info.get('filmName', '未知影片') if order_info else '未知影片'
        hall_name = order_info.get('hallName', '') if order_info else ''
        cinema_name = order_info.get('cinemaName', '未知影院') if order_info else '未知影院'
        show_time = order_info.get('showTime', '未知时间') if order_info else '未知时间'
        seat_info = order_info.get('seatInfo', '未知座位') if order_info else '未知座位'
        mobile = order_info.get('orderMobile', '') if order_info else ''
        cardno = order_info.get('cardno', '') if order_info else ''
        order_no = order_info.get('orderno', '') if order_info else ''
        ds_validate_code = order_info.get('dsValidateCode', ticket_code) if order_info else ticket_code
        
        # 🎯 创建画布
        canvas_width = 350
        canvas_height = 400
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
        
        # 🎯 添加文字信息
        draw = ImageDraw.Draw(canvas)
        
        try:
            # 尝试使用系统字体
            font_large = ImageFont.truetype("msyh.ttc", 20)  # 大字体
            font_medium = ImageFont.truetype("msyh.ttc", 18)  # 中字体
            font_small = ImageFont.truetype("msyh.ttc", 16)   # 小字体
        except:
            try:
                font_large = ImageFont.truetype("simhei.ttf", 20)
                font_medium = ImageFont.truetype("simhei.ttf", 18)
                font_small = ImageFont.truetype("simhei.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # 🎯 绘制取票码框
        y_offset = 30
        
        # 绘制取票码背景框
        box_margin = 20
        box_height = 80
        draw.rectangle([box_margin, y_offset, canvas_width - box_margin, y_offset + box_height], 
                      fill='#f0f0f0', outline='#cccccc', width=2)
        
        # 取票码标题
        title_text = "取票码"
        title_bbox = draw.textbbox((0, 0), title_text, font=font_medium)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (canvas_width - title_width) // 2
        draw.text((title_x, y_offset + 10), title_text, fill='#666666', font=font_medium)
        
        # 取票码内容
        code_text = ds_validate_code
        code_bbox = draw.textbbox((0, 0), code_text, font=font_large)
        code_width = code_bbox[2] - code_bbox[0]
        code_x = (canvas_width - code_width) // 2
        draw.text((code_x, y_offset + 40), code_text, fill='red', font=font_large)
        
        y_offset += box_height + 30
        
        # 🎯 绘制详细信息
        left_margin = 25
        line_height = 25
        
        info_items = [
            f"影片: {film_name}",
            f"影厅: {hall_name}" if hall_name else None,
            f"影院: {cinema_name}",
            f"时间: {show_time}",
            f"座位: {seat_info}",
            f"手机: {mobile}" if mobile else None,
            f"卡号: {cardno}" if cardno else None,
            f"订单: {order_no}" if order_no else None,
        ]
        
        for item in info_items:
            if item:  # 只显示非空项目
                draw.text((left_margin, y_offset), item, fill='black', font=font_small)
                y_offset += line_height
        
        print(f"[简化二维码] ✅ 取票码图片创建完成: {canvas.size}")
        
        # 转换为bytes
        img_buffer = io.BytesIO()
        canvas.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        print(f"[简化二维码] ✅ 图片生成完成: {len(img_bytes)} bytes")
        return img_bytes
        
    except Exception as e:
        print(f"[简化二维码] ❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_simple_image(img_bytes: bytes, order_no: str, cinema_id: str) -> str:
    """保存简化图片到本地"""
    try:
        # 生成文件名
        current_date = datetime.now().strftime("%m%d")
        filename = f"取票码_{current_date}_{order_no}.png"
        
        # 确保目录存在
        img_dir = os.path.join("data", "img")
        os.makedirs(img_dir, exist_ok=True)
        
        # 完整文件路径
        file_path = os.path.join(img_dir, filename)
        
        # 保存图片
        with open(file_path, 'wb') as f:
            f.write(img_bytes)
        
        print(f"[简化二维码] ✅ 图片保存成功: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"[简化二维码] ❌ 保存失败: {e}")
        return None

if __name__ == "__main__":
    # 测试
    test_code = "2025060239828060"
    test_info = {
        'filmName': '私家侦探',
        'hallName': '3号激光OMIS厅',
        'cinemaName': '深影国际影城(佐阾虹湾购物中心店)',
        'showTime': '2025-06-03 10:00',
        'seatInfo': '8排8座,8排9座',
        'dsValidateCode': '2025 0602 3982 8060',
        'orderno': '202506021611295648804'
    }
    
    img_bytes = generate_simple_ticket_image(test_code, test_info)
    if img_bytes:
        save_path = save_simple_image(img_bytes, "TEST123", "test")
        print(f"✅ 测试成功: {save_path}")
