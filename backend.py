from datetime import datetime
import numpy as np
import pandas as pd

# Define the custom dtype for the structured array
dtype = np.dtype([
    ('datetime', 'datetime64[m]'),
    ('open', 'f4'),
    ('high', 'f4'),
    ('low', 'f4'),
    ('close', 'f4')
])

# Read the CSV file
df_eurusd = pd.read_csv('./Data/eurusd_2021to2024.csv')

# Convert the datetime column to datetime64
df_eurusd['datetime'] = pd.to_datetime(df_eurusd['datetime'])

# Create the structured array
data_eurusd = np.zeros(len(df_eurusd), dtype=dtype)

# Fill the structured array with data from the dataframe
data_eurusd['datetime'] = df_eurusd['datetime'].values.astype('datetime64[m]')
data_eurusd['open'] = df_eurusd['open'].values
data_eurusd['high'] = df_eurusd['high'].values
data_eurusd['low'] = df_eurusd['low'].values
data_eurusd['close'] = df_eurusd['close'].values

# Read the CSV file
df_btcusd = pd.read_csv('./Data/btcusd_2022to2024.csv')

# Convert the datetime column to datetime64
df_btcusd['datetime'] = pd.to_datetime(df_btcusd['datetime'])

# Create the structured array
data_btcusd = np.zeros(len(df_btcusd), dtype=dtype)

# Fill the structured array with data from the dataframe
data_btcusd['datetime'] = df_btcusd['datetime'].values.astype('datetime64[m]')
data_btcusd['open'] = df_btcusd['open'].values
data_btcusd['high'] = df_btcusd['high'].values
data_btcusd['low'] = df_btcusd['low'].values
data_btcusd['close'] = df_btcusd['close'].values

"""
Klasse für Positionen, soll bei jedem kauf geöffnet werden und bei jedem verkauf geschlossen
"""

class Position:
    def __init__(self, ticker, quantity, price, leverage, margin, type) -> None:
        self.ticker = ticker
        self.quantity = quantity
        self.price_whenopened = price
        self.price = price
        self.total_whenopened = self.quantity * self.price
        self.total = self.quantity * self.price
        self.leverage = leverage
        self.margin = margin
        self.pnl = 0
        self.type = type

    def add_quantity(self, quantity_to_add, margin_to_add, price):
        self.quantity = self.quantity + quantity_to_add
        self.total_whenopened += quantity_to_add * price
        self.total += quantity_to_add * price
        self.margin += margin_to_add
        self.leverage = self.total_whenopened / self.margin
    
    def remove_quantity(self, quantity_to_remove):
        percentage = quantity_to_remove / self.quantity
        self.quantity = self.quantity - quantity_to_remove
        self.total_whenopened = self.quantity * self.price_whenopened
        self.total = self.quantity * self.price
        self.margin = self.margin * (1-percentage)
        self.pnl = self.total - self.total_whenopened
        
    def update_price(self, new_price):
        self.price = new_price
        self.total = self.quantity * self.price
        self.pnl = self.total - self.total_whenopened
        
    
    def close(self):
        self = None
        
from typing import List

"""
Klasse die das Kapital und die Positionen eines Users speichert und verwaltet
"""

class User:
    def __init__(self, name, cash):
        self.name = name
        self.cash = cash                # Starting cash
        self.capital_invested = 0
        self.capital = self.cash + self.capital_invested
        self.positions = {}
        self.current_prices = {}
        
    def buy_stock(self, ticker, margin, price, leverage, type):
        quantity = (margin*leverage)/price
        if margin <= self.cash:
            self.capital_invested += margin
            self.cash -= margin
            self.capital = self.cash + self.capital_invested
            if ticker in self.positions.keys():
                position = self.positions[ticker] 
                position.add_quantity(quantity, margin, price)
            else:
                self.positions[ticker] = Position(ticker, quantity, price, leverage, margin, type)
            print(f"{self.name} bought Stock {ticker} for {margin}$ with Leverage: {leverage} at {price}")

        else:
            print("Not enough cash")

    def sell_stock(self, position:Position, quantity):
        if position.quantity == quantity:
            self.capital_invested -= position.margin + position.pnl
            self.cash += position.margin + position.pnl
            self.capital = self.cash + self.capital_invested
            del self.positions[position.ticker]
            position.close()
            print(f"{self.name} sold Stock {position.ticker} for {position.total}$ with Leverage: {position.leverage} at {position.price}")
        elif position.quantity > quantity:
            percentage = quantity / position.quantity
            self.capital_invested -=( position.margin + position.pnl) * percentage
            self.cash += (position.margin + position.pnl) * percentage
            self.capital = self.cash + self.capital_invested
            position.remove_quantity(quantity)
        else:
            print("Not enough stock to sell")
    
    def set_current_prices(self, ticker, price):
            self.current_prices[ticker] = price
    
    def update_positions(self, ticker, price):
        try: self.positions[ticker].update_price(price)
        except: pass
        self.capital = self.cash
        for position in self.positions.values():
            self.capital += position.pnl + position.margin
        self.set_current_prices(ticker, price)
    
    def get_cash(self):
        return self.cash

    def get_positions(self):
        return self.positions
    
class GameManager:
    """
    datetime must be in Year-Month-Day Minutes:Hours
    """
    def __init__(self, start_date, tickers) -> None:
        self.start_date = start_date
        self.tickers = tickers
        
    
    def get_stock_prices(self, ticker, start_date, end_date):
        start_date = np.datetime64(start_date, 'm')
        end_date = np.datetime64(end_date, 'm')
        if ticker in self.tickers:
            if ticker == 'EUR/USD':
                # Create a boolean mask
                mask = (data_eurusd['datetime'] >= start_date) & (data_eurusd['datetime'] <= end_date)
                Data_df = pd.DataFrame(data_eurusd[mask])
                Data_df.rename(columns={'datetime': 'date'}, inplace=True)
                Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')
                return Data_df
            elif ticker == 'BTC/USD':
                mask = (data_btcusd['datetime'] >= start_date) & (data_btcusd['datetime'] <= end_date)
                Data_df = pd.DataFrame(data_btcusd[mask])
                Data_df.rename(columns={'datetime': 'date'}, inplace=True)
                Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')
                return Data_df
        else:
            print("Not supported ticker symbol")