# 🎯 PyQt5版本功能对接任务 - 直接复用现有代码

## 📋 任务说明
你已经完成了PyQt5的UI界面，现在需要将所有功能接口对接上。**好消息是：所有功能代码都已经完成，你只需要复制和对接，不需要重新开发！**

---

## 🚀 第一步：复制完整业务逻辑（5分钟）

### 直接复制以下目录到你的PyQt5项目：
```
从源项目复制到PyQt5项目：
├── services/          # 所有API接口和业务逻辑
├── models/            # 数据模型  
├── utils/             # 工具类（包括机器码生成）
├── data/              # 所有数据文件
├── requirements.txt   # 依赖包
├── cacert.pem         # SSL证书文件
└── .cursorrules       # 项目规则文件
```

**重要：这些文件夹的所有代码都可以直接使用，无需修改！**

---

## 🔗 第二步：在PyQt5主窗口中导入所有功能（2分钟）

在你的PyQt5主窗口文件开头添加这些导入：

```python
# 用户认证
from services.auth_service import auth_service
from services.ui_utils import MessageManager, CouponManager, UIConstants

# 所有API接口  
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

---

## 🔧 第三步：复制关键业务方法（30分钟）

### 从源项目`ui/main_window.py`复制以下方法到你的PyQt5主窗口类中：

```python
# 直接复制这些方法，不需要修改业务逻辑：
def set_current_account(self, account)
def set_main_account(self, account)  
def refresh_account_list(self)
def on_cinema_changed(self)
def on_submit_order(self, selected_seats)
def update_coupons(self, coupon_result, ticketcount=1)
def on_coupon_select(self, event)  # 注意：event参数在PyQt5中会不同
def on_bind_coupons(self)
def refresh_order_list(self)
def on_one_click_pay(self)
def show_order_detail(self, detail)
def _cancel_unpaid_orders(self, account, cinemaid)
def _get_member_info(self, account, cinemaid)
def _create_order(self, account, cinemaid, selected_seats)
def cinema_account_login_api(self, phone, openid, token, cinemaid)
```

### 复制关键数据属性到你的`__init__`方法中：

```python
def __init__(self):
    # 其他初始化代码...
    
    # 从源项目复制这些属性：
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
```

---

## 🔄 第四步：修改事件绑定（20分钟）

### 只需要修改事件绑定方式，业务逻辑保持不变：

```python
# tkinter → PyQt5 事件绑定对照表：

# 按钮点击：
# 原来：button.config(command=self.method)
# 现在：button.clicked.connect(self.method)

# 列表选择：
# 原来：listbox.bind('<<ListboxSelect>>', self.method)
# 现在：listbox.itemSelectionChanged.connect(self.method)

# 下拉框选择：
# 原来：combobox.bind('<<ComboboxSelected>>', self.method)
# 现在：combobox.currentTextChanged.connect(self.method)

# 双击事件：
# 原来：treeview.bind('<Double-1>', self.method)
# 现在：treeview.itemDoubleClicked.connect(self.method)
```

---

## ⚠️ 第五步：处理定时器和异常（10分钟）

### 定时器替换：
```python
# 原来tkinter：
self.after(1000, self.update_countdown)

# 现在PyQt5：
from PyQt5.QtCore import QTimer
self.countdown_timer = QTimer()
self.countdown_timer.timeout.connect(self.update_countdown)
self.countdown_timer.start(1000)
```

### 异常处理保持不变：
```python
# 继续使用MessageManager显示错误信息，代码不用改
MessageManager.show_error(self, "错误", "错误信息")
MessageManager.show_info(self, "成功", "成功信息")
```

---

## ✅ 第六步：验证功能（15分钟）

### 按顺序测试这些功能：
1. **启动程序** - 应该显示登录窗口
2. **登录测试** - 使用 15155712316 登录
3. **账号列表** - 应该显示账号列表
4. **影院选择** - 下拉框应该正常联动
5. **座位选择** - 座位图应该可以点击选择
6. **券功能** - 券列表应该能获取和选择
7. **下单功能** - 应该能正常提交订单

---

## 🎯 成功标准

### 如果以下功能都正常，说明对接成功：
- ✅ 用户可以正常登录（机器码验证）
- ✅ 账号列表正常显示和切换
- ✅ 影院-影片-日期-场次可以正常选择
- ✅ 座位图可以正常选择座位
- ✅ 优惠券可以正常获取和使用
- ✅ 可以正常下单和支付
- ✅ 订单列表可以正常查看

---

## 💡 关键提示

1. **不要重新开发功能** - 所有功能代码都已经完成，直接复制使用
2. **只改事件绑定** - 业务逻辑代码完全不用改，只需要改事件绑定方式
3. **保持API调用不变** - 所有API调用参数和处理逻辑都保持原样
4. **遇到问题先检查导入** - 确保所有需要的模块都已正确导入

### 预计总耗时：约90分钟

**记住：你的任务不是重新开发功能，而是将已有的成熟功能连接到PyQt5界面上！** 