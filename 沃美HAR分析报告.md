# 沃美电影票务系统HAR文件分析报告

## 📋 概述

本报告基于HAR文件 `沃美下单用券ct.womovie.cn_2025_06_24_16_59_20.har` 的分析，该文件记录了沃美电影票务系统从创建订单开始到使用优惠券的完整网络请求流程，共包含35个API请求。

## 🔍 接口梳理与分类

### 1. 订单相关接口 (9个)

#### ✅ 已实现接口
- **POST** `/ticket/wmyc/cinema/{cinema_id}/order/ticket/` - 创建订单
- **GET** `/ticket/wmyc/cinema/{cinema_id}/order/info/` - 获取订单详情

#### 🔶 部分实现接口  
- **POST** `/ticket/wmyc/cinema/{cinema_id}/order/change/` - 修改订单
- **POST** `/ticket/wmyc/cinema/{cinema_id}/order/query/` - 查询订单状态

#### ❌ 未实现接口
- **GET** `/ticket/order/sublists/info` - 获取订单子列表
- **POST** `/ticket/wmyc/cinema/{cinema_id}/order/payment/` - 订单支付
- **POST** `/ticket/wmyc/cinema/{cinema_id}/order/template/` - 订单模板处理

### 2. 券相关接口 (15个)

#### ✅ 已实现接口
- **GET** `/ticket/wmyc/cinema/{cinema_id}/user/voucher/list/` - 获取用户券列表

#### ❌ 未实现接口
- **GET** `/ticket/wmyc/cinema/{cinema_id}/user/vouchers` - 获取特定类型券列表
  - `voucher_type=VGC_T` - 票券
  - `voucher_type=VGC_P` - 商品券
- **GET** `/ticket/wmyc/cinema/{cinema_id}/user/vouchers_page` - 分页获取券列表
- **POST** `/ticket/wmyc/cinema/{cinema_id}/order/voucher/price/` - 计算券价格
- **GET** `/ticket/wmyc/cinema/{cinema_id}/order/vcc/list/` - 获取订单VCC券列表
- **GET** `/ticket/wmyc/cinema/{cinema_id}/order/vcc/usable/count` - 获取可用VCC券数量

### 3. 用户相关接口 (5个)

#### ✅ 已实现接口
- **GET** `/ticket/wmyc/cinema/{cinema_id}/user/info/` - 获取用户信息
- **GET** `/ticket/wmyc/cinema/{cinema_id}/user/cards/` - 获取用户卡片

### 4. 其他接口 (6个)

#### ❓ 状态未知接口
- **GET** `/ticket/wmyc/cinema/{cinema_id}/ads/` - 获取广告
- **GET** `/ticket/wmyc/cinema/{cinema_id}/vcc/activity/gift/` - 获取VCC活动礼品

## 🎯 关键流程分析

### 券使用完整流程

1. **创建订单** → `POST /order/ticket/`
2. **获取券列表** → `GET /user/voucher/list/`
3. **获取特定券** → `GET /user/vouchers?voucher_type=VGC_T`
4. **计算券价格** → `POST /order/voucher/price/` ⚠️ **未实现**
5. **修改订单绑定券** → `POST /order/change/` (部分实现)
6. **订单支付** → `POST /order/payment/` ⚠️ **未实现**
7. **查询支付状态** → `POST /order/query/` (部分实现)

### 支付流程分析

从HAR文件可以看出完整的支付流程：

1. **选择券** → 用户选择要使用的券
2. **价格计算** → 调用券价格计算接口
3. **订单修改** → 绑定券到订单
4. **发起支付** → 调用支付接口
5. **状态轮询** → 定期查询支付状态
6. **支付完成** → 订单状态变为SUCCESS

## ❌ 缺失功能模块

### 1. 券价格计算模块
- **接口**: `POST /order/voucher/price/`
- **功能**: 计算使用券后的订单价格和手续费
- **参数**: `voucher_code`, `order_id`
- **响应**: `surcharge_price`, `pay_price`, `surcharge_msg`

### 2. 券类型查询模块
- **接口**: `GET /user/vouchers`
- **功能**: 按类型获取券列表
- **参数**: `voucher_type` (VGC_T/VGC_P), `schedule_id`, `goods_id`

### 3. VCC券管理模块
- **接口**: `GET /order/vcc/list/`, `GET /order/vcc/usable/count`
- **功能**: 管理EVGC_VOUCHER类型的券

### 4. 支付处理模块
- **接口**: `POST /order/payment/`
- **功能**: 处理订单支付，生成支付凭证
- **参数**: `order_id`, `mobile`, `pay_type`
- **响应**: `wechat_pay_certificate`, `total_fee`, `total_price`

### 5. 订单状态管理模块
- **接口**: `POST /order/query/`
- **功能**: 查询订单处理状态
- **状态**: PROCESSING → SUCCESS

## 🔧 实现状态对比

| 功能模块 | 当前状态 | 缺失接口数量 | 优先级 |
|---------|---------|-------------|--------|
| 订单创建 | ✅ 完整 | 0 | - |
| 订单查询 | ✅ 完整 | 0 | - |
| 基础券查询 | ✅ 完整 | 0 | - |
| 券价格计算 | ❌ 缺失 | 1 | 🔴 高 |
| 券类型查询 | ❌ 缺失 | 2 | 🟡 中 |
| VCC券管理 | ❌ 缺失 | 2 | 🟡 中 |
| 支付处理 | ❌ 缺失 | 1 | 🔴 高 |
| 订单状态管理 | 🔶 部分 | 0 | 🟡 中 |

## 📊 关键发现

### 1. 券使用的核心逻辑
- 用户选择券后，系统会调用价格计算接口验证券的有效性
- 券绑定通过修改订单接口实现，参数包括 `voucher_code` 和 `voucher_code_type`
- 支付时需要传递 `pay_type=WECHAT` 等参数

### 2. 订单修改的复杂性
- 订单修改接口承担了多种功能：支付方式切换、会员卡绑定、券绑定等
- 每次修改都会重新计算订单价格
- 支持多种折扣类型：MARKETING、TP_VOUCHER等

### 3. 支付流程的完整性
- 支付接口返回微信支付凭证
- 需要轮询查询支付状态
- 支付完成后订单状态从PROCESSING变为SUCCESS

## 🚀 建议实现优先级

### 高优先级 (立即实现)
1. **券价格计算接口** - 券使用的核心功能
2. **支付处理接口** - 完成支付流程的关键

### 中优先级 (后续实现)  
1. **券类型查询接口** - 提升券选择体验
2. **VCC券管理接口** - 支持更多券类型
3. **订单状态轮询** - 完善支付状态监控

### 低优先级 (可选实现)
1. **订单模板处理** - 消息推送功能
2. **广告接口** - 营销功能
3. **活动礼品接口** - 增值功能

## 📝 总结

通过HAR文件分析，我们发现当前系统在券使用和支付流程方面还有重要的功能缺失。最关键的是**券价格计算**和**支付处理**两个接口，这些是完成完整券使用流程的必要组件。

建议优先实现这两个核心接口，然后逐步补充其他功能模块，以提供完整的沃美电影票务系统体验。
