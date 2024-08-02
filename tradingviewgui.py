import pandas as pd
from lightweight_charts import Chart
import backend
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QDialog, QLineEdit, QMessageBox, QSlider
from PyQt5.QtCore import Qt
from lightweight_charts.widgets import QtChart, QWebEngineView
import time
import threading
from datetime import datetime, timedelta

interval = 1
stock = "EUR/USD"
all_stocks = ["EUR/USD", "BTC/USD"]
Game = backend.GameManager("2022-06-06", all_stocks)
Data_df = Game.get_stock_prices(stock, "2022-08-09 07:20", "2022-08-10 00:00")
Data_df = Data_df.iloc[::interval, :]
current_price = Data_df["close"].iloc[-1]
#Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')

def buy(ticker, user: backend.User):
    current_price = user.current_prices[ticker]  # Assuming this is how you get the current price
    new_window = QDialog()
    new_window.setWindowTitle("Buy")
    new_window.resize(400, 300)

    layout = QVBoxLayout()
    
    # Adding input widgets for margin and leverage:
    label1 = QLabel("Margin:")
    layout.addWidget(label1)
    input_field1 = QLineEdit()
    layout.addWidget(input_field1)
    
    label2 = QLabel("Leverage: 1")
    layout.addWidget(label2)

    def update_percentage_label(value):
        label2.setText(f"Leverage: {value}")
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(1)
    slider.setMaximum(200)
    slider.setValue(1)  # Default value
    layout.addWidget(slider)

    # Connect the slider's valueChanged signal to update the label
    slider.valueChanged.connect(update_percentage_label)
    
    # Adding output widget for calculated quantity
    quantity_label = QLabel("Quantity: 0")
    layout.addWidget(quantity_label)

    button_layout = QHBoxLayout()
    
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    
    ok_button.setStyleSheet("background-color: green; color: white; font-size: 18px; padding: 10px;")
    cancel_button.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 10px;")
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    
    layout.addLayout(button_layout)

    def update_quantity():
        try:
            margin = int(input_field1.text())
            leverage = int(slider.value())
            quantity = (margin * leverage) / current_price
            quantity_label.setText(f"Quantity: {quantity:.2f}")
        except ValueError:
            quantity_label.setText("Quantity: Invalid input")

    # Connect the textChanged signals to the update_quantity function
    input_field1.textChanged.connect(update_quantity)
    slider.valueChanged.connect(update_quantity)

    def kaufen():
        try:
            margin = int(input_field1.text())
            leverage = int(slider.value())
            quantity = (margin * leverage) / current_price

            if user.cash >= margin:
                user.buy_stock(ticker, margin, current_price, leverage, type='long')
                clabel.setText(f"Cash: {user.cash}")
                alabel.setText(f"{ticker}: {user.positions[ticker].quantity}")
                new_window.close()
            else:
                QMessageBox.information(new_window, "Title", "Nicht genug Cash")
        except ValueError:
            QMessageBox.information(new_window, "Title", "Bitte gebe eine Menge & Hebel an!")

    def close_window():
        new_window.close()

    ok_button.clicked.connect(kaufen)
    cancel_button.clicked.connect(close_window)
    
    new_window.setLayout(layout)
    new_window.exec_()

    
def sell(ticker, user):
    new_window = QDialog()
    new_window.setWindowTitle("Sell")
    new_window.resize(400, 300)

    layout = QVBoxLayout()
    
    label1 = QLabel("Prozent der Anzahl der Aktien: 50%")
    layout.addWidget(label1)
    
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(1)
    slider.setMaximum(100)
    slider.setValue(50)  # Default value
    layout.addWidget(slider)

    def update_percentage_label(value):
        label1.setText(f"Prozent der Anzahl der Aktien: {value}%")

    # Connect the slider's valueChanged signal to update the label
    slider.valueChanged.connect(update_percentage_label)
    
    button_layout = QHBoxLayout()
    
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    
    ok_button.setStyleSheet("background-color: green; color: white; font-size: 18px; padding: 10px;")
    cancel_button.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 10px;")
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    
    layout.addLayout(button_layout)

    def verkaufen():
        while True:
            try:
                percentage = slider.value() / 100
                break
            except:
                #catch edge case, when user hasnt entered a quantity
                QMessageBox.information(window, "Title", "Bitte gebe eine Menge an!")
                return
        #with integrated backend:
        """
        1. sell the stock
        2. if the new quantity would be zero, the backend deletes the whole object
        3. use try-except
        """
        try:
            user.sell_stock(user.positions[ticker], percentage)
            clabel.setText(f"Cash: {user.cash}")
            try:
                alabel.setText(f"{ticker}: {user.positions[stock].quantity}")
            except:
                alabel.setText(f"{ticker}: {0}")
            new_window.close()
        except:
            QMessageBox.information(window, "Title", "Von dieser Aktie gibt es keine offene Position")
        """ old code:
        if aktien[stock] >= stockcount:
            aktien[stock] -= stockcount
            global cash
            cash += stockcount * Data_df["close"].iloc[-1]
            clabel.setText(f"Cash: {cash}")
            alabel.setText(f"{stock}: {aktien[stock]}")
            new_window.close()
        else:
            QMessageBox.information(window, "Title", "Nicht genug Aktien im Besitz")"""
        
    def close_window():
        new_window.close()

    ok_button.clicked.connect(verkaufen)
    cancel_button.clicked.connect(close_window)
    
    new_window.setLayout(layout)
    new_window.exec_()

def on_button_press(chart):
    new_button_value = 'On' if chart.topbar['my_button'].value == 'Off' else 'Off'
    chart.topbar['my_button'].set(new_button_value)
    print(f'Turned something {new_button_value.lower()}.')

def update(user):
    vonzeit = "07:20"
    biszeit = "00:01"
    while running:
        Data_df = Game.get_stock_prices(stock, f"2022-08-09 {vonzeit}", f"2022-08-10 {biszeit}") 
        Data_df = Data_df.iloc[::interval, :]
        current_time = datetime.strptime(biszeit, "%H:%M")
        # Increment the time by one minute
        current_time += timedelta(minutes=interval)
        # Format the datetime object back to a string and print
        biszeit = current_time.strftime("%H:%M")
        chart.set(Data_df)
        current_price = Data_df["close"].iloc[-1]
        user.update_positions(stock, current_price)
        try: pnllabel.setText(f"{stock} PNL: {user.positions[stock].pnl}")
        except: pnllabel.setText(f"{stock} PNL: 0")
        try: alabel.setText(f"{stock}: {user.positions[stock].quantity}")
        except: alabel.setText(f"{stock}: 0")
        #update all other stocks so portfolio value is correctly updated:
        current_date = Data_df["date"].iloc[-1]
        for ticker in all_stocks:
            if ticker != stock:
                Data_df_2 = Game.get_stock_prices(ticker, current_date, current_date)
                user.update_positions(ticker, Data_df_2["close"][0])
        pvlabel.setText(f"Portfolio Value: {user.capital}")
        time.sleep(0.5)

# if __name__ == '__main__':
#     chart = Chart()

#     # Columns: time | open | high | low | close | volume 
#     #df = pd.read_csv('ohlcv.csv')
#     chart.set(Data_df)
#     chart.topbar.textbox('clock', 'dings')
#     chart.topbar.button('my_button', 'Off', func=on_button_press)
#     chart.show(block=True)

def timechange(chart):
    global interval
    if chart.topbar['timemenu'].value == "1min":
        interval = 1
    elif chart.topbar['timemenu'].value == "10min":
        interval = 10
    elif chart.topbar['timemenu'].value == "30min":
        interval = 30
    elif chart.topbar['timemenu'].value == "1h":
        interval = 60
    elif chart.topbar['timemenu'].value == "4h":
        interval = 60*4

def stockchange(chart):
    global stock
    stock = chart.topbar['stock_menu'].value
    
cash = 100000
running = True
user1 = backend.User("name", cash=cash) #create a user in the backend
#user1.set_current_prices(stock, current_price)
"""to do: pop up window which lets the user enter a name"""
    
app = QApplication([])
window = QMainWindow()
layout = QVBoxLayout()
widget = QWidget()

window.resize(800, 500)
layout.setContentsMargins(0, 0, 0, 0)

text_layout = QHBoxLayout()

pvlabel = QLabel(f"Portfolio Value: {cash}")
pvlabel.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 10px;
    border-radius: 5px;
    height: 20px;
    display: inline-block;
""")

clabel = QLabel(f"Cash: {cash}")
clabel.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 10px;
    border-radius: 5px;
    height: 20px;
    display: inline-block;
""")

alabel = QLabel(f"{stock}: 0")
alabel.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 10px;
    border-radius: 5px;
    height: 20px;
    display: inline-block;
""")

pnllabel = QLabel(f"{stock} PNL: 0")
pnllabel.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 10px;
    border-radius: 5px;
    height: 20px;
    display: inline-block;
""")
text_layout.addWidget(pvlabel)
text_layout.addWidget(clabel)
text_layout.addWidget(alabel)
text_layout.addWidget(pnllabel)
layout.addLayout(text_layout,1)

chart = QtChart(widget)

chart.topbar.menu(
    name='timemenu',
    options=('1min', '10min', '30min', '1h', '4h'),
    default='1min',
    func=timechange
    )

chart.topbar.menu(
    name='stock_menu',
    options=('BTC/USD', 'EUR/USD'),
    default= stock,
    func=stockchange
    )
#set chart data
chart.set(Data_df)

chalayout = QHBoxLayout()
chalayout.addWidget(chart.get_webview())

layout.addLayout(chalayout,9)
# Create the buy and sell buttons
buy_button = QPushButton("Buy")
sell_button = QPushButton("Sell")

btn_layout = QHBoxLayout()

# Add buttons to the layout
btn_layout.addWidget(buy_button)
btn_layout.addWidget(sell_button)

buy_button.setStyleSheet("background-color: green; color: white; font-size: 18px; padding: 10px; display: inline-block; border: 0;")
sell_button.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 10px; display: inline-block; border: 0;")

layout.addLayout(btn_layout)

buy_button.clicked.connect(lambda: buy(user=user1, ticker=stock))
#using lambda because it makes it possible to pass a function with arguments as an argument
sell_button.clicked.connect(lambda: sell(user=user1, ticker=stock))

widget.setLayout(layout)
window.setCentralWidget(widget)
window.show()

x = threading.Thread(target= lambda: update(user1))
x.start()


app.exec_()
running = False
x.join()