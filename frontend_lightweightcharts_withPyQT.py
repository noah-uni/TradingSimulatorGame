import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from lightweight_charts.widgets import QtChart
import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
start_date = "2022-08-09 07:20"
end_date = "2022-08-12 00:00"
Data = Game.get_stock_prices("EUR/USD", start_date, end_date)
Data_df = pd.DataFrame(Data)
Data_df.rename(columns={'datetime': 'date'}, inplace=True)
Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')

app = QApplication([])
window = QMainWindow()
layout = QVBoxLayout()
widget = QWidget()
widget.setLayout(layout)

window.resize(800, 500)
layout.setContentsMargins(0, 0, 0, 0)

chart = QtChart(widget)

df = pd.read_csv('ohlcv.csv')
chart.set(df)

layout.addWidget(chart.get_webview())

window.setCentralWidget(widget)
window.show()

app.exec_()