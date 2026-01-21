import pygame
from screeninfo import get_monitors
import sys
import math
import config

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
object_font = pygame.font.SysFont("arial", 24, bold=True)

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

def draw_objects(surface, objects):
    # обновляем волны
    config.update_waves()

    mouse_pos = pygame.mouse.get_pos()

    # сначала волны
    for obj in objects:
        if obj["type"] == "circle" and "waves" in obj:
            x, y = obj["position"]
            for wave in obj["waves"]:
                if wave["active"] and wave["opacity"] > 0:
                    pygame.draw.circle(surface, wave["color"], (int(x), int(y)), int(wave["radius"]), 2)

    # соединения
    for obj in objects:
        x1, y1 = obj["position"]
        for conn_name in obj.get("connections", []):
            for target in objects:
                if target["name"] == conn_name:
                    x2, y2 = target["position"]
                    pygame.draw.line(surface, white, (x1, y1), (x2, y2), 3)
                    break

    # объекты с текстом
    for obj in objects:
        x, y = obj["position"]

        # проверка наведения
        config.check_hover(mouse_pos, obj)
        color = config.get_hover_color(obj)

        if obj["type"] == "circle":
            pygame.draw.circle(surface, color, (int(x), int(y)), obj["radius"], 4)

            # ТЕКСТ ВНУТРИ
            text = object_font.render(obj["display_text"], True, white)
            text_rect = text.get_rect(center=(int(x), int(y)))
            surface.blit(text, text_rect)

        elif obj["type"] == "square":
            size = obj["size"]
            rect = pygame.Rect(0, 0, size, size)
            rect.center = (int(x), int(y))
            pygame.draw.rect(surface, color, rect, 4)

            # ТЕКСТ ВНУТРИ
            text = object_font.render(obj["display_text"], True, white)
            text_rect = text.get_rect(center=(int(x), int(y)))
            surface.blit(text, text_rect)

        elif obj["type"] == "triangle":
            size = obj["size"]
            half = size // 2
            points = [
                (x, y - half),
                (x - half, y + half),
                (x + half, y + half)
            ]
            pygame.draw.polygon(surface, color, points, 4)

            # ТЕКСТ ВНУТРИ (немного выше)
            text = object_font.render(obj["display_text"], True, white)
            text_rect = text.get_rect(center=(int(x), int(y - half // 3)))
            surface.blit(text, text_rect)

def main():
    new_game_btn = Button("Новая игра", height // 2 + 40)
    exit_btn = Button("Выход", height // 2 + 150)

    game_started = False

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
            # вставить уровень 1
            objects = config.get_all_objects()
            draw_objects(screen, objects)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if not game_started and new_game_btn.clicked(event):
                # сброс и генерация
                config.reset_all()

                # генерируем объекты
                for _ in range(5):
                    config.randspawn(1.0, 1, True)
                for _ in range(2):
                    config.randspawn(1.0, 2)
                config.randspawn(1.0, 3)

                game_started = True
            if not game_started and exit_btn.clicked(event):
                running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()