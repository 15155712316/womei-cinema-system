def pay_order(order_id: str, pay_type: str = "模拟支付") -> bool:
    # 实际开发中这里会调用支付接口
    print(f"订单{order_id}已通过{pay_type}支付（模拟）")
    return True 