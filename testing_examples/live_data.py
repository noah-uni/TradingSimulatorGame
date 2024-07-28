import pandas as pd
from time import sleep
from lightweight_charts import Chart

import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
start_date = "2022-08-09 07:20"
end_date = "2022-08-12 00:00"
end_date2 = "2022-08-12 00:01"
next_date = "2022-08-13 00:00"
Data_df = Game.get_stock_prices("EUR/USD", start_date, end_date)
Data_Next_df = Game.get_stock_prices("EUR/USD", end_date2, next_date)


if __name__ == '__main__':

    chart = Chart()

    """df1 = pd.read_csv('./testing_examples/ohlcv.csv')
    df2 = pd.read_csv('./testing_examples/next_ohlcv.csv')"""
    df1 = Data_df
    df2 = Data_Next_df
    
    chart.set(df1)

    chart.show()

    last_close = df1.iloc[-1]['close']

    for i, series in df2.iterrows():
        chart.update(series)

        if series['close'] > 20 and last_close < 20:
            chart.marker(text='The price crossed $20!')

        last_close = series['close']
        sleep(1)