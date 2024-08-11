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

eurusd_file = "eurusd_2021to2024.csv"
btcusd_file = "btcusd_2022to2024.csv"

# CSV lesen und in richtiges datenformat bringen
data_eurusd = pd.read_csv('./Data/'+eurusd_file)
data_eurusd['datetime'] = pd.to_datetime(data_eurusd['datetime'])
data_btcusd = pd.read_csv('./Data/'+btcusd_file)
data_btcusd['datetime'] = pd.to_datetime(data_btcusd['datetime'])

def invert(Data_df):
    #invertiert die kurse in den csv um shorten einfacher zu implementieren
    inverse = Data_df.copy()
    numerical_columns = Data_df.select_dtypes(include=['number']).columns
    for column in numerical_columns:
        initial_value = Data_df['close'].iloc[0]
        inverse[column] = initial_value * (2 - (Data_df[column] / initial_value))
        inverse[column] = inverse[column].round(5)
    return inverse

inverted = {}
inverted["EUR/USD"] = invert(data_eurusd)
inverted["BTC/USD"] = invert(data_btcusd)


class Position:
    """
    Klasse für Positionen, soll bei jedem kauf geöffnet werden und bei jedem verkauf geschlossen
    """
    def __init__(self, ticker, quantity, price, leverage, margin, type) -> None:
        self.ticker = ticker    #Kürzel der Aktie der Position
        self.quantity = quantity    #Menge an Aktien
        self.price_whenopened = price   #Eröffnungspreis
        self.price = price              #Aktueller Preis
        self.total_whenopened = self.quantity * self.price  #Positionsgröße bei Eröffnung
        self.total = self.quantity * self.price #aktuelle Positionsgröße
        self.leverage = leverage    #verwendeter Hebel
        self.margin = margin    #verwendetes Eigenkapital / Margin (Bei Hebel = 1: margin = total_whenopened)
        self.pnl = 0    #=Profit & Loss: Gewinn & Verlust
        self.type = type    #typ: long / short
        self.liquidation_price = self.price_whenopened * (1 - 1/leverage) #liquidationspreis (falls leverage = 1: liquidation_price = 0)

    def add_quantity(self, quantity_to_add, margin_to_add, price):
        #falls bereits eine Position exisitiert wird bei abermaligem Kaufen nur die bestehende Position angepasst
        self.quantity = self.quantity + quantity_to_add
        self.total_whenopened += quantity_to_add * price
        self.total += quantity_to_add * price
        self.margin += margin_to_add
        self.leverage = self.total_whenopened / self.margin
    
    def remove_quantity(self, quantity_to_remove):
        #analog zu add_quantity, wird bei nur teilweisem schließen einer position benötigt
        percentage = quantity_to_remove / self.quantity
        self.quantity = self.quantity - quantity_to_remove
        self.total_whenopened = self.quantity * self.price_whenopened
        self.total = self.quantity * self.price
        self.margin = self.margin * (1-percentage)
        self.pnl = self.total - self.total_whenopened
        
    def update_price(self, new_price, user):
        #um die Daten der Positionen zu aktualisieren
        self.price = new_price
        self.total = self.quantity * self.price
        self.pnl = self.total - self.total_whenopened
        if new_price <= self.liquidation_price:
            print(f"Postion {self.ticker} was liquidated with remaining Margin: {self.margin+self.pnl}")
            user.cash += self.margin+self.pnl
            del user.positions[self.ticker]
            self.close()
            return "Liquidation"
        return ""
        
    
    def close(self):
        self = None


class User:
    """
    Klasse die das Kapital und die Positionen eines Users speichert und verwaltet
    """
    def __init__(self, name, cash):
        self.name = name
        self.cash = cash                # Starting cash
        self.capital_invested = 0
        self.capital = self.cash + self.capital_invested
        self.positions = {}
        self.current_prices = {}
        
    def buy_stock(self, ticker, margin, price, leverage, type):
        #funktion um Aktien zu kaufen
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
            print(f"{self.name} bought Stock {ticker} of the type {type} for {margin}$ with Leverage: {leverage} at {price}")

        else:
            print("Not enough cash")

    def sell_stock(self, position:Position, percentage):
        #funktion um Aktien zu verkaufen
        quantity_to_sell = position.quantity * percentage
        
        if position.quantity == quantity_to_sell:
            self.capital_invested -= position.margin + position.pnl
            self.cash += position.margin + position.pnl
            self.capital = self.cash + self.capital_invested
            del self.positions[position.ticker]
            position.close()
            print(f"{self.name} sold Stock {position.ticker} for {position.total}$ with Leverage: {position.leverage} at {position.price}")
        elif position.quantity > quantity_to_sell:
            percentage = quantity_to_sell / position.quantity
            self.capital_invested -=( position.margin + position.pnl) * percentage
            self.cash += (position.margin + position.pnl) * percentage
            self.capital = self.cash + self.capital_invested
            position.remove_quantity(quantity_to_sell)
        else:
            print("Not enough stock to sell")
    
    def set_current_prices(self, ticker, price):
        #aktualisiert die liste mit aktuellen preisen, notwendig um positionen zu aktualisieren
            self.current_prices[ticker] = price
    
    def update_positions(self, ticker, price):
        #aktualisiert positionen und deren attribute, vor allem PNL sehr wichtig
        result = ""
        try: result = self.positions[ticker].update_price(price, self)
        except: pass
        self.capital = self.cash
        for position in self.positions.values():
            self.capital += position.pnl + position.margin
        self.set_current_prices(ticker, price)
        return result
    
    def get_cash(self):
        return self.cash

    def get_positions(self):
        return self.positions
    
class GameManager:
    """
    Klasse um das Spiel zu verwalten & Daten bereitzustellen
    datetime must be in Year-Month-Day Minutes:Hours
    """
    def __init__(self, start_date, tickers) -> None:
        self.start_date = start_date
        self.tickers = tickers

    def get_data_frame(self, data_source, start_date, end_date):
        #Eigene Methode für Dataframe Verarbeitung
        mask = (data_source['datetime'] >= start_date) & (data_source['datetime'] <= end_date)
        Data_df = pd.DataFrame(data_source[mask])
        Data_df.rename(columns={'datetime': 'date'}, inplace=True)
        Data_df['date'] = Data_df['date'].map(lambda x: str(x) + '+00:00')
        return Data_df
    
    def get_stock_prices(self, ticker, start_date, end_date):
        #methode um daten/aktienkurse zu bekommen
        start_date = np.datetime64(start_date, 'm')
        end_date = np.datetime64(end_date, 'm')
        if ticker in self.tickers:
            if ticker == 'EUR/USD':
                return self.get_data_frame(data_eurusd, start_date, end_date)
            elif ticker == 'BTC/USD':
                return self.get_data_frame(data_btcusd, start_date, end_date)
            elif ticker == "Inverse EUR/USD":
                return self.get_data_frame(inverted["EUR/USD"], start_date, end_date)
            elif ticker == "Inverse BTC/USD":
                return self.get_data_frame(inverted["BTC/USD"], start_date, end_date)
        else:
            print("Not supported ticker symbol")