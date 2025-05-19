from typing import Optional

class Account:
    def __init__(self, account_id: str, password: str, balance: float = 0.0, points: int = 0):
        self.account_id = account_id
        self.password = password
        self.balance = balance
        self.points = points 