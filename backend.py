# backend.py

class TradingGame:
    def __init__(self):
        self.cash = 10000  # Starting cash
        self.portfolio = {}  # Dictionary to hold stocks and their quantities
        self.stock_prices = {
            "AAPL": 150.00,
            "GOOGL": 2800.00,
            "TSLA": 700.00
        }

    def buy_stock(self, stock, quantity=1):
        if stock in self.stock_prices:
            total_cost = self.stock_prices[stock] * quantity
            if self.cash >= total_cost:
                self.cash -= total_cost
                if stock in self.portfolio:
                    self.portfolio[stock] += quantity
                else:
                    self.portfolio[stock] = quantity
            else:
                print("Not enough cash to buy the stock")
        else:
            print("Stock not found")

    def sell_stock(self, stock, quantity=1):
        if stock in self.portfolio and self.portfolio[stock] >= quantity:
            total_value = self.stock_prices[stock] * quantity
            self.cash += total_value
            self.portfolio[stock] -= quantity
            if self.portfolio[stock] == 0:
                del self.portfolio[stock]
        else:
            print("Not enough stock to sell or stock not found")

    def get_cash(self):
        return self.cash

    def get_portfolio(self):
        return self.portfolio

    def get_stock_prices(self):
        return self.stock_prices
