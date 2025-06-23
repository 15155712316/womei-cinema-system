import requests
import json

def decode_unicode_message(response_text):
    """解码响应中的Unicode字符，特别是msg字段"""
    try:
        # 解析JSON响应
        data = json.loads(response_text)

        # 解码msg字段中的Unicode字符
        if 'msg' in data and isinstance(data['msg'], str):
            # 将Unicode编码转换为中文
            # 方法1：直接使用json.loads再次解析（推荐）
            try:
                # 将包含Unicode的字符串重新编码为JSON格式再解析
                unicode_str = f'"{data["msg"]}"'
                data['msg'] = json.loads(unicode_str)
            except:
                # 方法2：手动替换Unicode编码
                import codecs
                data['msg'] = codecs.decode(data['msg'], 'unicode_escape')

        return data
    except Exception as e:
        print(f"❌ 解码失败: {e}")
        print(f"原始响应: {response_text}")
        return None

def print_formatted_response(data):
    """格式化打印响应数据"""
    if not data:
        return

    print("🔍 绑券接口响应:")
    print("=" * 50)
    print(f"📊 返回码: {data.get('ret', 'N/A')}")
    print(f"📊 子码: {data.get('sub', 'N/A')}")
    print(f"💬 消息: {data.get('msg', 'N/A')}")
    print(f"📦 数据: {data.get('data', 'N/A')}")
    print("=" * 50)

    # 判断绑券结果
    if data.get('ret') == 0:
        if data.get('sub') == 0:
            print("✅ 绑券成功!")
        else:
            print(f"⚠️ 绑券失败: {data.get('msg', '未知错误')}")
    else:
        print(f"❌ 请求失败: {data.get('msg', '未知错误')}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
    'Content-Type': 'application/x-www-form-urlencoded',
    'x-channel-id': '40000',
    'tenant-short': 'wmyc',
    'client-version': '4.0',
    'xweb_xhr': '1',
    'x-requested-with': 'wxapp',
    'token': 'f0fc8c185ecf4e241320811c84157bbf',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
    'accept-language': 'zh-CN,zh;q=0.9',
    'priority': 'u=1, i',
}

data = {
    'voucher_code': 'GZJY010029484250342',
    'voucher_password': '3594',
    'voucher_type': 'VOUCHER',
}

response = requests.post('https://ct.womovie.cn/ticket/wmyc/cinema/400028/user/voucher/add/', headers=headers, data=data, verify=False)

print("📡 原始响应:")
print(response.text)
print()

# 解码Unicode字符并格式化显示
decoded_data = decode_unicode_message(response.text)
if decoded_data:
    print_formatted_response(decoded_data)

    # 同时输出解码后的完整JSON（便于复制使用）
    print("\n📋 解码后的完整JSON:")
    print(json.dumps(decoded_data, ensure_ascii=False, indent=2))