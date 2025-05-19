from models.order import Order
from typing import List
import uuid

def create_order(account_id: str, cinema_id: str, movie_id: str, session_id: str, seats: List[str], price: float) -> Order:
    order_id = str(uuid.uuid4())
    return Order(order_id, account_id, cinema_id, movie_id, session_id, seats, price) 