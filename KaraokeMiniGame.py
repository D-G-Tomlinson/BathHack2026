import pygame

# Initialize pygame
pygame.init()

# Create window
screen = pygame.display.set_mode((800, 600))

# Set window title
pygame.display.set_caption("Karaoke Mini Game")

# Main loop (keeps window open)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

# Quit pygame
pygame.quit()