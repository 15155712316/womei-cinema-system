#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
订单详情图片合成测试脚本
"""

from PIL import Image, ImageDraw, ImageFont
import io
import os
import datetime
import re

def test_image_generation():
    """测试图片合成功能"""
    
    # 模拟订单详情数据
    detail = {
        'resultCode': '0',
        'resultData': {
            'filmName': '星际宝贝史迪奇',
            'showTime': '2025-05-23 20:00 (英语3D)',
            'hallName': '7号厅',
            'seatInfo': '5排2座,5排3座',
            'dsValidateCode': '2025 0523 7855 7044',
            'orderno': '20250522222245684316',
            'orderMobile': '15155712316',
            'cinemaName': '深圳万友影城BCMall店',
            'payTime': '2025-05-22 22:23:05',
            'payAmount': 0
        }
    }
    
    data = detail['resultData']
    film = data.get('filmName', '')
    show_time = data.get('showTime', '')
    hall = data.get('hallName', '')
    seat_info = data.get('seatInfo', '')
    ds_code = data.get('dsValidateCode', '')
    orderno = data.get('orderno', '')
    mobile = data.get('orderMobile', '')
    cinema_name = data.get('cinemaName', '')
    pay_time = data.get('payTime', '')
    pay_amount = data.get('payAmount', 0)
    pay_amount_str = f"¥{int(pay_amount)/100:.2f}" if pay_amount else ""
    
    # 取当前月日
    try:
        if pay_time:
            dt = datetime.datetime.strptime(pay_time[:10], "%Y-%m-%d")
        else:
            dt = datetime.datetime.now()
        month_day = dt.strftime("%m%d")
    except:
        month_day = datetime.datetime.now().strftime("%m%d")
    
    # 影院名去除特殊字符
    cinema_name_safe = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', cinema_name)
    img_filename = f"{cinema_name_safe}_{month_day}_{orderno}.png"
    
    # 优化图片尺寸和布局 - 减少留白，提升观感
    width, height = 320, 420
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("msyh.ttc", 18)  # 标题稍大
        font_text = ImageFont.truetype("msyh.ttc", 12)   # 正文适中 
        font_code = ImageFont.truetype("msyh.ttc", 15)   # 取票码突出
        font_small = ImageFont.truetype("msyh.ttc", 10)  # 小字体
    except:
        font_title = font_text = font_code = font_small = None
    
    # 减少顶部边距
    y = 8
    
    # 电影名称（标题，加粗效果）
    draw.text((12, y), film, fill='black', font=font_title)
    y += 26
    
    # 场次时间
    draw.text((12, y), show_time, fill='#555', font=font_text)
    y += 18
    
    # 影厅和座位信息
    draw.text((12, y), f"{hall}  {seat_info}", fill='#555', font=font_text)
    y += 22
    
    # 取票分割线（减少间距）
    draw.line((12, y, width-12, y), fill='#ddd', width=1)
    y += 8
    draw.text((12, y), "取票", fill='black', font=font_text)
    y += 16
    
    # 二维码居中显示（增大尺寸）
    qr_size = 140
    qr_x = int((width - qr_size) / 2)
    qr_img = Image.new('RGB', (qr_size, qr_size), color='white')
    qr_draw = ImageDraw.Draw(qr_img)
    # 简单的二维码模拟图案
    for i in range(0, qr_size, 10):
        for j in range(0, qr_size, 10):
            if (i//10 + j//10) % 2 == 0:
                qr_draw.rectangle([i, j, i+10, j+10], fill='black')
    img.paste(qr_img, (qr_x, y))
    y += qr_size + 6
    
    # 取票码（橙色高亮，居中，减少间距）
    if ds_code:
        code_text = f"取票码：{ds_code}"
        try:
            code_w = draw.textlength(code_text, font=font_code)
        except:
            code_w = len(code_text) * 10
        draw.text(((width - code_w) // 2, y), code_text, fill='#ff6600', font=font_code)
        y += 20
    
    # 提示文字（缩小字体，减少间距）
    tip_text = "请到自助取票机扫描上述二维码取票"
    try:
        tip_w = draw.textlength(tip_text, font=font_small)
    except:
        tip_w = len(tip_text) * 6
    draw.text(((width - tip_w) // 2, y), tip_text, fill='#999', font=font_small)
    y += 18
    
    # 订单详情分割线（减少间距）
    draw.line((12, y, width-12, y), fill='#ddd', width=1)
    y += 8
    draw.text((12, y), "订单详情", fill='black', font=font_text)
    y += 16
    
    # 订单信息（紧凑布局，减少行间距）
    line_height = 15
    
    # 实付金额
    if pay_amount_str:
        draw.text((12, y), f"实付金额：{pay_amount_str}", fill='#333', font=font_text)
        y += line_height
    
    # 影院名称
    # 如果影院名太长，截断显示
    cinema_display = cinema_name[:15] + "..." if len(cinema_name) > 15 else cinema_name
    draw.text((12, y), f"影院名称：{cinema_display}", fill='#333', font=font_text)
    y += line_height
    
    # 手机号码
    if mobile:
        draw.text((12, y), f"手机号码：{mobile}", fill='#333', font=font_text)
        y += line_height
    
    # 订单号（分行显示，避免过长）
    if orderno:
        if len(orderno) > 16:
            draw.text((12, y), f"订单号：{orderno[:16]}", fill='#333', font=font_text)
            y += line_height
            draw.text((12, y), f"        {orderno[16:]}", fill='#333', font=font_text)
        else:
            draw.text((12, y), f"订单号：{orderno}", fill='#333', font=font_text)
        y += line_height
    
    # 购买时间
    if pay_time:
        draw.text((12, y), f"购买时间：{pay_time}", fill='#333', font=font_text)
    
    # 保存图片到data/img
    img_dir = os.path.join('data', 'img')
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.abspath(os.path.join(img_dir, img_filename))
    img.save(img_path)
    
    print(f"优化后测试图片已生成: {img_path}")
    print(f"图片尺寸: {width}x{height}")
    print(f"文件名: {img_filename}")
    print("优化要点：")
    print("- 图片尺寸从280x360调整为320x420")
    print("- 减少边距从20px调整为12px")
    print("- 二维码尺寸从120x120增大到140x140")
    print("- 行间距从16-24px减少到15px")
    print("- 字体大小进行分级优化")
    print("- 长文本进行截断处理")
    
    return img_path

if __name__ == "__main__":
    test_image_generation() 