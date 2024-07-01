import pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
FONT_SIZE = 24
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50

# Initialize Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paper Stock Trading Game")

# Fonts
font = pygame.font.Font(None, FONT_SIZE)

# Game Variables
cash = 10000  # Starting cash
portfolio = {}  # Dictionary to hold stocks and their quantities

# Sample stock prices (in a real game, fetch from an API)
stock_prices = {
    "AAPL": 150.00,
    "GOOGL": 2800.00,
    "TSLA": 700.00
}

# Button Class
class Button:
    def __init__(self, text, x, y, width, height, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        
        label = font.render(self.text, True, TEXT_COLOR)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

# Function to render text
def render_text(text, pos):
    label = font.render(text, True, TEXT_COLOR)
    screen.blit(label, pos)

# Function to buy stocks
def buy_stock(stock):
    global cash
    quantity = 1
    if stock in stock_prices:
        total_cost = stock_prices[stock] * quantity
        if cash >= total_cost:
            cash -= total_cost
            if stock in portfolio:
                portfolio[stock] += quantity
            else:
                portfolio[stock] = quantity
        else:
            print("Not enough cash to buy the stock")
    else:
        print("Stock not found")

# Function to sell stocks
def sell_stock(stock):
    global cash
    quantity = 1
    if stock in portfolio and portfolio[stock] >= quantity:
        total_value = stock_prices[stock] * quantity
        cash += total_value
        portfolio[stock] -= quantity
        if portfolio[stock] == 0:
            del portfolio[stock]
    else:
        print("Not enough stock to sell or stock not found")

# Main Game Loop
def main():
    global cash, portfolio
    
    # Create buttons
    buttons = []
    y_pos = 60
    for stock in stock_prices:
        buy_button = Button(f"Buy {stock}", 600, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT, lambda s=stock: buy_stock(s))
        sell_button = Button(f"Sell {stock}", 710, y_pos, BUTTON_WIDTH, BUTTON_HEIGHT, lambda s=stock: sell_stock(s))
        buttons.append(buy_button)
        buttons.append(sell_button)
        y_pos += 60

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            for button in buttons:
                button.is_clicked(event)

        # Clear screen
        screen.fill(BACKGROUND_COLOR)

        # Render cash and portfolio
        render_text(f"Cash: ${cash:.2f}", (20, 20))
        y_pos = 60
        for stock, quantity in portfolio.items():
            render_text(f"{stock}: {quantity} shares", (20, y_pos))
            y_pos += 30

        # Render available stocks and their prices
        y_pos = 60
        for stock, price in stock_prices.items():
            render_text(f"{stock}: ${price:.2f}", (400, y_pos))
            y_pos += 60

        # Draw buttons
        for button in buttons:
            button.draw(screen)

        # Update display
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
