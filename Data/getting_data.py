from alpha_vantage.timeseries import TimeSeries
import pandas as pd

# Your Alpha Vantage API key
api_key = 'HQM041114YXW71OZ'

# Create an Alpha Vantage TimeSeries object
ts = TimeSeries(key=api_key, output_format='pandas')

# Get minute-level data for a given symbol (e.g., 'AAPL')
data, meta_data = ts.get_intraday(symbol='TSLA', interval='1min', outputsize='full', month='January')
print(meta_data)
print(len(data))
print(data)
