from lightweight_charts import Chart
import backend
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QVBoxLayout, 
    QHBoxLayout, 
    QWidget, 
    QPushButton, 
    QLabel, 
    QDialog, 
    QLineEdit, 
    QMessageBox, 
    QSlider,
    QRadioButton,
    QInputDialog,
    QScrollArea,
    )
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont
from lightweight_charts.widgets import QtChart, QWebEngineView
import time
import threading
from datetime import datetime, timedelta
import socket
import json
import threading

LOCAL_PORT = 12346

#declare & intitalize default variablen
pvp = True
client = None
thecountdown = 10
speed_factor = 60
table = {}
interval = 1
stock = "EUR/USD"
all_stocks = ["EUR/USD", "BTC/USD", "Inverse EUR/USD", "Inverse BTC/USD"]
Game = backend.GameManager(speed_factor, "2022-06-06", thecountdown, all_stocks)
Data_df = Game.get_stock_prices(stock, "2022-08-09 07:20", "2022-08-10 00:00")
Data_df = Data_df.iloc[::interval, :]
current_price = Data_df["close"].iloc[-1]

#funktion die layout und backend fürs kaufen konfiguriert
def buy(ticker, user: backend.User):
    current_price = user.current_prices[ticker]
    
    #layout erstellen
    new_window = QDialog()
    new_window.setWindowTitle("Buy")
    new_window.resize(400, 300)

    layout = QVBoxLayout()
    
    # Hinzufügen von input widgets für margin:
    label1 = QLabel("Margin:")
    layout.addWidget(label1)
    input_field1 = QLineEdit()
    layout.addWidget(input_field1)

    #long short buttons
    long_radio = QRadioButton("Long")
    short_radio = QRadioButton("Short")
    long_radio.setChecked(True)  # Default to Long

    radio_layout = QHBoxLayout()
    radio_layout.addWidget(long_radio)
    radio_layout.addWidget(short_radio)
    layout.addLayout(radio_layout)

    #falls short -> ticker zu "Inverse ticker", da wir um zu 
    # shorten seperate ticker erstellen die den ursprünglichen invertieren
    def radio_clicked(ticker):
        if long_radio.isChecked():
            if ticker.startswith("Inverse "):
                ticker = ticker.removeprefix("Inverse ")
        elif short_radio.isChecked():
            if not ticker.startswith("Inverse "):
                ticker = "Inverse " + ticker
        return ticker

    def on_radio_clicked():
        nonlocal ticker, current_price
        ticker = radio_clicked(ticker)
        current_price = user.current_prices[ticker]
        update_quantity()

    long_radio.toggled.connect(on_radio_clicked)
    short_radio.toggled.connect(on_radio_clicked)

    # Hinzufügen von input widgets für margin:
    label2 = QLabel("Leverage: 1")
    layout.addWidget(label2)
    def update_percentage_label(value):
        label2.setText(f"Leverage: {value:.2f}")
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(1)
    slider.setMaximum(200)
    slider.setValue(1)  # Default value
    layout.addWidget(slider)

    #slider mit funktion verbinden die dirket quantity berechnet
    slider.valueChanged.connect(update_percentage_label)
    
    # Hinzufügen von output widget für calculated quantity
    quantity_label = QLabel("Quantity: 0")
    layout.addWidget(quantity_label)

    #buttons für kaufen und canceln hinzufügen
    button_layout = QHBoxLayout()
    
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    
    ok_button.setStyleSheet("background-color: green; color: white; font-size: 18px; padding: 10px;")
    cancel_button.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 10px;")
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    
    layout.addLayout(button_layout)

    #funktion um die quantity zu berechnen
    def update_quantity():
        try:
            margin = int(input_field1.text())
            leverage = int(slider.value())
            quantity = (margin * leverage) / current_price
            quantity_label.setText(f"Quantity: {quantity:.2f}")
        except ValueError:
            quantity_label.setText("Quantity: Invalid input")

    # Connect the textChanged signals to the update_quantity function
    input_field1.textChanged.connect(update_quantity)
    slider.valueChanged.connect(update_quantity)

    #funktion um im backend zu kaufen und error handling zu machen
    def kaufen():
        try:
            margin = int(input_field1.text())
            leverage = int(slider.value())
            position_type = "long" if long_radio.isChecked() else "short"

            if user.cash >= margin:
                user.buy_stock(ticker, margin, current_price, leverage, type=position_type)
                cashlabel.setText(f"Cash: {user.cash:.2f}")
                #quantitylabel.setText(f"{ticker}: {user.positions[ticker].quantity:.2f}")
                new_window.close()
                chart.marker(shape="circle", text=f"Bought {ticker}", color="green")
            else:
                QMessageBox.information(new_window, "Title", "Nicht genug Cash")
        except ValueError:
            QMessageBox.information(new_window, "Title", "Bitte gebe eine Menge & Hebel an!")

    def close_window():
        new_window.close()

    ok_button.clicked.connect(kaufen)
    cancel_button.clicked.connect(close_window)
    
    new_window.setLayout(layout)
    new_window.exec_()

#funktion die layout und backend fürs verkaufen konfiguriert
def sell(ticker, user):
    #layout um zu verkaufen
    new_window = QDialog()
    new_window.setWindowTitle("Sell")
    new_window.resize(400, 300)

    layout = QVBoxLayout()
    
    label1 = QLabel("Prozent der Anzahl der Aktien: 50%")
    layout.addWidget(label1)

    long_radio = QRadioButton("Long")
    short_radio = QRadioButton("Short")
    long_radio.setChecked(True)  # Default to Long

    radio_layout = QHBoxLayout()
    radio_layout.addWidget(long_radio)
    radio_layout.addWidget(short_radio)
    layout.addLayout(radio_layout)
    
    #slider um prozentzahl der zu verkaufenden aktien festzulegen
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(1)
    slider.setMaximum(100)
    slider.setValue(50)  # Default value
    layout.addWidget(slider)

    #label je nach slider position updaten
    def update_percentage_label(value):
        label1.setText(f"Prozent der Anzahl der Aktien: {value}%")

    # Connect the slider's valueChanged signal to update the label
    slider.valueChanged.connect(update_percentage_label)
    
    button_layout = QHBoxLayout()
    
    ok_button = QPushButton("OK")
    cancel_button = QPushButton("Cancel")
    
    ok_button.setStyleSheet("background-color: green; color: white; font-size: 18px; padding: 10px;")
    cancel_button.setStyleSheet("background-color: red; color: white; font-size: 18px; padding: 10px;")
    
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    
    layout.addLayout(button_layout)

    #funktion für error handling und backend nutzung beim verkaufen
    def verkaufen():
        while True:
            try:
                percentage = slider.value() / 100
                break
            except:
                #catch edge case, when user hasnt entered a quantity
                QMessageBox.information(window, "Title", "Bitte gebe eine Menge an!")
                return
        try:
            # ticker wird invertiert, wenn short ausgewählt wurde
            nonlocal ticker
            if long_radio.isChecked():
                if ticker.startswith("Inverse "):
                    ticker = ticker.removeprefix("Inverse ")
            elif short_radio.isChecked():
                if not ticker.startswith("Inverse "):
                    ticker = "Inverse " + ticker
            user.sell_stock(user.positions[ticker], percentage)
            cashlabel.setText(f"Cash: {user.cash:.2f}")
            """
            try:
                positions_label.setText(f"{ticker}: {user.positions[stock].quantity:.2f}")
            except:
                positions_label.setText(f"{ticker}: {0}")
            """
            chart.marker(shape="circle", text=f"Sold {ticker}", color="red")
            new_window.close()
        except:
            QMessageBox.information(window, "Title", "Von dieser Aktie gibt es keine offene Position")
        
    def close_window():
        new_window.close()

    ok_button.clicked.connect(verkaufen)
    cancel_button.clicked.connect(close_window)
    
    new_window.setLayout(layout)
    new_window.exec_()

def on_button_press(chart):
    new_button_value = 'On' if chart.topbar['my_button'].value == 'Off' else 'Off'
    chart.topbar['my_button'].set(new_button_value)
    print(f'Turned something {new_button_value.lower()}.')

#funktion die die charts und preise updatet
def update(user):
    try: 
        biszeit = Game.start_date
        vonzeit = datetime.strptime(biszeit, "%Y-%m-%d %H:%M") - timedelta(days=2)
    except: 
        vonzeit = "2022-08-09 07:20"
        biszeit = "2022-08-10 00:01"
        
    while running:
        Data_df = Game.get_stock_prices(stock, vonzeit, biszeit) 
        #close und open angleichen wenn intervall größer als eine minute ist
        if interval > 1:
            tempData_df = Data_df.iloc[interval-1::interval, :].reset_index(drop=True)
            Data_df = Data_df.iloc[::interval, :].reset_index(drop=True)
            min_length = min(len(Data_df), len(tempData_df))
            Data_df = Data_df.iloc[:min_length, :]
            #Close Positionen von der Reihe davor übernehmen
            Data_df["close"] = tempData_df["close"]

        #Format the string to a datetime object
        current_time = datetime.strptime(biszeit, "%Y-%m-%d %H:%M")
        # Increment the time by one minute
        current_time += timedelta(minutes=interval)
        # Format the datetime object back to a string and print
        biszeit = current_time.strftime("%Y-%m-%d %H:%M")
        chart.set(Data_df)
        current_price = Data_df["close"].iloc[-1]
        current_date = Data_df["date"].iloc[-1]
        result = user.update_positions(stock, current_price)
        #check for possible liquidation
        if result == "Liquidation":
            chart.marker(time=current_date, shape="circle", text=f"Position {stock} was liquidated")
        #update pnl data
        try: pnllabel.setText(f"Total unrealized PNL: {sum([position.pnl for position in user.positions.values()]):.2f}")
        except: pnllabel.setText(f"Total unrealized PNL: 0")
        #update Open Positions data
        try: positions_label.setText(f"Open Positions: {len(user.positions)}")
        except: positions_label.setText(f"Open Positions: 0")
        #update total pnl label color (green or red or white)
        color = "#FFFFFF"
        if sum(position.pnl for position in user.positions.values()) > 0:
            color = "#00FF00"
        elif sum(position.pnl for position in user.positions.values()) < 0:
            color = "#FF4500"
        pnllabel.setStyleSheet(f"""
            font-size: 28px;
            font-weight: 600;
            color: {color};
            padding: 12px 15px;
            background-color: #1F1F1F;
            border: 2px solid #FFFFFF;
            border-radius: 8px;
            min-height: 40px;
            qproperty-alignment: 'AlignCenter';
        """)
        #update all other stocks so portfolio value is correctly updated:
        for ticker in all_stocks:
            if ticker != stock:
                Data_df_2 = Game.get_stock_prices(ticker, current_date, current_date)
                try: 
                    result = user.update_positions(ticker, Data_df_2["close"].iloc[0])
                    if result == "Liquidation":
                        chart.marker(time=current_date, shape="circle", text=f"Position {ticker} was liquidated")
                except: print(f"Missing Data in Df {ticker}")

        pvlabel.setText(f"Portfolio Value: {user.capital:.2f}")
        cashlabel.setText(f"Cash: {user.cash:.2f}")

        if pvp:
            client.send_profit(user.capital - 100000)
        time.sleep(60/Game.speed_factor)


def timechange(chart):
    global interval
    if chart.topbar['timemenu'].value == "1min":
        interval = 1
    elif chart.topbar['timemenu'].value == "10min":
        interval = 10
    elif chart.topbar['timemenu'].value == "30min":
        interval = 30
    elif chart.topbar['timemenu'].value == "1h":
        interval = 60
    elif chart.topbar['timemenu'].value == "4h":
        interval = 60*4

def stockchange(chart):
    global stock
    stock = chart.topbar['stock_menu'].value

#benutzer erstellen
cash = 100000
running = True
user1 = backend.User("name", cash=cash) #create a user in the backend

class GameClient(QObject):
    end_game_signal = pyqtSignal()
    def __init__(self, player_id, host='localhost', port=LOCAL_PORT):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.player_id = player_id
        self.profit = 0

    def send_profit(self, profits):
        self.profit = profits
        data = {
            'type': 'game',
            'player_id': self.player_id,
            'profit': profits
        }
        self.client.send(json.dumps(data).encode('utf-8'))

    def receive_results(self):
        global running, table
        while running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                results = json.loads(message)
                if results['type'] == "timer":
                    timestring = results['time']
                    timerlabel.setText(f"Time left: {timestring}")

                elif results['type'] == "game over":
                    print("received:" , results)
                    running = False
                    table = results["profit"]
                    self.end_game_signal.emit()

            except ConnectionResetError:
                break
            except Exception as e:
                print("Error while receiving results: ", e)

    def send(self, data):
        self.client.sendall(data)

    def send_ready_status(self):
        data = {
            'type': 'ready',
            'name': self.player_id
        }
        self.client.send(json.dumps(data).encode('utf-8'))

    def receive(self):
        while running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                players = json.loads(message)
                print("players:", players)
                yield players
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def start(self):
        self.result_thread = threading.Thread(target=self.receive_results)
        self.result_thread.start()
        self.end_game_signal.connect(end_screen)

    def end(self):
        self.client.close()
        try:
            self.client.shutdown(socket.SHUT_RDWR)  # Shut down the socket for both send and receive
        except OSError as e:
            pass
        self.result_thread.join()


class NameInputDialog(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.label = QLabel("Mandatory Fields", self)
        self.label.setFont(QFont("Arial", 18))
        self.layout.addWidget(self.label)

        self.single_radio = QRadioButton("Singleplayer")
        self.multi_radio = QRadioButton("Multiplayer")
        self.multi_radio.setChecked(True)  # Default to Long

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.single_radio)
        radio_layout.addWidget(self.multi_radio)
        self.layout.addLayout(radio_layout)

        #input field for name
        self.label = QLabel("Name:", self)
        self.label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.label)
        self.inputField = QLineEdit(self)
        self.inputField.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.inputField)
        
        self.label = QLabel("Voluntary Fields", self)
        self.label.setFont(QFont("Arial", 18))
        self.layout.addWidget(self.label)
        #input field for game speed
        self.label = QLabel("Speed Multiplier:", self)
        self.label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.label)
        self.inputField_speed = QLineEdit(self)
        self.inputField_speed.setFont(QFont("Arial", 12))
        self.inputField_speed.setText("60")
        self.layout.addWidget(self.inputField_speed)
        
        #input field for game duration
        self.label = QLabel("Game Duration in Minutes:", self)
        self.label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.label)
        self.inputField_duration = QLineEdit(self)
        self.inputField_duration.setFont(QFont("Arial", 12))
        self.inputField_duration.setText("10")
        self.layout.addWidget(self.inputField_duration)
        
        #input field for start date in yy-mm-dd
        self.label = QLabel("Start Date(between 2022-2024) in 'yyyy-mm-dd HH-MM':", self)
        self.label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.label)
        self.inputField_start = QLineEdit(self)
        self.inputField_start.setFont(QFont("Arial", 12))
        self.inputField_start.setText("2022-08-10 00:00")
        self.layout.addWidget(self.inputField_start)

        self.button = QPushButton("Start", self)
        self.button.setFont(QFont("Arial", 12))
        self.button.clicked.connect(self.resume)
        
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)
        self.setWindowTitle('Name Input Dialog')

    def resume(self):
        global pvp
        name = self.inputField.text()
        #try & except as duration & start_date & speed-multiplier are not mandatory
        try:
            duration = float(self.inputField_duration.text())
            Game.duration = int(duration)
        except: pass
        try: 
             start_date = self.inputField_start.text()
             Game.start_date = start_date
        except: pass
        try: 
             speed = float(self.inputField_speed.text())
             Game.speed_factor = int(speed)
        except: pass
        
        if name:
            user1.name = name

        if self.single_radio.isChecked():
            pvp = False
            self.close()
        elif self.multi_radio.isChecked():
            pvp = True
            self.close()

            self.lobby = LobbyWindow()
            self.lobby.show()   
            
#Window for the Lobby, shows all Players in the lobby
class LobbyWindow(QWidget):

    start_game_signal = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lobby")
        self.setGeometry(100, 100, 400, 200)
        self.initUI()
        
    def initUI(self):
        global client

        self.layout = QVBoxLayout()
        self.label = QLabel("Welcome to the Lobby!", self)
        self.label.setFont(QFont("Arial", 14))
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        client = GameClient(user1.name)
        self.start_game_signal.connect(self.close)
        threading.Thread(target=self.joined, args=(self.label,)).start()
        
        self.ready_button = QPushButton("Ready", self)
        self.ready_button.clicked.connect(self.send_ready_status)
        self.layout.addWidget(self.ready_button)

        self.ready_label = QLabel("", self)
        self.ready_label.setFont(QFont("Arial", 17))
        self.layout.addWidget(self.ready_label)
        #self.close()
    
    def send_ready_status(self):
        client.send_ready_status()
        self.ready_button.hide()
        self.ready_label.setText("You are ready!")

    def joined(self, label):
        global client
        data = {
            'type': "lobby",
            'name': user1.name
        }
        client.send(json.dumps(data).encode('utf-8'))
        
        for message in client.receive():
            if 'players' in message:
                players = message['players']
                playerstring = " \n ".join(players)
                label.setText(f"Players:\n{playerstring}")
            elif 'start_game' in message and message['start_game']:
                print("starting game")
                self.start_game_signal.emit()
                break



# layout definieren, dass Benutzer Daten am oberen Rand darstellt
app = QApplication([])
ex = NameInputDialog()
ex.show()
app.exec_()

window = QMainWindow()
layout = QVBoxLayout()
widget = QWidget()
window.resize(800, 500)
layout.setContentsMargins(0, 0, 0, 0)

#Label für timer
timerlabel = QLabel(f"Time left: ")
timerlabel.setStyleSheet("""
    font-size: 28px;
    font-weight: 600;
    color: #FFFFFF;
    padding: 12px 15px;
    background-color: #1F1F1F;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    min-height: 40px;
    qproperty-alignment: 'AlignCenter';
""")
layout.addWidget(timerlabel)

# Label for current Portfolio Value
pvlabel = QLabel(f"Portfolio Value: {cash}")
pvlabel.setWordWrap(True)
pvlabel.setStyleSheet("""
    font-size: 28px;
    font-weight: 600;
    color: #FFFFFF;
    padding: 12px 15px;
    background-color: #1F1F1F;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    min-height: 40px;
    qproperty-alignment: 'AlignCenter';
""")

# Label for available cash
cashlabel = QLabel(f"Cash: {cash}")
cashlabel.setWordWrap(True)
cashlabel.setStyleSheet("""
    font-size: 28px;
    font-weight: 600;
    color: #FFFFFF;
    padding: 12px 15px;
    background-color: #1F1F1F;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    min-height: 40px;
    qproperty-alignment: 'AlignCenter';
""")

# Label for the number of open positions
positions_label = QLabel(f"Open Positions: 0")
positions_label.setWordWrap(True)
positions_label.setStyleSheet("""
    font-size: 28px;
    font-weight: 600;
    color: #FFFFFF;
    padding: 12px 15px;
    background-color: #1F1F1F;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    min-height: 40px;
    qproperty-alignment: 'AlignCenter';
""")

# Label to display total PNL
pnllabel = QLabel(f"{stock} unrealized PNL: 0")
pnllabel.setWordWrap(True)
pnllabel.setStyleSheet("""
    font-size: 28px;
    font-weight: 600;
    color: #FFFFFF;
    padding: 12px 15px;
    background-color: #1F1F1F;
    border: 2px solid #FFFFFF;
    border-radius: 8px;
    min-height: 40px;
    qproperty-alignment: 'AlignCenter';
""")

text_layout = QHBoxLayout()

text_layout.addWidget(pvlabel)
text_layout.addWidget(cashlabel)
text_layout.addWidget(pnllabel)
text_layout.addWidget(positions_label)

layout.addLayout(text_layout,1)

chart = QtChart(widget)
chart.topbar.menu(
    name='timemenu',
    options=['1min', '10min', '30min', '1h', '4h'],
    default='1min',
    func=timechange
    )

chart.topbar.switcher(
    name='stock_menu',
    options=("EUR/USD", "BTC/USD"),
    default=stock,
    func=stockchange
    )
#set chart data
chart.set(Data_df)

chalayout = QHBoxLayout()
chalayout.addWidget(chart.get_webview())

layout.addLayout(chalayout,9)

# Create the buy and sell buttons
buy_button = QPushButton("Buy")
sell_button = QPushButton("Sell")

btn_layout = QHBoxLayout()

# Add buttons to the layout
btn_layout.addWidget(buy_button)
btn_layout.addWidget(sell_button)

buy_button.setStyleSheet("""
    QPushButton {
        background-color: green;
        color: white;
        font-size: 18px;
        padding: 10px; 
        border: none;  
    }
    QPushButton:hover {
        background-color: darkgreen; 
    }
    QPushButton:pressed {
        background-color: lightgreen; 
    }
""")
sell_button.setStyleSheet("""
    QPushButton {
        background-color: red;
        color: white;
        font-size: 18px;
        padding: 10px;  
        border: none; 
    }
    QPushButton:hover {
        background-color: darkred;  
    }
    QPushButton:pressed {
        background-color: orange; 
    }
""")

layout.addLayout(btn_layout)


buy_button.clicked.connect(lambda: buy(user=user1, ticker=stock))
#using lambda because it makes it possible to pass a function with arguments as an argument
sell_button.clicked.connect(lambda: sell(user=user1, ticker=stock))

#create a widget that displays position information and pops up when a button is clicked
class Positions_Window(QDialog):
    def __init__(self, positions):
        super().__init__()
        self.positions = positions
        self.setWindowTitle("Positions")
        self.setGeometry(150, 150, 300, 200)
        self.main_layout = QVBoxLayout()
        
        # Create a horizontal layout for all positions
        self.positions_layout = QHBoxLayout()
        self.main_layout.addLayout(self.positions_layout)
        
        # Start a timer to update the window every second (500 ms)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(500)  # Update every 0.5 second
        
        self.update_labels()  # Initial update
    
    def update_labels(self):
        # Clear existing positions layout
        while self.positions_layout.count():
            item = self.positions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Create a QLabel for when there are no open positions
        if not self.positions:
            label = QLabel(f"You have no open positions!")
            self.positions_layout.addWidget(label)
        else:
            for position in self.positions.values():
                # Create a vertical layout for each position's details
                position_layout = QVBoxLayout()
                
                # Populate the vertical layout with position data
                label_data = [
                    (position.ticker, QLabel, "header"),
                    ("Current Data", QLabel, "small header"),
                    (f"Position size: {position.total}", QLabel, "normal"),
                    (f"PNL: {position.pnl}", QLabel, "pnl_positiv" if position.pnl >= 0 else "pnl_negativ"),
                    (f"Preis: {position.price}", QLabel, "normal"),
                    ("Data at Opening", QLabel, "small header"),
                    (f"Preis: {position.price_whenopened}", QLabel, "normal"),
                    (f"Position size: {position.total_whenopened}", QLabel, "normal"),
                    (f"Margin: {position.margin}", QLabel, "normal"),
                    (f"Quantity: {position.quantity}", QLabel, "normal"),
                    (f"Type: {position.type}", QLabel, "normal"),
                    (f"Leverage: {position.leverage}", QLabel, "normal"),
                    (f"Liquidation Price: {position.liquidation_price}", QLabel, "normal")
                ]
                
                for text, label_class, type in label_data:
                    label = label_class(text)
                    if type == "header":
                        font_size = "18px"
                        margin = "2px"
                        background_color = "#34495e"
                    elif type == "small header":
                        font_size = "14px"
                        margin = "1px"
                        background_color = "#34495e"
                    elif type == "pnl_positiv":
                        font_size = "12px"
                        margin = "0.5px"
                        background_color = "#2ecc71"
                    elif type == "pnl_negativ":
                        font_size = "12px"
                        margin = "0.5px"
                        background_color = "#e74c3c"
                    else:
                        font_size = "12px"
                        margin = "0.5px"
                        background_color = "#34495e"
                    
                    label.setStyleSheet(f"""
                    font-size: {font_size};
                    font-weight: bold;
                    color: white;
                    background-color: {background_color};
                    padding: 2px;
                    border-radius: 5px;
                    margin: {margin};
                """)
                    position_layout.addWidget(label)
                
                # Add the position's vertical layout to the horizontal layout
                self.positions_layout.addLayout(position_layout)
        
        self.setLayout(self.main_layout)

def open_positions_widget(window):
    # Create an instance of the new widget and show it
    window.new_widget = Positions_Window(user1.positions)
    window.new_widget.show()


def end_screen():
    global pvp

    new_window = QDialog()
    new_window.setWindowTitle("Time is up!")
    new_window.resize(400, 300)

    layout = QVBoxLayout()
    
    # Adding input widgets for margin and leverage:
    label1 = QLabel(f"You've made: {(user1.capital-100000):.3f} dollars ")
    layout.addWidget(label1)

    #Dictionary nach val sortieren
    sorted_table = dict(sorted(table.items(), key=lambda item: item[1], reverse=True))

    if pvp == True:
        stats = ""
        for key, val in sorted_table.items():
            stats += f"{key} has made {val:.3f} dollars\n"
        playertable = QLabel(stats)
        playertable.setTextFormat(Qt.PlainText)
        layout.addWidget(playertable)
    
    new_window.setLayout(layout)
    new_window.exec_()

#class for timer countdown
#When the thread closes, the game over screen is opened and running is set to False
class CountdownWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, seconds):
        super().__init__()
        self.seconds = seconds

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 1 second interval

    def update_time(self):
        global running
        if self.seconds >= 0 and running:
            mins, secs = divmod(self.seconds, 60)
            timer_text = f'{mins:02d}:{secs:02d}'
            timerlabel.setText(f"Time left: {timer_text}")
            # Emit the finished signal when the countdown is done
            if self.seconds == 0:
                running = False
                self.timer.stop()
                self.finished.emit()
            self.seconds -= 1

    def stop(self):
        self.timer.stop()
      
button_show_positions = QPushButton("Positions: Show More")

button_show_positions.clicked.connect(lambda: open_positions_widget(window))  # Connect the button to the slot
text_layout.addWidget(button_show_positions)

widget.setLayout(layout)
window.setCentralWidget(widget)
window.show()

x = threading.Thread(target= lambda: update(user1))
x.start()

if pvp:
    if client == None:
        client = GameClient(user1.name)
    client.start()
else:
    worker = CountdownWorker(Game.duration * 60)  # Set countdown time in seconds
    worker.finished.connect(end_screen)

    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.start)
    thread.start()

app.exec_()
running = False
x.join()

if pvp:
    client.end()