from typing import List

class Order:
    def __init__(self, order_id: str, account_id: str, cinema_id: str, movie_id: str, session_id: str, seats: List[str], price: float, status: str = "待支付"):
        self.order_id = order_id
        self.account_id = account_id
        self.cinema_id = cinema_id
        self.movie_id = movie_id
        self.session_id = session_id
        self.seats = seats
        self.price = price
        self.status = status 