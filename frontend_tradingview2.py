from lightweight_charts import Chart
import pandas as pd
import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
start_date = "2022-08-09 07:20"
end_date = "2022-08-12 00:00"
next_date = "2022-08-13 00:00"
Data_df = Game.get_stock_prices("EUR/USD", start_date, end_date)
Data_Next_df = Game.get_stock_prices("EUR/USD", end_date, next_date)


def get_bar_data(symbol, start_date=start_date, end_date=end_date):
    if symbol not in Game.tickers:
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return Game.get_stock_prices(symbol, start_date, end_date)


import pandas as pd
from time import sleep
from lightweight_charts import Chart

if __name__ == '__main__':

    chart = Chart()

    chart.set(Data_df)

    chart.show()

    last_close = Data_df.iloc[-1]['close']

    for i, series in Data_Next_df.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')

        last_close = series['close']
        sleep(5)