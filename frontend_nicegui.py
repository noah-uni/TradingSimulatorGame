import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
Data = Game.get_stock_prices("EUR/USD", "2022-08-09 07:20", "2022-08-10 00:00")


from nicegui import ui

with ui.dropdown_button('Select Ticker', auto_close=True):
    ui.item('EUR/USD', on_click=lambda: ui.notify('You clicked item 1'))
    ui.item('BTC/USD', on_click=lambda: ui.notify('You clicked item 2'))

select_time = ui.select(["1min", "15min", "1h", "4h"], with_input=True, value=1)
select_charttype = ui.select(["Candles", "Line"], with_input=True, value=1)

ui.run()