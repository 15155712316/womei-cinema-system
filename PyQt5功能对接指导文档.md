# 🔧 PyQt5版本功能对接指导文档

## 📋 项目现状说明
- **源项目**: tkinter版本 - 所有功能接口已完成，运行正常
- **目标项目**: PyQt5版本 - UI界面已完成，功能接口需要对接
- **任务目标**: 将源项目的所有业务逻辑、API接口、数据处理完整迁移到PyQt5版本

---

## 🎯 对接策略：直接复用 + 最小修改原则

### 核心原则
1. **业务逻辑层完全复用** - services/、models/、utils/ 目录内容直接复制
2. **数据层完全复用** - data/ 目录内容直接复制  
3. **API接口层完全复用** - 所有API调用逻辑保持不变
4. **只修改UI层** - 仅将tkinter事件绑定改为PyQt5信号槽

---

## 📂 文件复制清单

### 第一步：直接复制业务逻辑层
```bash
# 从源项目复制以下完整目录到PyQt5项目：
源项目/services/     → PyQt5项目/services/     # 所有业务逻辑
源项目/models/       → PyQt5项目/models/       # 数据模型  
源项目/utils/        → PyQt5项目/utils/        # 工具类
源项目/data/         → PyQt5项目/data/         # 数据文件
源项目/requirements.txt → PyQt5项目/requirements.txt # 依赖包
```

### 第二步：复制核心配置文件
```bash
# 配置和资源文件
源项目/README.md     → PyQt5项目/README.md
源项目/使用说明.md    → PyQt5项目/使用说明.md  
源项目/.cursorrules   → PyQt5项目/.cursorrules
源项目/cacert.pem     → PyQt5项目/cacert.pem
```

---

## 🔌 功能对接映射表

### 1. 用户认证功能
**源文件**: `services/auth_service.py`
**功能**: 机器码生成、API登录验证、权限检查
**PyQt5对接点**: 登录对话框 + 主窗口认证检查

```python
# 需要对接的关键函数：
from services.auth_service import auth_service

# 在PyQt5登录对话框中调用：
is_valid, message, user_info = auth_service.authenticate(phone, machine_code)

# 在PyQt5主窗口中调用：
is_valid, message, user_info = auth_service.check_auth()
```

### 2. 账号管理功能  
**源文件**: `ui/account_list_panel.py` + `services/account_api.py`
**功能**: 账号列表、主账号标记、账号切换
**PyQt5对接点**: 左栏账号列表区

```python
# 需要对接的关键函数：
- self.set_current_account(account)      # 设置当前账号
- self.set_main_account(account)         # 设置主账号  
- self.refresh_account_list()            # 刷新账号列表
- self.save_cinema_account(account_data) # 保存账号数据
```

### 3. 影院选择功能
**源文件**: `ui/cinema_select_panel.py` + `services/cinema_manager.py`
**功能**: 影院-影片-日期-场次四级联动
**PyQt5对接点**: 中栏Tab1左侧影院选择区

```python
# 需要对接的关键函数：
- self.on_cinema_changed()               # 影院切换事件
- self.load_movies()                     # 加载影片列表
- self.load_dates()                      # 加载日期列表  
- self.load_sessions()                   # 加载场次列表
- self.get_selected_cinemaid()           # 获取选中影院ID
```

### 4. 座位选择功能
**源文件**: `ui/seat_map_panel.py` + `services/film_service.py`
**功能**: 座位图绘制、座位选择、价格计算
**PyQt5对接点**: 中栏下部座位区域

```python
# 需要对接的关键函数：
- self.load_seat_map(session_data)       # 加载座位图数据
- self.on_seat_clicked(row, col)         # 座位点击事件
- self.calculate_total_price()           # 计算总价格
- self.get_selected_seats()              # 获取已选座位
```

### 5. 优惠券管理功能
**源文件**: `services/order_api.py` 中的券相关函数
**功能**: 券列表获取、券选择、券绑定
**PyQt5对接点**: 中栏Tab1右侧券列表区 + Tab2绑券页面

```python
# 需要对接的关键函数：
- get_coupons_by_order(params)           # 获取可用券列表
- bind_coupon(params)                    # 绑定优惠券
- self.update_coupons(coupon_result)     # 更新券列表显示
- self.on_coupon_select(event)           # 券选择事件
- self.on_bind_coupons()                 # 批量绑券功能
```

### 6. 订单处理功能
**源文件**: `services/order_api.py` 主要订单函数
**功能**: 创建订单、支付订单、订单查询、订单取消
**PyQt5对接点**: 提交订单按钮 + Tab4订单页面 + 右栏订单详情区

```python
# 需要对接的关键函数：
- create_order(params)                   # 创建订单
- pay_order(params)                      # 支付订单
- get_order_list(params)                 # 获取订单列表
- get_order_detail(params)               # 获取订单详情
- cancel_all_unpaid_orders(params)       # 取消未支付订单
- get_order_qrcode_api(params)           # 获取订单二维码
- self.on_submit_order(selected_seats)   # 提交订单处理
- self.on_one_click_pay()                # 一键支付处理
```

---

## 🔄 事件绑定转换指南

### tkinter事件 → PyQt5信号槽映射

#### 1. 按钮点击事件
```python
# tkinter版本：
button.config(command=self.on_click)

# PyQt5版本：
button.clicked.connect(self.on_click)
```

#### 2. 列表选择事件
```python
# tkinter版本：
listbox.bind('<<ListboxSelect>>', self.on_select)

# PyQt5版本：
listbox.itemSelectionChanged.connect(self.on_select)
```

#### 3. 下拉框选择事件
```python
# tkinter版本：
combobox.bind('<<ComboboxSelected>>', self.on_combo_change)

# PyQt5版本：
combobox.currentTextChanged.connect(self.on_combo_change)
```

#### 4. 双击事件
```python
# tkinter版本：
treeview.bind('<Double-1>', self.on_double_click)

# PyQt5版本：
treeview.itemDoubleClicked.connect(self.on_double_click)
```

#### 5. 右键菜单事件
```python
# tkinter版本：
widget.bind('<Button-3>', self.show_context_menu)

# PyQt5版本：
widget.setContextMenuPolicy(Qt.CustomContextMenu)
widget.customContextMenuRequested.connect(self.show_context_menu)
```

---

## 🔧 具体对接实现步骤

### 步骤1：导入所有业务逻辑模块
在PyQt5主窗口文件开头添加：
```python
# 用户认证相关
from services.auth_service import auth_service
from services.ui_utils import MessageManager, CouponManager, UIConstants

# API接口相关  
from services.order_api import (
    create_order, get_unpaid_order_detail, get_coupons_by_order, 
    bind_coupon, get_order_list, get_order_detail, get_order_qrcode_api,
    cancel_all_unpaid_orders, get_coupon_prepay_info, pay_order
)

# 影院和账号管理
from services.cinema_manager import cinema_manager
from services.film_service import FilmService
from services.member_service import MemberService

# 工具类
from utils.machine_code import get_machine_code
import json, os, time, traceback
```

### 步骤2：复制核心业务方法
将tkinter版本的以下关键方法直接复制到PyQt5版本：

```python
# 从 ui/main_window.py 复制的核心方法：
def set_current_account(self, account)           # 设置当前账号
def set_main_account(self, account)              # 设置主账号
def refresh_account_list(self)                   # 刷新账号列表  
def on_cinema_changed(self)                      # 影院切换处理
def on_submit_order(self, selected_seats)        # 订单提交处理
def update_coupons(self, coupon_result, ticketcount=1)  # 更新券列表
def on_coupon_select(self, event)                # 券选择处理
def on_bind_coupons(self)                        # 券绑定处理
def refresh_order_list(self)                     # 刷新订单列表
def on_one_click_pay(self)                       # 一键支付处理
def show_order_detail(self, detail)              # 显示订单详情

# 从对应组件复制的方法：
def _cancel_unpaid_orders(self, account, cinemaid)      # 取消未支付订单
def _get_member_info(self, account, cinemaid)           # 获取会员信息
def _create_order(self, account, cinemaid, selected_seats)  # 创建订单
def cinema_account_login_api(self, phone, openid, token, cinemaid)  # 账号登录API
```

### 步骤3：修改事件绑定方式
只需要修改事件绑定部分，业务逻辑保持不变：

```python
# 示例：账号列表选择事件
def setup_account_list_events(self):
    # 原tkinter版本的事件绑定逻辑保持不变，只修改绑定方式
    self.account_tree.itemSelectionChanged.connect(self.on_account_selected)

def on_account_selected(self):
    # 这里的处理逻辑完全复制tkinter版本的实现
    selected_items = self.account_tree.selectedItems()
    if selected_items:
        # 原有的账号选择处理逻辑...
        account = self.get_account_from_selection(selected_items[0])
        self.set_current_account(account)  # 直接调用原有方法
```

---

## 📊 数据流保持一致

### 关键数据属性复制
确保PyQt5版本包含以下关键属性：
```python
class MainWindow:
    def __init__(self):
        # 从tkinter版本复制的核心属性
        self.current_user = None
        self.current_account = None
        self.current_order = None
        self.member_info = None
        self.selected_coupons = []
        self.selected_coupons_info = None
        self.current_coupon_info = None
        self.coupons_data = []
        self.max_coupon_select = 1
        self.ui_state = "initial"
        self.show_debug = False
        self.last_priceinfo = {}
        
        # 定时器相关（使用QTimer替代tkinter.after）
        self.auth_check_timer = None
        self.countdown_timer = None
```

### API配置保持一致
确保使用相同的API配置：
```python
# 从源项目复制API配置
API_BASE_URL = "http://43.142.19.28:5000"
SSL_VERIFY = False  # 禁用SSL验证
API_TIMEOUT = 30    # 请求超时时间
```

---

## ⚠️ 对接过程中的注意事项

### 1. 异常处理保持一致
```python
# 保持与tkinter版本相同的异常处理方式
try:
    result = api_call(params)
    if result.get('resultCode') == '0':
        # 成功处理逻辑
        pass
    else:
        # 错误处理逻辑
        MessageManager.show_error(self, "错误", result.get('resultDesc', '未知错误'))
except Exception as e:
    # 异常处理逻辑
    MessageManager.show_error(self, "异常", str(e))
```

### 2. 定时器替换
```python
# tkinter版本：
self.after(1000, self.update_countdown)

# PyQt5版本：
self.countdown_timer = QTimer()
self.countdown_timer.timeout.connect(self.update_countdown)
self.countdown_timer.start(1000)
```

### 3. 线程安全处理
```python
# 对于API调用，如果需要后台处理，使用QThread
from PyQt5.QtCore import QThread, pyqtSignal

class ApiWorker(QThread):
    result_ready = pyqtSignal(object)
    
    def run(self):
        try:
            result = api_call(self.params)
            self.result_ready.emit(result)
        except Exception as e:
            self.result_ready.emit({'error': str(e)})
```

---

## 🚀 快速验证检查清单

### 功能验证清单
- [ ] **用户认证**: 登录、权限检查、机器码验证
- [ ] **账号管理**: 账号列表、主账号设置、账号切换
- [ ] **影院选择**: 四级联动下拉选择
- [ ] **座位选择**: 座位图显示、座位选择、价格计算  
- [ ] **优惠券**: 券列表获取、券选择、券绑定
- [ ] **订单流程**: 订单创建、订单支付、订单查询
- [ ] **数据持久化**: 账号数据、配置数据保存
- [ ] **错误处理**: API异常、网络异常、数据异常

### API接口验证清单
- [ ] `auth_service.authenticate()` - 用户登录认证
- [ ] `create_order()` - 创建订单API
- [ ] `pay_order()` - 支付订单API  
- [ ] `get_coupons_by_order()` - 获取券列表API
- [ ] `bind_coupon()` - 绑定优惠券API
- [ ] `get_order_list()` - 获取订单列表API
- [ ] `get_order_detail()` - 获取订单详情API
- [ ] `cancel_all_unpaid_orders()` - 取消订单API

---

## 📞 对接完成验证方法

### 完整功能测试流程
1. **启动测试**: 程序正常启动，显示登录窗口
2. **登录测试**: 使用测试账号 15155712316 成功登录
3. **账号测试**: 账号列表正常显示，账号切换正常
4. **影院测试**: 影院-影片-日期-场次联动正常
5. **座位测试**: 座位图正常显示，座位选择和价格计算正确
6. **券功能测试**: 券列表正常获取，券绑定功能正常
7. **订单测试**: 完整下单流程正常，支付功能正常
8. **数据测试**: 所有数据保存和读取正常

### 验证成功标准
- ✅ 所有原有功能在PyQt5版本中完全可用
- ✅ API调用返回结果与原版本一致
- ✅ 数据处理逻辑与原版本一致  
- ✅ 错误处理行为与原版本一致
- ✅ 用户体验流程与原版本一致（除UI框架差异外）

---

## 🎯 总结：对接成功的关键

1. **复用至上**: 最大程度复用现有的成熟代码
2. **最小修改**: 只修改UI层事件绑定，业务逻辑保持不变  
3. **保持一致**: API调用、数据处理、异常处理都保持与原版本一致
4. **逐步验证**: 每对接一个功能模块就进行验证测试
5. **完整测试**: 对接完成后进行完整的端到端功能测试

**记住：您的目标是让PyQt5版本具有与tkinter版本完全相同的功能，只是界面框架不同！** 