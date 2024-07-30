import pandas as pd
from lightweight_charts import Chart
import backend
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QDialog, QLineEdit, QMessageBox
from lightweight_charts.widgets import QtChart, QWebEngineView
import time
import threading
from datetime import datetime, timedelta

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
Data = Game.get_stock_prices("EUR/USD", "2022-08-09 07:20", "2022-08-10 00:00")
Data_df = pd.DataFrame(Data)
Data_df = Data_df.rename(columns={'datetime': 'date'})
#Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')

def buy(ticker, user: backend.User):
    new_window = QDialog()
    new_window.setWindowTitle("Buy")
    new_window.resize(400, 300)

    layout = QVBoxLayout()
    
    label = QLabel("Anzahl der Aktien:")
    layout.addWidget(label)
    
    input_field = QLineEdit()
    layout.addWidget(input_field)
    
    button_layout = QHBoxLayout()
    
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    
    ok_button.setStyleSheet("background-color: green; color: white; font-size: 18px; padding: 10px;")
    cancel_button.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 10px;")
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    
    layout.addLayout(button_layout)

    def kaufen():
        while True:
            try:
                quantity = int(input_field.text())
                break
            except:
                #catch edge case, when user hasnt entered a quantity
                QMessageBox.information(window, "Title", "Bitte gebe eine Menge an!")
                return
        
        value = quantity * Data_df["close"].iloc[-1]
        #integrating backend:
        if user.cash >= value:
            user.buy_stock(ticker, quantity, Data_df["close"].iloc[-1], leverage=1, type='long')
            clabel.setText(f"Cash: {user.cash}")
            alabel.setText(f"{ticker}: {user.positions[ticker].quantity}")
            new_window.close()
        else:
            QMessageBox.information(window, "Title", "Zu arm für den Aktienpreis")
            
        """ old code:
        global cash
        if cash >= value:
            aktien[stock] += stockcount
            cash -= value
            print("cash: ", cash)
            clabel.setText(f"Cash: {cash}")
            alabel.setText(f"{stock}: {aktien[stock]}")
            new_window.close()
        else:
            QMessageBox.information(window, "Title", "Zu arm für den Aktienpreis")"""
    
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
    
    label = QLabel("Anzahl der Aktien:")
    layout.addWidget(label)
    
    input_field = QLineEdit()
    layout.addWidget(input_field)
    
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
                quantity = int(input_field.text())
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
            if user.positions[ticker].quantity >= quantity:
                user.sell_stock(user.positions[ticker], quantity)
                clabel.setText(f"Cash: {user.cash}")
                try:
                    alabel.setText(f"{ticker}: {user.positions[stock].quantity}")
                except:
                    alabel.setText(f"{ticker}: {0}")
                new_window.close()
            else:
                QMessageBox.information(window, "Title", "Nicht genug Aktien im Besitz")
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

def update():
    vonzeit = "07:20"
    biszeit = "00:01"
    while running:
        Data = Game.get_stock_prices("EUR/USD", f"2022-08-09 {vonzeit}", f"2022-08-10 {biszeit}")
        Data_df = pd.DataFrame(Data)
        Data_df = Data_df.rename(columns={'datetime': 'date'})
        current_time = datetime.strptime(biszeit, "%H:%M")
        # Increment the time by one minute
        current_time += timedelta(minutes=1)
        # Format the datetime object back to a string and print
        biszeit = current_time.strftime("%H:%M")
        chart.set(Data_df)
        time.sleep(1)

# if __name__ == '__main__':
#     chart = Chart()

#     # Columns: time | open | high | low | close | volume 
#     #df = pd.read_csv('ohlcv.csv')
#     chart.set(Data_df)
#     chart.topbar.textbox('clock', 'dings')
#     chart.topbar.button('my_button', 'Off', func=on_button_press)
#     chart.show(block=True)

cash = 10000
stock = "EUR/USD"
aktien = {stock: 0}
running = True
user1 = backend.User("name", cash=cash) #create a user in the backend
"""to do: pop up window which lets the user enter a name"""
    
app = QApplication([])
window = QMainWindow()
layout = QVBoxLayout()
widget = QWidget()

window.resize(800, 500)
layout.setContentsMargins(0, 0, 0, 0)

text_layout = QHBoxLayout()

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

alabel = QLabel(f"{stock}: {aktien[stock]}")
alabel.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 10px;
    border-radius: 5px;
    height: 20px;
    display: inline-block;
""")

text_layout.addWidget(clabel)
text_layout.addWidget(alabel)
#text_layout.setSizeConstraint()
layout.addLayout(text_layout,1)

chart = QtChart(widget)


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
#using lambad because it makes it possible to pass a function with arguments as an argument
sell_button.clicked.connect(lambda: sell(user=user1, ticker=stock))

widget.setLayout(layout)
window.setCentralWidget(widget)
window.show()

x = threading.Thread(target=update)
x.start()


app.exec_()
running = False
x.join()