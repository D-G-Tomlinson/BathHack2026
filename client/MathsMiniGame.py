import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Maths Mini Game")

# TODO: actually build this
# placeholder for now so the menu doesn't crash

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()