import backend

Game = backend.GameManager("2022-06-06", ["EUR/USD"])
Data = Game.get_stock_prices("EUR/USD", "2022-08-09 07:20", "2022-08-10 00:00")


from nicegui import ui

ui.label("Hello")
ui.run()