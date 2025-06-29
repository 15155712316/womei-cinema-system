#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美券管理服务
处理券的查询、过滤、分页等功能
"""

import requests
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

class VoucherStatus:
    """券状态常量"""
    UN_USE = "UN_USE"          # 未使用
    USED = "USED"              # 已使用
    DISABLED = "DISABLED"      # 已作废
    EXPIRED = "EXPIRED"        # 已过期

class VoucherBalanceType:
    """券余额类型常量"""
    NT = "NT"                  # 次数类型
    AMOUNT = "AMOUNT"          # 金额类型

class VoucherInfo:
    """券信息数据类"""
    def __init__(self, data: Dict[str, Any]):
        self.voucher_code = data.get('voucher_code', '')
        self.voucher_code_mask = data.get('voucher_code_mask', '')
        self.voucher_name = data.get('voucher_name', '')
        self.expire_time = data.get('expire_time', 0)
        self.expire_time_string = data.get('expire_time_string', '')
        self.voucher_desc = data.get('voucher_desc', '')
        self.bind_time = data.get('bind_time', 0)
        self.bind_time_str = data.get('bind_time_str', '')
        self.use_time = data.get('use_time', 0)
        self.use_time_str = data.get('use_time_str', '')
        self.status = data.get('status', '')
        self.voucher_balance = data.get('voucher_balance', 0)
        self.voucher_balance_type = data.get('voucher_balance_type', '')
        self.voucher_balance_str = data.get('voucher_balance_str', '')
        self.use_desc = data.get('use_desc', '')
        self.use_rule_desc = data.get('use_rule_desc', '')
        self.scope_desc = data.get('scope_desc', '')
        self.douyin_code_resault = data.get('douyin_code_resault', [])
    
    def is_valid(self) -> bool:
        """判断券是否有效（未使用且未过期）"""
        return (self.status == VoucherStatus.UN_USE and 
                self.expire_time > int(time.time()))
    
    def is_expired(self) -> bool:
        """判断券是否已过期"""
        return self.expire_time <= int(time.time())
    
    def get_expire_date(self) -> str:
        """获取格式化的过期日期"""
        if self.expire_time > 0:
            dt = datetime.fromtimestamp(self.expire_time)
            return dt.strftime('%Y年%m月%d日')
        return ''
    
    def get_bind_date(self) -> str:
        """获取格式化的绑定日期"""
        if self.bind_time > 0:
            dt = datetime.fromtimestamp(self.bind_time)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return ''
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'voucher_code': self.voucher_code,
            'voucher_code_mask': self.voucher_code_mask,
            'voucher_name': self.voucher_name,
            'expire_time': self.expire_time,
            'expire_time_string': self.expire_time_string,
            'voucher_desc': self.voucher_desc,
            'bind_time': self.bind_time,
            'bind_time_str': self.bind_time_str,
            'use_time': self.use_time,
            'use_time_str': self.use_time_str,
            'status': self.status,
            'voucher_balance': self.voucher_balance,
            'voucher_balance_type': self.voucher_balance_type,
            'voucher_balance_str': self.voucher_balance_str,
            'use_desc': self.use_desc,
            'use_rule_desc': self.use_rule_desc,
            'scope_desc': self.scope_desc,
            'is_valid': self.is_valid(),
            'is_expired': self.is_expired(),
            'expire_date_formatted': self.get_expire_date(),
            'bind_date_formatted': self.get_bind_date()
        }

class VoucherService:
    """沃美券管理服务"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn/ticket/wmyc"
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.10(0x13080a10) XWEB/1227',
            'x-channel-id': '40000',
            'wechat-referrer-appid': 'wx4bb9342b9d97d53c',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'content-type': 'multipart/form-data',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'wechat-referrer-info': '{"appId":"wx4bb9342b9d97d53c"}',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
    
    def get_vouchers_page(self, cinema_id: str, token: str, voucher_type: str = "VGC_T", 
                         page_index: int = 1) -> Dict[str, Any]:
        """
        获取指定页的券列表
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            voucher_type: 券类型，默认VGC_T
            page_index: 页码，从1开始
            
        Returns:
            API响应数据
        """
        url = f"{self.base_url}/cinema/{cinema_id}/user/vouchers_page"
        
        params = {
            'voucher_type': voucher_type,
            'page_index': page_index
        }
        
        headers = self.default_headers.copy()
        headers['token'] = token
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"获取券列表成功 - 页码: {page_index}, 影院: {cinema_id}")

            # 添加调试信息
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"API响应数据类型: {type(data)}")
                if isinstance(data, dict):
                    logger.debug(f"API响应keys: {list(data.keys())}")
                    data_field = data.get('data')
                    if data_field:
                        logger.debug(f"data字段类型: {type(data_field)}")
                        if isinstance(data_field, dict):
                            logger.debug(f"data字段keys: {list(data_field.keys())}")

            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取券列表失败: {e}")
            return {
                'ret': -1,
                'msg': f'网络请求失败: {str(e)}',
                'data': None
            }
        except json.JSONDecodeError as e:
            logger.error(f"解析响应数据失败: {e}")
            return {
                'ret': -1,
                'msg': f'数据解析失败: {str(e)}',
                'data': None
            }
    
    def get_all_vouchers(self, cinema_id: str, token: str, voucher_type: str = "VGC_T", 
                        only_valid: bool = False) -> Tuple[List[VoucherInfo], Dict[str, Any]]:
        """
        获取所有券列表（自动分页）
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            voucher_type: 券类型
            only_valid: 是否只返回有效券
            
        Returns:
            (券列表, 分页信息)
        """
        all_vouchers = []
        page_info = {}
        current_page = 1
        
        while True:
            result = self.get_vouchers_page(cinema_id, token, voucher_type, current_page)

            # 安全地检查API响应
            if not isinstance(result, dict):
                logger.error(f"获取第{current_page}页券列表失败: API响应不是字典格式")
                break

            if result.get('ret') != 0:
                logger.error(f"获取第{current_page}页券列表失败: {result.get('msg')}")
                break

            data = result.get('data', {})

            # 🔧 强健的数据格式处理 - 支持所有可能的格式
            page_info = {}
            vouchers_data = []

            try:
                if isinstance(data, dict):
                    # 格式1：标准字典格式 {page: {...}, result: [...]}
                    if 'page' in data and 'result' in data:
                        page_info = data.get('page', {})
                        vouchers_data = data.get('result', [])
                        logger.debug(f"第{current_page}页使用标准字典格式，券数量: {len(vouchers_data)}")

                    # 格式2：直接包含券数据的字典
                    elif any(key in data for key in ['voucher_code', 'voucher_name', 'vouchers']):
                        if 'vouchers' in data:
                            vouchers_data = data.get('vouchers', [])
                        else:
                            vouchers_data = [data]  # 单个券对象
                        page_info = {'total_page': 1, 'page_num': current_page, 'data_total': len(vouchers_data)}
                        logger.info(f"第{current_page}页使用券字典格式，券数量: {len(vouchers_data)}")

                    # 格式3：其他字典格式，尝试找到券数据
                    else:
                        # 尝试找到可能的券数据字段
                        possible_keys = ['data', 'items', 'list', 'vouchers', 'result']
                        for key in possible_keys:
                            if key in data and isinstance(data[key], list):
                                vouchers_data = data[key]
                                break
                        page_info = {'total_page': 1, 'page_num': current_page, 'data_total': len(vouchers_data)}
                        logger.info(f"第{current_page}页使用其他字典格式，券数量: {len(vouchers_data)}")

                elif isinstance(data, list):
                    # 格式4：data直接是券列表
                    vouchers_data = data
                    page_info = {'total_page': 1, 'page_num': current_page, 'data_total': len(data)}
                    logger.info(f"第{current_page}页使用列表格式，券数量: {len(vouchers_data)}")

                else:
                    # 格式5：未知格式
                    logger.error(f"第{current_page}页data字段格式未知: {type(data)}")
                    if data is None:
                        logger.warning(f"第{current_page}页data字段为None，跳过此页")
                        break
                    else:
                        logger.warning(f"第{current_page}页data内容: {str(data)[:100]}...")
                        vouchers_data = []
                        page_info = {}

            except Exception as parse_error:
                logger.error(f"第{current_page}页数据解析异常: {parse_error}")
                vouchers_data = []
                page_info = {}

            # 安全地检查券数据
            if not isinstance(vouchers_data, list):
                logger.error(f"获取第{current_page}页券列表失败: 券数据不是列表格式，类型: {type(vouchers_data)}")
                break

            # 转换为VoucherInfo对象
            for i, voucher_data in enumerate(vouchers_data):
                try:
                    # 确保券数据是字典格式
                    if not isinstance(voucher_data, dict):
                        logger.warning(f"第{current_page}页第{i+1}个券数据不是字典格式，跳过")
                        continue

                    voucher = VoucherInfo(voucher_data)

                    # 根据only_valid参数过滤
                    if only_valid and not voucher.is_valid():
                        continue

                    all_vouchers.append(voucher)

                except Exception as e:
                    logger.error(f"处理第{current_page}页第{i+1}个券数据失败: {e}")
                    continue
            
            # 检查是否还有下一页
            total_pages = page_info.get('total_page', 1)
            if current_page >= total_pages:
                break
                
            current_page += 1
            
            # 添加延迟避免请求过快
            time.sleep(0.5)
        
        logger.info(f"获取券列表完成 - 总数: {len(all_vouchers)}, 总页数: {page_info.get('total_page', 0)}")
        return all_vouchers, page_info
    
    def filter_vouchers(self, vouchers: List[VoucherInfo], 
                       status_filter: Optional[str] = None,
                       name_filter: Optional[str] = None,
                       expired_filter: Optional[bool] = None) -> List[VoucherInfo]:
        """
        过滤券列表
        
        Args:
            vouchers: 券列表
            status_filter: 状态过滤 (UN_USE, USED, DISABLED)
            name_filter: 名称过滤（包含匹配）
            expired_filter: 过期过滤 (True=只要过期的, False=只要未过期的, None=全部)
            
        Returns:
            过滤后的券列表
        """
        filtered = vouchers
        
        if status_filter:
            filtered = [v for v in filtered if v.status == status_filter]
        
        if name_filter:
            filtered = [v for v in filtered if name_filter.lower() in v.voucher_name.lower()]
        
        if expired_filter is not None:
            if expired_filter:
                filtered = [v for v in filtered if v.is_expired()]
            else:
                filtered = [v for v in filtered if not v.is_expired()]
        
        return filtered
    
    def get_voucher_statistics(self, vouchers: List[VoucherInfo]) -> Dict[str, Any]:
        """
        获取券统计信息
        
        Args:
            vouchers: 券列表
            
        Returns:
            统计信息字典
        """
        total = len(vouchers)
        valid_count = len([v for v in vouchers if v.is_valid()])
        used_count = len([v for v in vouchers if v.status == VoucherStatus.USED])
        disabled_count = len([v for v in vouchers if v.status == VoucherStatus.DISABLED])
        expired_count = len([v for v in vouchers if v.is_expired()])
        
        # 按券名称分组统计
        name_stats = {}
        for voucher in vouchers:
            name = voucher.voucher_name
            if name not in name_stats:
                name_stats[name] = {'total': 0, 'valid': 0, 'used': 0, 'disabled': 0}
            
            name_stats[name]['total'] += 1
            if voucher.is_valid():
                name_stats[name]['valid'] += 1
            elif voucher.status == VoucherStatus.USED:
                name_stats[name]['used'] += 1
            elif voucher.status == VoucherStatus.DISABLED:
                name_stats[name]['disabled'] += 1
        
        return {
            'total_count': total,
            'valid_count': valid_count,
            'used_count': used_count,
            'disabled_count': disabled_count,
            'expired_count': expired_count,
            'valid_rate': round(valid_count / total * 100, 2) if total > 0 else 0,
            'name_statistics': name_stats,
            'summary': {
                'has_valid_vouchers': valid_count > 0,
                'most_common_name': max(name_stats.keys(), key=lambda k: name_stats[k]['total']) if name_stats else None,
                'latest_bind_time': max([v.bind_time for v in vouchers]) if vouchers else 0
            }
        }

# 全局券服务实例
voucher_service = VoucherService()

def get_voucher_service() -> VoucherService:
    """获取券服务实例"""
    return voucher_service
