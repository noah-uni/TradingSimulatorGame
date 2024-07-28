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
Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')

cash = 10000
stock = "EUR/USD"
aktien = {stock: 0}
running = True

def buy():
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
        stockcount = int(input_field.text())
        value = stockcount * Data_df["close"].iloc[-1]
        global cash
        if cash >= value:
            aktien[stock] += stockcount
            cash -= value
            print("cash: ", cash)
            clabel.setText(f"Cash: {cash}")
            alabel.setText(f"{stock}: {aktien[stock]}")
            new_window.close()
        else:
            QMessageBox.information(window, "Title", "Zu arm für den Aktienpreis")
    
    def close_window():
        new_window.close()

    ok_button.clicked.connect(kaufen)
    cancel_button.clicked.connect(close_window)
    
    new_window.setLayout(layout)
    new_window.exec_()

    
def sell():
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
        stockcount = int(input_field.text())
        if aktien[stock] >= stockcount:
            aktien[stock] -= stockcount
            global cash
            cash += stockcount * Data_df["close"].iloc[-1]
            clabel.setText(f"Cash: {cash}")
            alabel.setText(f"{stock}: {aktien[stock]}")
            new_window.close()
        else:
            QMessageBox.information(window, "Title", "Nicht genug Aktien im Besitz")
        
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
    vonzeit = "00:00"
    biszeit = "00:01"
    while running:
        Data = Game.get_stock_prices("EUR/USD", f"2022-08-09 {vonzeit}", f"2022-08-10 {biszeit}")
        Data_df = pd.DataFrame(Data)
        Data_df = Data_df.rename(columns={'datetime': 'date'})
        Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')
        vonzeit = biszeit
        current_time = datetime.strptime(biszeit, "%H:%M")
        # Increment the time by one minute
        current_time += timedelta(minutes=1)
        # Format the datetime object back to a string and print
        biszeit = current_time.strftime("%H:%M")
        print(biszeit)
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
    max-height: 70px;
    display: inline-block;
""")
layout.addWidget(clabel)

alabel = QLabel(f"{stock}: {aktien[stock]}")
alabel.setStyleSheet("""
    font-size: 24px;
    font-weight: bold;
    color: white;
    padding: 10px;
    border-radius: 5px;
    max-height: 70px;
    display: inline-block;
""")
layout.addWidget(clabel)

text_layout.addWidget(clabel)
text_layout.addWidget(alabel)
layout.addLayout(text_layout)

chart = QtChart(widget)

#set chart data
chart.set(Data_df)


layout.addWidget(chart.get_webview())
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

buy_button.clicked.connect(buy)
sell_button.clicked.connect(sell)

widget.setLayout(layout)
window.setCentralWidget(widget)
window.show()

x = threading.Thread(target=update)
x.start()


app.exec_()
running = False
x.join()