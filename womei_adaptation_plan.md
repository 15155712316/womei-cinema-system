# 沃美影院系统适配方案

## 📋 HAR文件分析总结

### 1. 基本信息
- **总请求数**: 51个
- **API请求数**: 27个
- **主要域名**: ct.womovie.cn
- **Token**: 47794858a832916d8eda012e7cabd269

### 2. 业务流程映射

#### 完整的API调用链路：
1. **城市选择** → `GET /ticket/wmyc/citys/`
2. **影院信息** → `GET /ticket/wmyc/cinema/{cinema_id}/info/`
3. **电影列表** → `GET /ticket/wmyc/cinema/{cinema_id}/movies/`
4. **场次列表** → `GET /ticket/wmyc/cinema/{cinema_id}/shows/?movie_id={movie_id}`
5. **座位信息** → `GET /ticket/wmyc/cinema/{cinema_id}/hall/info/?hall_id={hall_id}&schedule_id={schedule_id}`
6. **座位状态** → `GET /ticket/wmyc/cinema/{cinema_id}/hall/saleable/?schedule_id={schedule_id}`
7. **订单创建** → `POST /ticket/wmyc/cinema/{cinema_id}/order/ticket/`
8. **订单信息** → `GET /ticket/wmyc/cinema/{cinema_id}/order/info/?order_id={order_id}`

### 3. 关键发现

#### ✅ 现有配置验证
- 域名: `ct.womovie.cn` ✓
- tenant-short: `wmyc` ✓  
- x-channel-id: `40000` ✓
- client-version: `4.0` ✓
- 微信小程序ID: `wx4bb9342b9d97d53c` ✓

#### 🔍 API端点差异
**现有配置**:
```python
"endpoints": {
    "cities": "/ticket/{tenant_short}/citys/",
    "cinemas": "/ticket/{tenant_short}/cinemas/", 
    "movies": "/ticket/{tenant_short}/movies/",
    "sessions": "/ticket/{tenant_short}/sessions/",
    "order": "/ticket/{tenant_short}/order/"
}
```

**实际HAR中的端点**:
```python
"endpoints": {
    "cities": "/ticket/wmyc/citys/",
    "cinema_info": "/ticket/wmyc/cinema/{cinema_id}/info/",
    "movies": "/ticket/wmyc/cinema/{cinema_id}/movies/",
    "shows": "/ticket/wmyc/cinema/{cinema_id}/shows/",
    "hall_info": "/ticket/wmyc/cinema/{cinema_id}/hall/info/",
    "hall_saleable": "/ticket/wmyc/cinema/{cinema_id}/hall/saleable/",
    "order_ticket": "/ticket/wmyc/cinema/{cinema_id}/order/ticket/",
    "order_info": "/ticket/wmyc/cinema/{cinema_id}/order/info/",
    "user_info": "/ticket/wmyc/cinema/{cinema_id}/user/info/",
    "member_card": "/ticket/wmyc/cinema/{cinema_id}/member/card/auto_solid/"
}
```

## 🔧 适配方案

### 阶段1: API配置更新

#### 1.1 更新cinema_api_adapter.py
需要扩展端点配置以支持cinema_id参数：

```python
WOMEI: {
    "endpoints": {
        "cities": "/ticket/{tenant_short}/citys/",
        "cinema_info": "/ticket/{tenant_short}/cinema/{cinema_id}/info/",
        "movies": "/ticket/{tenant_short}/cinema/{cinema_id}/movies/",
        "shows": "/ticket/{tenant_short}/cinema/{cinema_id}/shows/",
        "hall_info": "/ticket/{tenant_short}/cinema/{cinema_id}/hall/info/",
        "hall_saleable": "/ticket/{tenant_short}/cinema/{cinema_id}/hall/saleable/",
        "order_ticket": "/ticket/{tenant_short}/cinema/{cinema_id}/order/ticket/",
        "order_info": "/ticket/{tenant_short}/cinema/{cinema_id}/order/info/",
        "user_info": "/ticket/{tenant_short}/cinema/{cinema_id}/user/info/",
        "member_card": "/ticket/{tenant_short}/cinema/{cinema_id}/member/card/auto_solid/"
    }
}
```

#### 1.2 请求参数分析
从HAR文件中提取的关键请求参数：

**订单创建请求体**:
```
seatlable=10013:7:5:11112211#04#10|10013:7:4:11112211#04#09&schedule_id=16607189
```

**订单变更请求体**:
```
order_id=250615152110001239&discount_id=0&discount_type=MARKETING&card_id=376354&pay_type=MEMBER&rewards=[]&use_rewards=Y&use_limit_cards=N&limit_cards=[]&voucher_code=&voucher_code_type=&ticket_pack_goods=
```

### 阶段2: 代码适配

#### 2.1 需要修改的文件清单

1. **cinema_api_adapter.py**
   - 扩展端点配置
   - 添加cinema_id参数支持
   - 更新请求方法

2. **services/film_service.py**
   - 修改get_films函数适配新的API端点
   - 更新数据解析逻辑

3. **services/cinema_manager.py**
   - 更新影院信息获取逻辑
   - 适配新的API结构

4. **services/order_api.py**
   - 更新订单创建API调用
   - 适配新的请求参数格式

5. **main_modular.py**
   - 更新业务流程逻辑
   - 确保cinema_id正确传递

#### 2.2 关键修改点

**API客户端适配**:
```python
def build_api_url(self, endpoint: str, cinema_id: str = None) -> str:
    """构建API完整URL，支持cinema_id参数"""
    config = self.get_config()
    api_config = config["api_config"]
    endpoint_path = config["endpoints"].get(endpoint)
    
    if not endpoint_path:
        raise ValueError(f"不支持的接口端点: {endpoint}")
    
    # 替换路径中的占位符
    path = endpoint_path.format(
        tenant_short=api_config["tenant_short"],
        cinema_id=cinema_id or ""
    )
    return f"{api_config['base_url']}{path}"
```

**数据格式适配**:
- 座位数据格式: `seatlable=10013:7:5:11112211#04#10|10013:7:4:11112211#04#09`
- 响应格式: `{"ret": 0, "sub": 0, "msg": "successfully", "data": {...}}`

### 阶段3: 实施步骤

#### 步骤1: 验证现有配置 (1天)
- [ ] 测试现有cinema_api_adapter.py的沃美配置
- [ ] 验证基础API调用（城市列表）
- [ ] 确认token有效性

#### 步骤2: 扩展API适配器 (2天)
- [ ] 更新端点配置
- [ ] 添加cinema_id参数支持
- [ ] 实现新的API方法

#### 步骤3: 修改业务逻辑 (3天)
- [ ] 更新film_service.py
- [ ] 修改cinema_manager.py
- [ ] 适配order_api.py
- [ ] 更新主窗口逻辑

#### 步骤4: 数据格式适配 (2天)
- [ ] 分析响应数据结构
- [ ] 创建数据转换器
- [ ] 更新数据解析逻辑

#### 步骤5: 测试验证 (2天)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 完整流程测试

## 🚨 关键注意事项

### 1. API差异
- 沃美系统的大部分API都需要cinema_id参数
- 端点路径结构与华联系统不同
- 请求参数格式可能有差异

### 2. 数据结构
- 响应格式: `{"ret": 0, "sub": 0, "msg": "successfully", "data": {...}}`
- 座位数据格式特殊，需要专门解析
- 订单参数格式复杂

### 3. 业务流程
- 需要先获取影院信息才能调用其他API
- 座位选择涉及多个API调用
- 订单创建和变更是分离的API

## 📝 下一步行动

1. **立即验证**: 使用现有配置测试沃美城市API
2. **扩展适配器**: 根据HAR分析结果更新API适配器
3. **逐步适配**: 按业务流程顺序逐个适配API
4. **全面测试**: 确保完整的下单流程正常工作

## 🔗 相关文件
- HAR分析结果: `womei_har_analysis.json`
- 现有适配器: `cinema_api_adapter.py`
- 主要业务逻辑: `main_modular.py`
