from src.backtester import Order, OrderBook
from typing import List
import numpy as np
import pandas as pd


class Trader:
    def __init__(self):
        self.price_history = []
        self.bb_width_history = []
        self.entry_price = None
        self.position = 0
        self.lookback = 20

    def run(self, state, current_position):
        result = {}

        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth
        best_ask = sorted(order_depth.sell_orders.items())[0][0] if order_depth.sell_orders else None
        best_bid = sorted(order_depth.buy_orders.items(), reverse=True)[0][0] if order_depth.buy_orders else None

        if best_ask is not None and best_bid is not None:
            mid_price = (best_ask + best_bid) / 2
            self.price_history.append(mid_price)
        period = 20
        if len(self.price_history) > period:
            self.price_history.pop(0)

        # define SMA and calculate bollinger bands:

        def calculate_bollinger_bands():
            mean = np.mean(self.price_history)
            std = np.std(self.price_history)
            upper_band = mean + 2 * std
            lower_band = mean - 2 * std
            BB_width = upper_band - lower_band
            return BB_width



        # Determining Volataility

        VOL_WINDOW = 100
        BB_Width = calculate_bollinger_bands()
        self.bb_width_history.append(BB_Width)
        if len(self.bb_width_history) > VOL_WINDOW:
            self.bb_width_history.pop(0)
        if len(self.bb_width_history) == VOL_WINDOW:
            BB_Width_Median = pd.Series(self.bb_width_history).median()
            if BB_Width < BB_Width_Median:
                volatility = "LOW_VOLATILITY"  # Market making
            else:
                volatility = "HIGH_VOLATILITY"  # Breakout

            if volatility == "LOW_VOLATILITY":

                orders.append(Order("PRODUCT", best_bid, 50))  # Buy at bid
                orders.append(Order("PRODUCT", best_ask, -50))  # Sell at ask

            if volatility == "HIGH_VOLATILITY":
                if len(self.price_history) == self.lookback:
                    recent_high = max(self.price_history)
                    recent_low = min(self.price_history)
                if self.position == 0:
                    if mid_price > recent_high:
                        self.position = 1
                        orders.append(Order("PRODUCT", best_ask, 10))  # Enter Long
                    elif mid_price < recent_low:
                        self.position = -1
                        orders.append(Order("PRODUCT", best_bid, -10))  # Enter Short

                    # Exit logic for both long and short
                elif self.position == 1 and mid_price < recent_low:
                    orders.append(Order("PRODUCT", best_bid, -5))  # Exit Long
                    self.position = 0

                elif self.position == -1 and mid_price > recent_high:
                    orders.append(Order("PRODUCT", best_ask, 5))  # Exit Short
                    self.position = 0
        result["PRODUCT"] = orders
        return result