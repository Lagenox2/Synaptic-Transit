import pygame
from screeninfo import get_monitors
import sys
import math
import json

pygame.init()
pygame.font.init()

monitor = get_monitors()[0]
width, height = monitor.width, monitor.height

screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("Synaptic Transit")

delta = 10
black = (0 * delta, 0 * delta, 0 * delta)
white = (25 * delta, 25 * delta, 25 * delta)
hover = (19 * delta, 2 * delta, 25 * delta)

title_font = pygame.font.SysFont("arial", 64, bold=True)
button_font = pygame.font.SysFont("arial", 32)

clock = pygame.time.Clock()

class Button:
    def __init__(self, text, center_y):
        self.current_color = white
        self.text = text
        self.width = 420
        self.height = 80
        self.rect = pygame.Rect(
            (width - self.width) // 2,
            center_y - self.height // 2,
            self.width,
            self.height
        )

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        n = delta
        target_color = hover if self.rect.collidepoint(mouse_pos) else white
        current = self.current_color
        color = tuple(
            current[i] + n if current[i] < target_color[i] else
            current[i] - n if current[i] > target_color[i] else
            current[i]
            for i in range(3)
        )
        self.current_color = color
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        label = button_font.render(self.text, True, black)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def draw_logo(surface):
    cx, cy = width // 2, height // 2 - 420
    line = 8
    color = (250, 250, 250)
    square_size = 135
    square_rect = pygame.Rect(0, 0, square_size, square_size)
    square_rect.center = (cx, cy)
    pygame.draw.rect(surface, color, square_rect, line, border_radius=10)
    r = square_size / 2
    pygame.draw.circle(surface, color, (cx, cy), int(r), line)
    points = []
    for i in range(3):
        angle = math.radians(90 + i * 120)
        x = cx + r * math.cos(angle) * 0.94
        y = cy + r * math.sin(angle) * 0.94
        points.append((x, y))
    pygame.draw.polygon(surface, color, points, line)

def load_config(path="config.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["shapes"]

def draw_scheme(surface, shapes):
    shape_map = {s["name"]: s for s in shapes}

    for s in shapes:
        x1, y1 = s["position"]
        for t in s["connections"]:
            if t in shape_map:
                x2, y2 = shape_map[t]["position"]
                pygame.draw.line(surface, white, (x1, y1), (x2, y2), 3)

    for s in shapes:
        x, y = s["position"]
        if s["type"] == "circle":
            pygame.draw.circle(surface, white, (x, y), 28, 4)
        elif s["type"] == "square":
            rect = pygame.Rect(0, 0, 60, 60)
            rect.center = (x, y)
            pygame.draw.rect(surface, white, rect, 4)
        elif s["type"] == "triangle":
            size = 34
            points = [
                (x, y - size),
                (x - size, y + size),
                (x + size, y + size)
            ]
            pygame.draw.polygon(surface, white, points, 4)

def main():
    new_game_btn = Button("Новая игра", height // 2 + 40)
    exit_btn = Button("Выход", height // 2 + 150)

    game_started = False
    shapes = []

    running = True
    while running:
        screen.fill(black)

        if not game_started:
            draw_logo(screen)
            title = title_font.render("SYNAPTIC TRANSIT", True, white)
            title_rect = title.get_rect(center=(width // 2, height // 2 - 110))
            screen.blit(title, title_rect)
            new_game_btn.draw(screen)
            exit_btn.draw(screen)
        else:
            draw_scheme(screen, shapes)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if not game_started and new_game_btn.clicked(event):
                shapes = load_config()
                game_started = True
            if not game_started and exit_btn.clicked(event):
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
