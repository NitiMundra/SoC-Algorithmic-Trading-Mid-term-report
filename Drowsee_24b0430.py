from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self):
        self.position = 0

    def run(self, state, current_position):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth

        best_ask = sorted(order_depth.sell_orders.items())[0][0] if order_depth.sell_orders else None
        best_bid = sorted(order_depth.buy_orders.items(), reverse=True)[0][0] if order_depth.buy_orders else None

        if best_ask is None or best_bid is None:
            return {}

        # Market making: place buy near bid, sell near ask
        orders.append(Order("PRODUCT", best_bid, 5))    # Buy at bid
        orders.append(Order("PRODUCT", best_ask, -5))   # Sell at ask

        result["PRODUCT"] = orders
        return result
