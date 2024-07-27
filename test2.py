# nicegui_app.py
import subprocess
from nicegui import ui

# Start the Flask chart application as a subprocess
chart_app_process = subprocess.Popen(['python', 'test.py'])

@ui.page('/')
async def index():
    ui.markdown('## Stock Trading Chart')
    # Embed the chart application using an iframe
    ui.html('<iframe src="http://127.0.0.1:5000" width="100%" height="400px" frameborder="0"></iframe>')

    # Add buy/sell buttons
    ui.button('Buy', on_click=lambda: print("Buy action triggered"), color='green')
    ui.button('Sell', on_click=lambda: print("Sell action triggered"), color='red')

# Run the NiceGUI app
ui.run()

# Ensure the subprocess is terminated when the NiceGUI app exits
import atexit
atexit.register(chart_app_process.terminate)
