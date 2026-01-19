import pygame
from screeninfo import get_monitors
import sys
import math

pygame.init()
pygame.font.init()

monitor = get_monitors()[0]
WIDTH, HEIGHT = monitor.width, monitor.height
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Synaptic Transit")

BLACK = (0, 0, 0)
WHITE = (240, 240, 240)
HOVER = (210, 210, 210)

TITLE_FONT = pygame.font.SysFont("comic sans mc", 64, bold=True)
BUTTON_FONT = pygame.font.SysFont("comic sans mc", 32)

clock = pygame.time.Clock()


class Button:
    def __init__(self, text, center_y):
        self.text = text
        self.width = 420
        self.height = 80
        self.rect = pygame.Rect(
            (WIDTH - self.width) // 2,
            center_y - self.height // 2,
            self.width,
            self.height
        )

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = HOVER if self.rect.collidepoint(mouse_pos) else WHITE

        pygame.draw.rect(surface, color, self.rect, border_radius=14)

        label = BUTTON_FONT.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

def draw_logo(surface):
    cx, cy = WIDTH // 2, HEIGHT // 2 - 220

    LINE = 6
    WHITE = (240, 240, 240)

    square_size = 135
    square_rect = pygame.Rect(0, 0, square_size, square_size)
    square_rect.center = (cx, cy)
    pygame.draw.rect(
        surface,
        WHITE,
        square_rect,
        LINE,
        border_radius=10
    )

    R = square_size / 2
    pygame.draw.circle(
        surface,
        WHITE,
        (cx, cy),
        int(R),
        LINE
    )

    points = []
    for i in range(3):
        angle = math.radians(90 + i * 120)
        x = cx + R * math.cos(angle)
        y = cy + R * math.sin(angle)
        points.append((x, y))

    pygame.draw.polygon(
        surface,
        WHITE,
        points,
        LINE
    )



def main():
    new_game_btn = Button("Новая игра", HEIGHT // 2 + 40)
    exit_btn = Button("Выход", HEIGHT // 2 + 150)

    running = True
    while running:
        screen.fill(BLACK)

        draw_logo(screen)

        title = TITLE_FONT.render("SYNAPTIC TRANSIT", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 110))
        screen.blit(title, title_rect)

        new_game_btn.draw(screen)
        exit_btn.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if new_game_btn.clicked(event):
                pass

            if exit_btn.clicked(event):
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()