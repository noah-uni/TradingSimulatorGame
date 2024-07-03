import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Trading Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font
font = pygame.font.Font(None, 32)

# Ticker input field
ticker_input = ""
input_rect = pygame.Rect(200, 200, 200, 32)
active = False

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Process the ticker_input (e.g., fetch data, execute trade)
                print("Ticker entered:", ticker_input)
                ticker_input = ""
            elif event.key == pygame.K_BACKSPACE:
                ticker_input = ticker_input[:-1]
            else:
                ticker_input += event.unicode
        
        # Toggle active state for input field
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = not active
            else:
                active = False

    # Draw input field
    pygame.draw.rect(screen, BLACK, input_rect, 2)
    text_surface = font.render(ticker_input, True, BLACK)
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
