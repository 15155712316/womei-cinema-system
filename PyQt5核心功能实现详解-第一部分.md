# 🎯 PyQt5核心功能实现详解 - 第一部分：影院管理和订单管理

## 📋 说明
本文档详细说明PyQt5版本中7个核心功能的实现方式，基于现有接口代码，提供完整的实现逻辑。

---

## 🏢 1. 影院管理功能 - 添加影院实现过程

### 界面布局
```
影院Tab页面布局：
┌─────────────────────────────────────────────────────────────┐
│ [刷新列表]  [添加影院]  [删除影院]  [编辑影院]  [复制ID]     │
├─────────────────────────────────────────────────────────────┤
│                    影院列表表格                              │
│ ┌─────────┬──────────────┬──────────────┬─────────────────┐ │
│ │ 影院名称 │    域名      │   影院ID     │      状态       │ │
│ ├─────────┼──────────────┼──────────────┼─────────────────┤ │
│ │万友影城  │api.xxx.com   │11b7e4bcc265 │ ✅ 可用         │ │
│ │星辰影院  │cinema.yyy.com│0f1e21d86ac8 │ ⚠️ 检测中       │ │
│ └─────────┴──────────────┴──────────────┴─────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 添加影院核心实现

#### 1.1 添加影院对话框实现
```python
def add_cinema(self):
    """添加影院功能 - 直接从源代码复制"""
    # 创建添加影院对话框
    add_dialog = QDialog(self)
    add_dialog.setWindowTitle("添加影院")
    add_dialog.setFixedSize(400, 300)
    
    # 对话框布局
    layout = QVBoxLayout(add_dialog)
    
    # 影院名称输入
    name_layout = QHBoxLayout()
    name_layout.addWidget(QLabel("影院名称:"))
    name_input = QLineEdit()
    name_input.setPlaceholderText("例如：万友影城")
    name_layout.addWidget(name_input)
    layout.addLayout(name_layout)
    
    # 域名输入
    domain_layout = QHBoxLayout()
    domain_layout.addWidget(QLabel("API域名:"))
    domain_input = QLineEdit()
    domain_input.setPlaceholderText("例如：api.cinema.com")
    domain_layout.addWidget(domain_input)
    layout.addLayout(domain_layout)
    
    # 影院ID输入
    id_layout = QHBoxLayout()
    id_layout.addWidget(QLabel("影院ID:"))
    id_input = QLineEdit()
    id_input.setPlaceholderText("例如：11b7e4bcc265")
    id_layout.addWidget(id_input)
    layout.addLayout(id_layout)
    
    # 按钮
    button_layout = QHBoxLayout()
    confirm_btn = QPushButton("确认添加")
    cancel_btn = QPushButton("取消")
    button_layout.addWidget(confirm_btn)
    button_layout.addWidget(cancel_btn)
    layout.addLayout(button_layout)
    
    # 事件绑定
    def validate_and_add():
        name = name_input.text().strip()
        domain = domain_input.text().strip()
        cinema_id = id_input.text().strip()
        
        # 验证输入
        if not all([name, domain, cinema_id]):
            QMessageBox.warning(add_dialog, "输入错误", "请填写完整的影院信息！")
            return
            
        # 验证域名格式
        if not domain.startswith(('http://', 'https://')):
            domain = f"https://{domain}"
            
        # 验证影院ID格式
        if len(cinema_id) != 12:
            QMessageBox.warning(add_dialog, "格式错误", "影院ID必须是12位字符！")
            return
            
        # 添加到影院列表
        self.add_cinema_to_list(name, domain, cinema_id)
        add_dialog.accept()
    
    confirm_btn.clicked.connect(validate_and_add)
    cancel_btn.clicked.connect(add_dialog.reject)
    
    add_dialog.exec_()
```

#### 1.2 影院数据保存逻辑
```python
def add_cinema_to_list(self, name, domain, cinema_id):
    """添加影院到数据文件 - 基于现有cinema_manager"""
    try:
        # 使用现有的cinema_manager
        from services.cinema_manager import cinema_manager
        
        # 新影院数据
        new_cinema = {
            "cinemaShortName": name,
            "domain": domain,
            "cinemaid": cinema_id,
            "status": "active",
            "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 加载现有影院列表
        cinemas = cinema_manager.load_cinema_list()
        
        # 检查是否已存在
        for cinema in cinemas:
            if cinema.get('cinemaid') == cinema_id:
                QMessageBox.warning(self, "添加失败", f"影院ID {cinema_id} 已存在！")
                return False
        
        # 添加新影院
        cinemas.append(new_cinema)
        
        # 保存到文件
        cinema_manager.save_cinema_list(cinemas)
        
        # 刷新界面
        self.refresh_cinema_list()
        
        QMessageBox.information(self, "添加成功", f"影院 {name} 已成功添加！")
        return True
        
    except Exception as e:
        QMessageBox.critical(self, "添加失败", f"添加影院时发生错误：{str(e)}")
        return False
```

---

## 🗑️ 2. 删除影院实现过程

### 删除影院核心实现
```python
def delete_cinema(self):
    """删除选中的影院 - 基于现有逻辑"""
    # 获取选中的影院
    selected_items = self.cinema_table.selectedItems()
    if not selected_items:
        QMessageBox.warning(self, "未选择影院", "请先选择要删除的影院！")
        return
    
    # 获取选中行的影院ID
    row = self.cinema_table.currentRow()
    if row < 0:
        return
        
    cinema_id_item = self.cinema_table.item(row, 2)  # 影院ID在第2列
    cinema_name_item = self.cinema_table.item(row, 0)  # 影院名称在第0列
    
    if not cinema_id_item or not cinema_name_item:
        return
        
    cinema_id = cinema_id_item.text()
    cinema_name = cinema_name_item.text()
    
    # 确认删除
    reply = QMessageBox.question(
        self, "确认删除", 
        f"确定要删除影院 {cinema_name} ({cinema_id}) 吗？\n\n注意：删除后该影院的所有账号也将失效！",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        self.delete_cinema_from_list(cinema_id, cinema_name)

def delete_cinema_from_list(self, cinema_id, cinema_name):
    """从数据文件中删除影院"""
    try:
        from services.cinema_manager import cinema_manager
        
        # 加载影院列表
        cinemas = cinema_manager.load_cinema_list()
        
        # 查找并删除影院
        original_count = len(cinemas)
        cinemas = [c for c in cinemas if c.get('cinemaid') != cinema_id]
        
        if len(cinemas) == original_count:
            QMessageBox.warning(self, "删除失败", f"未找到影院ID {cinema_id}！")
            return False
        
        # 保存更新后的列表
        cinema_manager.save_cinema_list(cinemas)
        
        # 同时清理该影院的账号数据
        self.cleanup_cinema_accounts(cinema_id)
        
        # 刷新界面
        self.refresh_cinema_list()
        self.refresh_account_list()  # 刷新账号列表
        
        QMessageBox.information(self, "删除成功", f"影院 {cinema_name} 已删除！")
        return True
        
    except Exception as e:
        QMessageBox.critical(self, "删除失败", f"删除影院时发生错误：{str(e)}")
        return False

def cleanup_cinema_accounts(self, cinema_id):
    """清理删除影院的相关账号"""
    try:
        with open("data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        
        # 过滤掉该影院的账号
        filtered_accounts = [acc for acc in accounts if acc.get('cinemaid') != cinema_id]
        
        with open("data/accounts.json", "w", encoding="utf-8") as f:
            json.dump(filtered_accounts, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"清理账号数据时出错: {e}")
```

---

## 📋 3. 订单Tab - 订单列表功能实现

### 3.1 订单列表界面布局
```
订单Tab页面：
┌─────────────────────────────────────────────────────────────┐
│ [刷新订单]  [取消选中订单]                                   │
├─────────────────────────────────────────────────────────────┤
│                     订单列表表格                             │
│ ┌────────────┬─────────┬─────────┬──────────────────────────┐ │
│ │   影片名   │  影院   │  状态   │         订单号           │ │
│ ├────────────┼─────────┼─────────┼──────────────────────────┤ │
│ │ 独一无二   │万友影城 │ 待支付  │ 20241229001234567890     │ │
│ │ 海王2      │星辰影院 │ 已支付  │ 20241228001234567891     │ │
│ │ 阿凡达3    │万友影城 │ 已取票  │ 20241227001234567892     │ │
│ └────────────┴─────────┴─────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 订单列表实现逻辑
```python
def build_order_list_tab(self, tab):
    """构建订单列表Tab - 基于现有实现"""
    layout = QVBoxLayout(tab)
    
    # 顶部按钮区
    top_frame = QFrame()
    top_layout = QHBoxLayout(top_frame)
    
    refresh_btn = QPushButton("刷新订单")
    refresh_btn.setFixedWidth(100)
    refresh_btn.clicked.connect(self.refresh_order_list)
    top_layout.addWidget(refresh_btn)
    
    cancel_btn = QPushButton("取消选中订单")
    cancel_btn.setFixedWidth(120)
    cancel_btn.clicked.connect(self.cancel_selected_order)
    top_layout.addWidget(cancel_btn)
    
    top_layout.addStretch()  # 左对齐
    layout.addWidget(top_frame)
    
    # 订单表格
    self.order_table = QTableWidget()
    self.order_table.setColumnCount(4)
    self.order_table.setHorizontalHeaderLabels(["影片", "影院", "状态", "订单号"])
    
    # 设置列宽
    header = self.order_table.horizontalHeader()
    header.resizeSection(0, 150)  # 影片
    header.resizeSection(1, 180)  # 影院
    header.resizeSection(2, 100)  # 状态
    header.resizeSection(3, 200)  # 订单号
    
    # 设置表格属性
    self.order_table.setSelectionBehavior(QAbstractItemView.SelectRows)
    self.order_table.setAlternatingRowColors(True)
    self.order_table.setSortingEnabled(True)
    
    # 事件绑定
    self.order_table.itemDoubleClicked.connect(self.on_order_double_click)
    self.order_table.setContextMenuPolicy(Qt.CustomContextMenu)
    self.order_table.customContextMenuRequested.connect(self.show_order_context_menu)
    
    layout.addWidget(self.order_table)
    
    # 订单数据缓存
    self.order_data_cache = []

def refresh_order_list(self):
    """刷新订单列表 - 调用现有API"""
    account = getattr(self, 'current_account', None)
    if not account:
        QMessageBox.warning(self, "未选择账号", "请先选择账号！")
        return
    
    cinemaid = self.get_selected_cinemaid()
    if not cinemaid:
        QMessageBox.warning(self, "未选择影院", "请先选择影院！")
        return
    
    try:
        # 调用现有的订单API
        from services.order_api import get_order_list
        
        params = {
            'userid': account['userid'],
            'token': account['token'], 
            'openid': account['openid'],
            'cinemaid': cinemaid,
            'pageIndex': 1,
            'pageSize': 50
        }
        
        result = get_order_list(params)
        
        if result.get('resultCode') == '0':
            orders = result.get('data', {}).get('orderList', [])
            self.update_order_table(orders)
        else:
            QMessageBox.warning(self, "获取失败", result.get('resultDesc', '获取订单列表失败'))
            
    except Exception as e:
        QMessageBox.critical(self, "错误", f"刷新订单列表时出错：{str(e)}")

def update_order_table(self, orders):
    """刷新订单表格显示"""
    self.order_table.setRowCount(len(orders))
    self.order_data_cache = orders
    
    for row, order in enumerate(orders):
        # 影片名称
        movie_name = order.get('movieName', '未知影片')
        self.order_table.setItem(row, 0, QTableWidgetItem(movie_name))
        
        # 影院名称
        cinema_name = order.get('cinemaName', '未知影院')
        self.order_table.setItem(row, 1, QTableWidgetItem(cinema_name))
        
        # 订单状态
        status = self.get_order_status_text(order.get('orderStatus', 0))
        status_item = QTableWidgetItem(status)
        
        # 根据状态设置颜色
        if '待支付' in status:
            status_item.setBackground(QColor('#fff3cd'))  # 黄色背景
        elif '已支付' in status:
            status_item.setBackground(QColor('#d4edda'))  # 绿色背景
        elif '已取票' in status:
            status_item.setBackground(QColor('#d1ecf1'))  # 蓝色背景
        elif '已取消' in status:
            status_item.setBackground(QColor('#f8d7da'))  # 红色背景
            
        self.order_table.setItem(row, 2, status_item)
        
        # 订单号
        order_no = order.get('orderNo', '无订单号')
        self.order_table.setItem(row, 3, QTableWidgetItem(order_no))

def get_order_status_text(self, status_code):
    """转换订单状态码为中文"""
    status_map = {
        0: "待支付",
        1: "已支付", 
        2: "已取票",
        3: "已取消",
        4: "已退款",
        5: "支付失败"
    }
    return status_map.get(status_code, "未知状态")
```

### 3.3 订单右键菜单功能
```python
def show_order_context_menu(self, position):
    """显示订单右键菜单"""
    if self.order_table.itemAt(position) is None:
        return
        
    menu = QMenu(self)
    
    view_action = menu.addAction("查看详情")
    cancel_action = menu.addAction("取消订单")
    copy_action = menu.addAction("复制订单号")
    
    action = menu.exec_(self.order_table.mapToGlobal(position))
    
    if action == view_action:
        self.view_order_detail()
    elif action == cancel_action:
        self.cancel_selected_order()
    elif action == copy_action:
        self.copy_order_number()

def view_order_detail(self):
    """查看订单详情"""
    row = self.order_table.currentRow()
    if row < 0 or row >= len(self.order_data_cache):
        return
        
    order = self.order_data_cache[row]
    order_no = order.get('orderNo')
    
    if order_no:
        # 调用现有的订单详情查询
        self.get_and_show_order_detail(order_no)

def get_and_show_order_detail(self, order_no):
    """获取并显示订单详情"""
    try:
        from services.order_api import get_order_detail
        
        account = self.current_account
        params = {
            'userid': account['userid'],
            'token': account['token'],
            'openid': account['openid'], 
            'cinemaid': account['cinemaid'],
            'orderNo': order_no
        }
        
        result = get_order_detail(params)
        
        if result.get('resultCode') == '0':
            detail = result.get('data')
            self.show_order_detail(detail)  # 调用现有的显示方法
        else:
            QMessageBox.warning(self, "获取失败", result.get('resultDesc', '获取订单详情失败'))
            
    except Exception as e:
        QMessageBox.critical(self, "错误", f"获取订单详情时出错：{str(e)}")
```

---

这是第一部分，包含了影院管理和订单管理的详细实现。接下来我会创建第二部分，包含兑换券、绑券、座位图等功能的实现。 