import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MinuteLocator
import mplfinance as mpf
from nicegui import ui

# Step 1: Prepare the DataFrame
import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
data = Game.get_stock_prices("EUR/USD", "2022-08-09 07:20", "2022-08-10 00:00")

df = pd.DataFrame(data, columns=["datetime", "open", "high", "low", "close"])
df["datetime"] = pd.to_datetime(df["datetime"])

# Step 2: Plot the Candlestick Chart
def plot_candlestick_chart():
    fig, ax = plt.subplots()
    mpf.plot(
        df.set_index("datetime"),
        type='candle',
        style='charles',
        ax=ax,
        datetime_format='%Y-%m-%d %H:%M',
        xrotation=20
    )
    
    ax.xaxis.set_major_locator(MinuteLocator(interval=1))
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("Stock Chart")
    plt.grid(True)

    return fig

# Step 3: Integrate with NiceGUI
"""@ui.page('/')
async def main_page():"""
fig = plot_candlestick_chart()
ui.pyplot(fig)

# Start the NiceGUI application
ui.run()
