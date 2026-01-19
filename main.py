import pygame
from screeninfo import get_monitors


for m in get_monitors():
    print(f"Монитор: {m.name}, Разрешение: {m.width}x{m.height}, Рабочая область: {m.width}x{m.height}")
    WIDTH = m.width
    HEIGHT = m.height

pygame.init()
pygame.mixer.init()  # для звука
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Synaptic Transit")
# clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
