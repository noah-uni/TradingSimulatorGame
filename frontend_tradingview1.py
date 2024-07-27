from lightweight_charts import Chart
import pandas as pd
import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
start_date = "2022-08-09 07:20"
end_date = "2022-08-12 00:00"
Data = Game.get_stock_prices("EUR/USD", start_date, end_date)
Data_df = pd.DataFrame(Data)
Data_df.rename(columns={'datetime': 'date'}, inplace=True)
Data_df['date'] = Data_df['date'].map(lambda x: str(x)+'+00:00')

def get_bar_data(symbol, start_date=start_date, end_date=end_date):
    if symbol not in Game.tickers:
        print(f'No data for "{symbol}"')
        return pd.DataFrame()
    return Game.get_stock_prices(symbol, start_date, end_date)


def on_timeframe_selection(chart):
    print(f'Getting data with a {chart.topbar["time_menu"].value} timeframe.')
def on_ticker_selection(chart):
    print(f'Showing data of ticker {chart.topbar["ticker_menu"].value}.')
def on_graphics_selection(chart):
    print(f'Graphics changed to {chart.topbar["graphics_menu"].value}.')
    
def calculate_sma(df, chart, line):
    print("Topbsr")
    try:
        print("Topbsr")
        period = chart.topbar['sma_menu'].value
    except: 
        period = 5
    print("Test")
    sma_df = pd.DataFrame({
    'date': df['date'],
    f'SMA': df['close'].rolling(window=period).mean()
    }).dropna()
    
    try:
        print("Update1")
        sma_series = sma_df['SMA']
        line.update(sma_series)
        print("Update2")
    except:
        print("Set1")
        line.set(sma_df)
        print("Set2")
    
if __name__ == '__main__':
    chart = Chart()
    #line = chart.create_line(name='SMA')
    chart.set(Data_df)
    line = chart.create_line(name='SMA')
    
    chart.topbar.menu(
    name='time_menu',
    options=('1min', '10min', '30min', '1h', '4h'),
    default='1min',
    func=on_timeframe_selection)
    
    chart.topbar.menu(
        name='ticker_menu',
        options=('EUR/USD', 'BTC/USD'),
        default='EUR/USD',
        func=on_ticker_selection)
    
    chart.topbar.menu(
        name='graphics_menu',
        options=('Candles', 'Line'),
        default='Candles',
        func=on_graphics_selection)
    
    chart.topbar.menu(
    name='sma_menu',
    options=('5', '25', '50', '100', '200'),
    default='5',
    func=calculate_sma(Data_df, chart, line)
    )
    chart.show(block = True)
