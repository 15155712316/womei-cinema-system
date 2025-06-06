import re

def validate_cinema_id_format(cinemaid):
    """
    验证影院ID格式
    参数：
        cinemaid: 影院ID字符串
    返回：
        (是否有效, 格式化后的ID, 错误信息)
    """
    if not cinemaid:
        return False, "", "影院ID不能为空"
    
    # 移除空格和特殊字符
    clean_id = cinemaid.strip()
    
    # 检查长度（通常影院ID是8-16位）
    if len(clean_id) < 8:
        return False, clean_id, f"影院ID长度太短（{len(clean_id)}位），通常应为8-16位"
    elif len(clean_id) > 16:
        return False, clean_id, f"影院ID长度太长（{len(clean_id)}位），通常应为8-16位"
    
    # 检查字符类型
    if re.match(r'^[0-9a-fA-F]+$', clean_id):
        # 十六进制格式
        return True, clean_id.lower(), "十六进制格式"
    elif re.match(r'^[0-9]+$', clean_id):
        # 纯数字格式
        return True, clean_id, "数字格式"
    elif re.match(r'^[a-zA-Z0-9]+$', clean_id):
        # 字母数字混合
        return True, clean_id, "字母数字混合格式"
    else:
        return False, clean_id, "包含无效字符，影院ID应只包含字母和数字"

def get_common_cinema_ids():
    """
    获取一些常见的影院ID示例
    返回：
        示例影院ID列表
    """
    return [
        "11b7e4bcc265",  # 虹湾影城
        "0f1e21d86ac8",  # 万友影城
        "44012291",      # 数字格式示例
        "1234567890ab",  # 12位十六进制
        "abcd1234",      # 8位混合格式
    ]

def suggest_similar_ids(input_id):
    """
    根据输入的ID建议可能的正确格式
    参数：
        input_id: 用户输入的ID
    返回：
        建议的ID格式列表
    """
    suggestions = []
    
    # 如果是纯数字，尝试转换为十六进制
    if re.match(r'^[0-9]+$', input_id):
        try:
            hex_val = hex(int(input_id))[2:]  # 移除0x前缀
            if 8 <= len(hex_val) <= 16:
                suggestions.append(f"{hex_val} (转换为十六进制)")
        except:
            pass
    
    # 如果是十六进制，尝试转换为数字
    if re.match(r'^[0-9a-fA-F]+$', input_id):
        try:
            dec_val = str(int(input_id, 16))
            if 8 <= len(dec_val) <= 16:
                suggestions.append(f"{dec_val} (转换为十进制)")
        except:
            pass
    
    # 添加填充建议
    if len(input_id) < 12:
        padded = input_id.zfill(12)
        suggestions.append(f"{padded} (前置补零到12位)")
    
    return suggestions

def format_cinema_id_for_display(cinemaid, cinema_name=""):
    """
    格式化影院ID用于显示
    参数：
        cinemaid: 影院ID
        cinema_name: 影院名称（可选）
    返回：
        格式化的显示字符串
    """
    if cinema_name:
        return f"{cinemaid} ({cinema_name})"
    else:
        return cinemaid 