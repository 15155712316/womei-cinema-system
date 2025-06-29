#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码生成工具
用于根据取票码生成二维码图片
"""

import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

# 🔧 根本性解决方案：多重导入策略
import sys
import os

# 全局变量，避免重复检查
QRCODE_AVAILABLE = None
qrcode = None

def ensure_qrcode_import():
    """确保qrcode模块可用的多重策略函数"""
    global QRCODE_AVAILABLE, qrcode

    if QRCODE_AVAILABLE is not None:
        return QRCODE_AVAILABLE, qrcode

    # 策略1: 直接导入
    try:
        import qrcode as qr_module
        QRCODE_AVAILABLE = True
        qrcode = qr_module
        print(f"[二维码生成] ✅ 策略1-直接导入: 成功")
        return True, qr_module
    except ImportError:
        pass

    # 策略2: 使用importlib动态导入
    try:
        import importlib
        qr_module = importlib.import_module('qrcode')
        QRCODE_AVAILABLE = True
        qrcode = qr_module
        print(f"[二维码生成] ✅ 策略2-importlib导入: 成功")
        return True, qr_module
    except ImportError:
        pass

    # 策略3: 手动添加路径后导入
    try:
        # 获取Python安装路径
        python_path = os.path.dirname(sys.executable)
        site_packages = os.path.join(python_path, 'lib', 'site-packages')

        if os.path.exists(site_packages) and site_packages not in sys.path:
            sys.path.insert(0, site_packages)
            print(f"[二维码生成] 🔧 策略3-添加路径: {site_packages}")

        import qrcode as qr_module
        QRCODE_AVAILABLE = True
        qrcode = qr_module
        print(f"[二维码生成] ✅ 策略3-路径修复导入: 成功")
        return True, qr_module
    except ImportError:
        pass

    # 策略4: 使用subprocess安装后导入
    try:
        import subprocess
        print(f"[二维码生成] 🔧 策略4-尝试重新安装qrcode模块...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "qrcode[pil]", "--force-reinstall"],
                              capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            import qrcode as qr_module
            QRCODE_AVAILABLE = True
            qrcode = qr_module
            print(f"[二维码生成] ✅ 策略4-重新安装导入: 成功")
            return True, qr_module
    except Exception as e:
        print(f"[二维码生成] ⚠️ 策略4失败: {e}")

    # 所有策略都失败
    QRCODE_AVAILABLE = False
    qrcode = None
    print(f"[二维码生成] ❌ 所有导入策略都失败，使用备用方案")

    # 详细诊断信息
    print(f"[二维码生成] 🔍 导入失败诊断:")
    print(f"[二维码生成] 📋 Python: {sys.executable}")
    print(f"[二维码生成] 📋 工作目录: {os.getcwd()}")
    print(f"[二维码生成] 📋 sys.path前3项: {sys.path[:3]}")

    return False, None

# 在模块加载时执行一次检查
QRCODE_AVAILABLE, qrcode = ensure_qrcode_import()

def get_cinema_name_by_id(cinema_id: str) -> str:
    """
    根据影院ID获取影院名称 - 🔧 修复：优先从沃美系统获取影院名称
    :param cinema_id: 影院ID
    :return: 影院名称
    """
    try:
        # 🎯 第一优先级：从沃美系统的全局影院数据获取
        try:
            from utils.signals import event_bus
            # 使用新的方法从事件总线获取沃美影院数据
            cinema_info = event_bus.find_womei_cinema_by_id(cinema_id)
            if cinema_info:
                cinema_name = cinema_info.get('cinema_name', '未知影院')
                print(f"[影院名称] ✅ 从沃美系统获取: {cinema_id} -> {cinema_name}")
                return cinema_name

            # 如果没有找到，尝试从所有沃美影院数据中查找
            womei_cinemas = event_bus.get_womei_cinemas()
            for cinema in womei_cinemas:
                if cinema.get('cinema_id') == cinema_id:
                    cinema_name = cinema.get('cinema_name', '未知影院')
                    print(f"[影院名称] ✅ 从沃美影院列表获取: {cinema_id} -> {cinema_name}")
                    return cinema_name
        except Exception as e:
            print(f"[影院名称] 从沃美系统获取失败: {e}")

        # 🎯 第二优先级：从本地影院管理器获取（华联系统）
        try:
            from services.cinema_manager import CinemaManager
            cinema_manager = CinemaManager()
            cinemas = cinema_manager.load_cinema_list()

            for cinema in cinemas:
                if cinema.get('cinemaid') == cinema_id or cinema.get('id') == cinema_id:
                    cinema_name = (cinema.get('cinemaShortName') or
                                  cinema.get('cinemaname') or
                                  cinema.get('name', '未知影院'))
                    print(f"[影院名称] ✅ 从本地数据获取: {cinema_id} -> {cinema_name}")
                    return cinema_name
        except Exception as e:
            print(f"[影院名称] 从本地数据获取失败: {e}")

        # 🎯 第三优先级：沃美系统硬编码映射
        womei_cinema_map = {
            "400028": "北京沃美世界城店",
            "400115": "沃美北京龙湖店",
            "400295": "沃美影城北京顺义鲁能店",
            "400357": "沃美总部尊享卡中心",
            "8065": "北京沃美影城(常营店)",
            "9647": "北京沃美影城(回龙观店)",
            "400296": "沃美影城武汉龙湖白沙店",
            "400031": "南宁沃美影城（大唐天城店）",
            "400127": "沃美合肥银泰店",
            "1402": "贵阳沃美影城(世纪金源购物中心店)",
            "2678": "东莞沃美影城（光大店）",
            "400308": "沃美影城泰安爱琴海店",
            "9934": "慈溪沃美影城"
        }

        if cinema_id in womei_cinema_map:
            cinema_name = womei_cinema_map[cinema_id]
            print(f"[影院名称] ✅ 从沃美映射获取: {cinema_id} -> {cinema_name}")
            return cinema_name

        # 🎯 第四优先级：华联系统硬编码映射
        huanlian_cinema_map = {
            "35fec8259e74": "华夏优加荟大都荟",
            "11b7e4bcc265": "深影国际影城(佐阾虹湾购物中心店)",
            "72f496f05710": "中影星美国际影城（郓城店）",
            "c71994bd3279": "1929电影公园"
        }

        if cinema_id in huanlian_cinema_map:
            cinema_name = huanlian_cinema_map[cinema_id]
            print(f"[影院名称] ✅ 从华联映射获取: {cinema_id} -> {cinema_name}")
            return cinema_name

        print(f"[影院名称] ❌ 未找到影院ID {cinema_id}，使用默认名称")
        return "未知影院"

    except Exception as e:
        print(f"[影院名称] ❌ 获取影院名称错误: {e}")
        import traceback
        traceback.print_exc()
        return "未知影院"

def create_fallback_qrcode(ticket_code: str, size: tuple = (200, 200)) -> Image.Image:
    """
    创建备用二维码图片（当qrcode模块不可用时）
    生成一个包含取票码的简单图片
    """
    try:
        width, height = size
        img = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(img)

        # 绘制边框
        border_width = 10
        draw.rectangle([border_width, border_width, width-border_width, height-border_width],
                      outline='black', width=3)

        # 绘制网格模式（模拟二维码外观）
        grid_size = 8
        for x in range(border_width + 20, width - border_width - 20, grid_size):
            for y in range(border_width + 20, height - border_width - 20, grid_size):
                # 根据位置创建伪随机模式
                if (x + y) % 16 < 8:
                    draw.rectangle([x, y, x + grid_size - 1, y + grid_size - 1], fill='black')

        # 在中心绘制取票码文字
        try:
            font = ImageFont.truetype("msyh.ttc", 14)
        except:
            font = ImageFont.load_default()

        # 计算文字位置
        text_bbox = draw.textbbox((0, 0), ticket_code, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # 绘制白色背景
        padding = 5
        draw.rectangle([text_x - padding, text_y - padding,
                       text_x + text_width + padding, text_y + text_height + padding],
                      fill='white', outline='black')

        # 绘制取票码文字
        draw.text((text_x, text_y), ticket_code, fill='black', font=font)

        return img

    except Exception as e:
        print(f"[二维码生成] ❌ 创建备用二维码失败: {e}")
        # 返回一个简单的白色图片
        return Image.new('RGB', size, 'white')

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

        # 🎯 确保qrcode模块可用并选择生成方式
        qr_available, qr_module = ensure_qrcode_import()

        if qr_available and qr_module:
            print(f"[二维码生成] 🎯 使用完整二维码生成")
            # 🎯 创建二维码对象（优化清晰度）
            qr = qr_module.QRCode(
                version=1,  # 控制二维码大小，1是最小的
                error_correction=qr_module.constants.ERROR_CORRECT_M,  # 中等错误纠正
                box_size=12,  # 🎨 增加每个小方块的像素数：从8提高到12
                border=3,   # 🎨 增加边框大小：从2提高到3
            )

            # 添加取票码数据
            qr.add_data(ticket_code)
            qr.make(fit=True)

            # 🎯 生成二维码图片（增大尺寸）
            qr_img = qr.make_image(fill_color="black", back_color="white")

            # 🎨 增大二维码尺寸（增加25%）
            original_size = qr_img.size
            new_size = int(original_size[0] * 1.25), int(original_size[1] * 1.25)
            qr_img = qr_img.resize(new_size, Image.NEAREST)  # 使用NEAREST保持清晰度

            print(f"[二维码生成] ✅ 完整二维码生成成功: {original_size} -> {qr_img.size}")
        else:
            print(f"[二维码生成] 🎯 使用备用二维码生成")
            # 使用备用方案（也增大尺寸）
            qr_img = create_fallback_qrcode(ticket_code, (250, 250))  # 🎨 从200增加到250
            print(f"[二维码生成] ✅ 备用二维码生成成功: {qr_img.size}")

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
        hall_name = order_info.get('hallName', '')  # 影厅
        cinema_name = order_info.get('cinemaName', '未知影院')
        show_time = order_info.get('showTime', '未知时间')
        seat_info = order_info.get('seatInfo', '未知座位')
        mobile = order_info.get('orderMobile', '')  # 手机号
        cardno = order_info.get('cardno', '')  # 卡号
        order_no = order_info.get('orderno', '')  # 订单号
        ds_validate_code = order_info.get('dsValidateCode', ticket_code)  # 使用dsValidateCode

        # 🎯 计算紧凑布局的画布大小
        qr_width, qr_height = qr_img.size

        # 🎨 计算实际需要的文字高度（8行文字 + 间距）
        estimated_text_lines = 8  # 取票码+影片+影厅+影院+时间+座位+手机+订单
        text_area_height = estimated_text_lines * 28 + 20  # 28px行高 + 20px缓冲

        # 🎨 紧凑布局：减少画布尺寸，提高内容占比
        canvas_width = max(qr_width + 40, 320)  # 🎨 减少宽度：从350到320，增加40px边距
        canvas_height = qr_height + text_area_height + 30  # 🎨 减少总高度，只保留30px缓冲

        print(f"[二维码生成] 📐 画布尺寸: {canvas_width}x{canvas_height}")
        print(f"[二维码生成] 📐 二维码尺寸: {qr_width}x{qr_height}")
        print(f"[二维码生成] 📐 文字区域高度: {text_area_height}")

        # 🎯 创建紧凑画布
        canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')

        # 🎯 粘贴二维码（顶部留少量边距）
        qr_x = (canvas_width - qr_width) // 2
        qr_y = 8  # 🎨 顶部边距：8px
        canvas.paste(qr_img, (qr_x, qr_y))

        # 🎯 添加文字信息
        draw = ImageDraw.Draw(canvas)

        try:
            # 🎨 统一字体：所有文字都使用24px微软雅黑（进一步提高清晰度）
            font_unified = ImageFont.truetype("msyh.ttc", 24)  # 🎨 从18px提高到24px
        except:
            try:
                # 尝试其他中文字体
                font_unified = ImageFont.truetype("simhei.ttf", 24)  # 黑体
            except:
                # 如果没有系统字体，使用默认字体
                font_unified = ImageFont.load_default()

        # 🎯 绘制文字信息（紧凑布局）
        left_margin = 12  # 🎨 减少左边距：从15px到12px
        y_offset = qr_y + qr_height + 12  # 🎨 减少二维码与文字间距：从20px到12px
        line_height = 26  # 🎨 紧凑行间距：从28px减少到26px，保持可读性

        # 🎯 取票码（使用dsValidateCode，重点显示，红色）
        ticket_text = f"取票码: {ds_validate_code}"
        draw.text((left_margin, y_offset), ticket_text, fill='red', font=font_unified)
        y_offset += line_height

        # 🎯 影片信息（左对齐，黑色）
        if film_name and film_name != '未知影片':
            film_text = f"影片: {film_name}"
            draw.text((left_margin, y_offset), film_text, fill='black', font=font_unified)
            y_offset += line_height

        # 🎯 影厅信息（新增，黑色）
        if hall_name:
            hall_text = f"影厅: {hall_name}"
            draw.text((left_margin, y_offset), hall_text, fill='black', font=font_unified)
            y_offset += line_height

        # 🎯 影院信息（左对齐，黑色）
        if cinema_name and cinema_name != '未知影院':
            cinema_text = f"影院: {cinema_name}"
            draw.text((left_margin, y_offset), cinema_text, fill='black', font=font_unified)
            y_offset += line_height

        # 🎯 时间信息（左对齐，黑色）
        if show_time and show_time != '未知时间':
            time_text = f"时间: {show_time}"
            draw.text((left_margin, y_offset), time_text, fill='black', font=font_unified)
            y_offset += line_height

        # 🎯 座位信息（左对齐，黑色）
        if seat_info and seat_info != '未知座位':
            seat_text = f"座位: {seat_info}"
            draw.text((left_margin, y_offset), seat_text, fill='black', font=font_unified)
            y_offset += line_height

        # 🎯 次要信息使用更紧凑的间距
        compact_line_height = 24  # 🎨 次要信息使用更小的行间距

        # 🎯 手机号信息（新增，黑色，统一字体）
        if mobile:
            mobile_text = f"手机: {mobile}"
            draw.text((left_margin, y_offset), mobile_text, fill='black', font=font_unified)
            y_offset += compact_line_height

        # 🎯 卡号信息（新增，黑色，统一字体）
        if cardno:
            card_text = f"卡号: {cardno}"
            draw.text((left_margin, y_offset), card_text, fill='black', font=font_unified)
            y_offset += compact_line_height

        # 🎯 订单编号（新增，黑色，统一字体）
        if order_no:
            order_text = f"订单: {order_no}"
            draw.text((left_margin, y_offset), order_text, fill='black', font=font_unified)

        print(f"[二维码生成] ✅ 带信息的二维码创建完成: {canvas.size}")
        return canvas

    except Exception as e:
        print(f"[二维码生成] ⚠️ 创建带信息二维码失败，返回基础二维码: {e}")
        return qr_img

def save_qrcode_image(qr_bytes: bytes, order_no: str, cinema_id: str) -> str:
    """
    保存二维码图片到本地 - 🔧 修复：保存到上级目录的"票根"文件夹
    :param qr_bytes: 二维码图片字节数据
    :param order_no: 订单号
    :param cinema_id: 影院ID
    :return: 保存的文件路径
    """
    try:
        # 🎯 获取影院名称 - 从沃美系统或本地数据获取真实名称
        cinema_name = get_cinema_name_by_id(cinema_id)

        # 🎯 生成日期字符串 (MMDD格式)
        current_date = datetime.now().strftime("%m%d")

        # 🎯 构建文件名：影院+日期+订单号_取票码.png
        filename = f"{cinema_name}_{current_date}_{order_no}_取票码.png"

        # 🔧 修复：使用相对路径保存到上级目录的"票根"文件夹
        # 获取当前脚本所在目录的上级目录
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        parent_dir = os.path.dirname(current_dir)
        ticket_dir = os.path.join(parent_dir, "票根")

        # 🎯 确保"票根"目录存在
        os.makedirs(ticket_dir, exist_ok=True)
        print(f"[图片保存] 📁 票根目录: {ticket_dir}")

        # 🎯 完整文件路径
        file_path = os.path.join(ticket_dir, filename)

        # 🎯 保存图片
        with open(file_path, 'wb') as f:
            f.write(qr_bytes)

        print(f"[图片保存] ✅ 取票码二维码保存成功:")
        print(f"[图片保存] 📁 路径: {file_path}")
        print(f"[图片保存] 📏 大小: {len(qr_bytes)} bytes")
        print(f"[图片保存] 🎬 影院: {cinema_name}")
        print(f"[图片保存] 🎫 订单: {order_no}")

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
