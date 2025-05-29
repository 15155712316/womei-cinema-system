# 🎯 PyQt5核心功能实现详解 - 第二部分：券管理和座位选择

## 🎫 4. 兑换券Tab实现详解

### 4.1 兑换券界面布局
```
兑换券Tab页面：
┌─────────────────────────────────────────────────────────────┐
│ 当前账号：15155712316 @ 万友影城 (余额:¥400.0 积分:3833)    │
├─────────────────────────────────────────────────────────────┤
│ [刷新券列表]    券类型: [全部 ▼]    状态: [可用 ▼]          │
├─────────────────────────────────────────────────────────────┤
│                    可兑换券列表                              │
│ ┌─────────────┬──────────────┬────────┬─────────┬─────────┐ │
│ │   券名称    │    券码      │ 面值   │  状态   │  操作   │ │
│ ├─────────────┼──────────────┼────────┼─────────┼─────────┤ │
│ │ 10元代金券  │ A1234567890  │ ¥10.0  │ 可兑换  │ [兑换]  │ │
│ │ 5元优惠券   │ B2345678901  │ ¥5.0   │ 可兑换  │ [兑换]  │ │
│ │ 免费观影券  │ C3456789012  │ ¥35.0  │ 已兑换  │   --    │ │
│ └─────────────┴──────────────┴────────┴─────────┴─────────┘ │
├─────────────────────────────────────────────────────────────┤
│ 兑换记录：                                                   │
│ • 2024-12-29 14:30 - 兑换 10元代金券 成功                   │
│ • 2024-12-29 14:25 - 兑换 5元优惠券 成功                    │
│ • 2024-12-29 14:20 - 兑换 免费观影券 失败：积分不足         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 兑换券Tab实现代码
```python
def build_coupon_exchange_tab(self, tab):
    """构建兑换券Tab - 基于现有逻辑"""
    layout = QVBoxLayout(tab)
    
    # 账号信息显示区
    account_info_frame = QFrame()
    account_info_frame.setStyleSheet("QFrame { background-color: #f0f8ff; padding: 10px; border: 1px solid #ddd; }")
    account_info_layout = QHBoxLayout(account_info_frame)
    
    self.exchange_account_info = QLabel("当前账号：未选择")
    self.exchange_account_info.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
    account_info_layout.addWidget(self.exchange_account_info)
    layout.addWidget(account_info_frame)
    
    # 控制按钮区
    control_frame = QFrame()
    control_layout = QHBoxLayout(control_frame)
    
    refresh_btn = QPushButton("刷新券列表")
    refresh_btn.clicked.connect(self.refresh_coupon_exchange_list)
    control_layout.addWidget(refresh_btn)
    
    # 券类型筛选
    control_layout.addWidget(QLabel("券类型:"))
    self.coupon_type_combo = QComboBox()
    self.coupon_type_combo.addItems(["全部", "代金券", "优惠券", "免费券"])
    self.coupon_type_combo.currentTextChanged.connect(self.filter_exchange_coupons)
    control_layout.addWidget(self.coupon_type_combo)
    
    # 状态筛选
    control_layout.addWidget(QLabel("状态:"))
    self.coupon_status_combo = QComboBox()
    self.coupon_status_combo.addItems(["全部", "可兑换", "已兑换", "已过期"])
    self.coupon_status_combo.currentTextChanged.connect(self.filter_exchange_coupons)
    control_layout.addWidget(self.coupon_status_combo)
    
    control_layout.addStretch()
    layout.addWidget(control_frame)
    
    # 可兑换券列表表格
    self.exchange_coupon_table = QTableWidget()
    self.exchange_coupon_table.setColumnCount(5)
    self.exchange_coupon_table.setHorizontalHeaderLabels(["券名称", "券码", "面值", "状态", "操作"])
    
    # 设置列宽
    header = self.exchange_coupon_table.horizontalHeader()
    header.resizeSection(0, 150)  # 券名称
    header.resizeSection(1, 120)  # 券码
    header.resizeSection(2, 80)   # 面值
    header.resizeSection(3, 80)   # 状态
    header.resizeSection(4, 80)   # 操作
    
    layout.addWidget(self.exchange_coupon_table)
    
    # 兑换记录区
    record_frame = QFrame()
    record_layout = QVBoxLayout(record_frame)
    record_layout.addWidget(QLabel("兑换记录:"))
    
    self.exchange_record_text = QTextEdit()
    self.exchange_record_text.setMaximumHeight(100)
    self.exchange_record_text.setReadOnly(True)
    record_layout.addWidget(self.exchange_record_text)
    
    layout.addWidget(record_frame)
    
    # 初始化数据
    self.exchange_coupon_data = []

def refresh_coupon_exchange_list(self):
    """刷新可兑换券列表"""
    account = getattr(self, 'current_account', None)
    if not account:
        QMessageBox.warning(self, "未选择账号", "请先选择账号！")
        return
    
    try:
        # 这里调用积分兑换API (如果有的话)
        # 目前基于现有数据结构模拟
        self.load_exchange_coupon_data(account)
        
    except Exception as e:
        QMessageBox.critical(self, "错误", f"刷新券列表时出错：{str(e)}")

def load_exchange_coupon_data(self, account):
    """加载兑换券数据 - 基于现有积分系统"""
    # 模拟可兑换券数据 (实际应该从API获取)
    sample_coupons = [
        {
            "couponName": "10元代金券",
            "couponCode": "CASH10_" + str(int(time.time())),
            "faceValue": 10.0,
            "requiredPoints": 100,
            "status": "available",
            "couponType": "代金券"
        },
        {
            "couponName": "5元优惠券", 
            "couponCode": "DISC5_" + str(int(time.time())),
            "faceValue": 5.0,
            "requiredPoints": 50,
            "status": "available",
            "couponType": "优惠券"
        },
        {
            "couponName": "免费观影券",
            "couponCode": "FREE_" + str(int(time.time())),
            "faceValue": 35.0,
            "requiredPoints": 350,
            "status": "available", 
            "couponType": "免费券"
        }
    ]
    
    self.exchange_coupon_data = sample_coupons
    self.update_exchange_coupon_table(sample_coupons)

def update_exchange_coupon_table(self, coupons):
    """更新兑换券表格"""
    self.exchange_coupon_table.setRowCount(len(coupons))
    
    for row, coupon in enumerate(coupons):
        # 券名称
        self.exchange_coupon_table.setItem(row, 0, QTableWidgetItem(coupon['couponName']))
        
        # 券码
        self.exchange_coupon_table.setItem(row, 1, QTableWidgetItem(coupon['couponCode']))
        
        # 面值
        face_value = f"¥{coupon['faceValue']:.1f}"
        self.exchange_coupon_table.setItem(row, 2, QTableWidgetItem(face_value))
        
        # 状态
        status_text = "可兑换" if coupon['status'] == 'available' else "已兑换"
        status_item = QTableWidgetItem(status_text)
        if coupon['status'] == 'available':
            status_item.setBackground(QColor('#d4edda'))  # 绿色
        else:
            status_item.setBackground(QColor('#f8d7da'))  # 红色
        self.exchange_coupon_table.setItem(row, 3, status_item)
        
        # 操作按钮
        if coupon['status'] == 'available':
            exchange_btn = QPushButton("兑换")
            exchange_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; }")
            exchange_btn.clicked.connect(lambda checked, idx=row: self.exchange_coupon(idx))
            self.exchange_coupon_table.setCellWidget(row, 4, exchange_btn)
        else:
            disabled_label = QLabel("--")
            disabled_label.setAlignment(Qt.AlignCenter)
            self.exchange_coupon_table.setCellWidget(row, 4, disabled_label)

def exchange_coupon(self, row_index):
    """兑换券功能"""
    if row_index >= len(self.exchange_coupon_data):
        return
        
    coupon = self.exchange_coupon_data[row_index]
    account = self.current_account
    
    # 检查积分是否足够
    current_points = account.get('score', 0)
    required_points = coupon.get('requiredPoints', 0)
    
    if current_points < required_points:
        QMessageBox.warning(
            self, "积分不足", 
            f"兑换 {coupon['couponName']} 需要 {required_points} 积分，当前只有 {current_points} 积分！"
        )
        return
    
    # 确认兑换
    reply = QMessageBox.question(
        self, "确认兑换",
        f"确定要用 {required_points} 积分兑换 {coupon['couponName']} 吗？\n"
        f"兑换后积分余额：{current_points - required_points}",
        QMessageBox.Yes | QMessageBox.No
    )
    
    if reply == QMessageBox.Yes:
        self.perform_coupon_exchange(coupon, required_points)

def perform_coupon_exchange(self, coupon, required_points):
    """执行兑换操作"""
    try:
        # 这里应该调用实际的兑换API
        # 目前模拟兑换过程
        
        account = self.current_account
        
        # 更新积分
        account['score'] = account.get('score', 0) - required_points
        
        # 保存账号数据
        self.save_account_points_update(account)
        
        # 添加兑换记录
        self.add_exchange_record(coupon, True)
        
        # 更新UI
        self.update_exchange_account_info()
        coupon['status'] = 'exchanged'
        self.update_exchange_coupon_table(self.exchange_coupon_data)
        
        QMessageBox.information(
            self, "兑换成功", 
            f"成功兑换 {coupon['couponName']}！\n券码：{coupon['couponCode']}"
        )
        
    except Exception as e:
        self.add_exchange_record(coupon, False, str(e))
        QMessageBox.critical(self, "兑换失败", f"兑换时发生错误：{str(e)}")

def add_exchange_record(self, coupon, success, error_msg=""):
    """添加兑换记录"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if success:
        record = f"• {timestamp} - 兑换 {coupon['couponName']} 成功"
    else:
        record = f"• {timestamp} - 兑换 {coupon['couponName']} 失败：{error_msg}"
    
    current_text = self.exchange_record_text.toPlainText()
    new_text = record + "\n" + current_text
    self.exchange_record_text.setPlainText(new_text)
```

---

## 🎟️ 5. 绑券Tab功能实现详解

### 5.1 绑券Tab界面布局
```
绑券Tab页面：
┌─────────────────────────────────────────────────────────────┐
│ 当前账号：15155712316 @ 万友影城                            │
│ 余额：¥400.0  积分：3833                                    │
├─────────────────┬───────────────────────────────────────────┤
│ 券号输入区域     │              绑定日志                     │
│ ┌─────────────┐ │ ┌───────────────────────────────────────┐ │
│ │每行一个券号： │ │ │绑定日志：                           │ │
│ │             │ │ │                                     │ │
│ │AB1234567890 │ │ │=== 绑定完成 ===                    │ │
│ │CD2345678901 │ │ │共2张券，绑定成功1，失败1              │ │
│ │EF3456789012 │ │ │券AB1234567890 绑定成功              │ │
│ │             │ │ │券CD2345678901 绑定失败：券号无效    │ │
│ │             │ │ │                                     │ │
│ │             │ │ │*** 建议 ***                        │ │
│ │             │ │ │如果频繁失败请检查：                  │ │
│ │             │ │ │1. 券号格式是否正确                  │ │
│ │             │ │ │2. 账号Token是否有效                 │ │
│ └─────────────┘ │ └───────────────────────────────────────┘ │
│ [绑定当前账号]   │ [复制日志]                               │
└─────────────────┴───────────────────────────────────────────┘
```

### 5.2 绑券Tab实现代码
```python
def build_bind_coupon_tab(self, tab):
    """构建绑券Tab - 直接从源代码复制并适配PyQt5"""
    main_layout = QHBoxLayout(tab)
    
    # 左侧输入区
    input_frame = QFrame()
    input_layout = QVBoxLayout(input_frame)
    
    # 当前账号信息显示
    self.bind_account_info = QLabel("当前账号：未选择")
    self.bind_account_info.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
    self.bind_account_info.setStyleSheet("QLabel { color: red; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
    self.bind_account_info.setWordWrap(True)
    input_layout.addWidget(self.bind_account_info)
    
    # 提示标签
    input_layout.addWidget(QLabel("每行一个券号："))
    
    # 券号输入框
    self.coupon_text = QTextEdit()
    self.coupon_text.setFixedHeight(200)
    self.coupon_text.setPlaceholderText("请在此输入券号，每行一个\n例如：\nAB1234567890\nCD2345678901\nEF3456789012")
    input_layout.addWidget(self.coupon_text)
    
    # 绑定按钮
    bind_btn = QPushButton("绑定当前账号")
    bind_btn.setStyleSheet("""
        QPushButton {
            background-color: #4caf50;
            color: white;
            font: bold 11px "Microsoft YaHei";
            padding: 10px;
            border: none;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    bind_btn.clicked.connect(self.on_bind_coupons)
    input_layout.addWidget(bind_btn)
    
    main_layout.addWidget(input_frame)
    
    # 右侧日志区
    log_frame = QFrame()
    log_layout = QVBoxLayout(log_frame)
    
    log_layout.addWidget(QLabel("绑定日志："))
    
    self.bind_log_text = QTextEdit()
    self.bind_log_text.setReadOnly(True)
    self.bind_log_text.setStyleSheet("QTextEdit { background-color: #f8f9fa; }")
    log_layout.addWidget(self.bind_log_text)
    
    copy_log_btn = QPushButton("复制日志")
    copy_log_btn.clicked.connect(self.copy_bind_log)
    log_layout.addWidget(copy_log_btn)
    
    main_layout.addWidget(log_frame)
    
    # 设置左右区域比例
    main_layout.setStretch(0, 1)  # 左侧占1份
    main_layout.setStretch(1, 1)  # 右侧占1份

def on_bind_coupons(self):
    """绑券功能 - 直接从源代码复制核心逻辑"""
    account = getattr(self, 'current_account', None)
    if not account:
        QMessageBox.warning(self, "未选中账号", "请先在左侧账号列表选择要绑定的账号！")
        return
    
    # 验证账号信息完整性
    required_fields = ['cinemaid', 'userid', 'openid', 'token']
    for field in required_fields:
        if not account.get(field):
            QMessageBox.warning(self, "账号信息不完整", f"当前账号缺少{field}字段，请重新登录！")
            return
    
    print(f"[券绑定] 使用账号: {account.get('userid')} @ {account.get('cinemaid')}")
    print(f"[券绑定] Token: {account.get('token', '')[:10]}...")
    
    coupon_codes = self.coupon_text.toPlainText().strip().split('\n')
    coupon_codes = [c.strip() for c in coupon_codes if c.strip()]
    if not coupon_codes:
        QMessageBox.warning(self, "无券号", "请输入至少一个券号！")
        return
    
    # 添加进度提示
    QMessageBox.information(self, "开始绑定", f"即将绑定{len(coupon_codes)}张券，每张券间隔0.2秒，请稍候...")
    
    # 执行绑定
    self.perform_batch_bind(account, coupon_codes)

def perform_batch_bind(self, account, coupon_codes):
    """执行批量绑券 - 基于现有API"""
    log_lines = []
    success, fail = 0, 0
    fail_codes = []
    
    # 导入现有的绑券API
    from services.order_api import bind_coupon
    
    for i, code in enumerate(coupon_codes, 1):
        params = {
            'couponcode': code,
            'cinemaid': account['cinemaid'],
            'userid': account['userid'],
            'openid': account['openid'],
            'token': account['token'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'source': '2',
            'groupid': '',
            'cardno': account.get('cardno', '')
        }
        
        print(f"[券绑定] 正在绑定第{i}/{len(coupon_codes)}张券: {code}")
        
        try:
            res = bind_coupon(params)
            print(f"[券绑定] 券{code}绑定结果: {res}")
            
            if res.get('resultCode') == '0':
                log_lines.append(f"券{code} 绑定成功")
                success += 1
            else:
                error_desc = res.get('resultDesc', '未知错误')
                log_lines.append(f"券{code} 绑定失败：{error_desc}")
                fail += 1
                fail_codes.append(code)
                
                # 特殊处理token失效问题
                if 'TOKEN_INVALID' in error_desc:
                    log_lines.append(f"  -> Token可能已失效，建议重新登录账号")
                    
        except Exception as e:
            error_msg = str(e)
            log_lines.append(f"券{code} 绑定失败：{error_msg}")
            fail += 1
            fail_codes.append(code)
            print(f"[券绑定] 券{code}绑定异常: {e}")
        
        # 添加0.2秒延迟（除了最后一张券）
        if i < len(coupon_codes):
            print(f"[券绑定] 等待0.2秒后绑定下一张券...")
            QApplication.processEvents()  # 处理界面事件
            time.sleep(0.2)
    
    # 更新UI并显示总结
    self.update_bind_log(log_lines, success, fail, fail_codes, len(coupon_codes))

def update_bind_log(self, log_lines, success, fail, fail_codes, total):
    """更新绑定日志显示"""
    log_lines.append(f"\n=== 绑定完成 ===")
    log_lines.append(f"共{total}张券，绑定成功{success}，失败{fail}")
    if fail_codes:
        log_lines.append(f"失败券号：{', '.join(fail_codes)}")
    
    # 如果全部失败且都是TOKEN_INVALID，给出建议
    if fail == total and all('TOKEN_INVALID' in line for line in log_lines if '绑定失败' in line):
        log_lines.append(f"\n*** 建议 ***")
        log_lines.append(f"所有券都显示TOKEN_INVALID错误")
        log_lines.append(f"请尝试：")
        log_lines.append(f"1. 重新登录当前账号")
        log_lines.append(f"2. 检查账号是否在对应影院有效")
        log_lines.append(f"3. 确认券号格式是否正确")
    
    self.bind_log_text.setPlainText("\n".join(log_lines))
    
    # 完成提示
    if success > 0:
        QMessageBox.information(self, "绑定完成", f"成功绑定{success}张券，失败{fail}张券")
    else:
        QMessageBox.warning(self, "绑定失败", f"所有{fail}张券绑定失败，请检查账号状态和券号")

def copy_bind_log(self):
    """复制绑定日志"""
    log = self.bind_log_text.toPlainText().strip()
    clipboard = QApplication.clipboard()
    clipboard.setText(log)
    QMessageBox.information(self, "复制成功", "日志内容已复制到剪贴板！")

def update_bind_account_info(self):
    """更新券绑定界面的账号信息显示"""
    account = getattr(self, 'current_account', None)
    if hasattr(self, 'bind_account_info'):
        if account:
            # 获取影院名称
            cinema_name = "未知影院"
            try:
                from services.cinema_manager import cinema_manager
                cinemas = cinema_manager.load_cinema_list()
                for cinema in cinemas:
                    if cinema.get('cinemaid') == account.get('cinemaid'):
                        cinema_name = cinema.get('cinemaShortName', '未知影院')
                        break
            except:
                pass
            
            info_text = (f"当前账号：{account['userid']}\n"
                       f"影院：{cinema_name}\n"
                       f"余额：{account.get('balance', 0)}  积分：{account.get('score', 0)}")
            self.bind_account_info.setText(info_text)
            self.bind_account_info.setStyleSheet("QLabel { color: blue; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
        else:
            self.bind_account_info.setText("请先选择账号和影院")
            self.bind_account_info.setStyleSheet("QLabel { color: red; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
```

---

这是第二部分，包含了兑换券Tab和绑券Tab的详细实现。接下来我会创建第三部分，包含座位图、账号登录和账号列表的实现。 