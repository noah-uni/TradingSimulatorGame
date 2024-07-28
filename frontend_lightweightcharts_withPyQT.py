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

df = Data_df
chart.set(df)
#test
def on_timeframe_selection(chart):
    print(f'Getting data with a {chart.topbar["time_menu"].value} timeframe.')
chart.topbar.menu(
    name='time_menu',
    options=('1min', '10min', '30min', '1h', '4h'),
    default='1min',
    func=on_timeframe_selection)

layout.addWidget(chart.get_webview())

window.setCentralWidget(widget)
window.show()

app.exec_()