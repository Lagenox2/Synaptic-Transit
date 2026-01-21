import pygame
from screeninfo import get_monitors
import sys
import math
import random

from traitlets import Union

from network import Network
from client import Client
from router import Router
from server import Server

pygame.init()
pygame.font.init()

monitor = get_monitors()[0]
width, height = monitor.width, monitor.height

screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption("Synaptic Transit")

# ДЕЛЬТА ТОЛЬКО КРАТНА 10 ИНАЧЕ КИРДЫК!
delta = 10
black = (0 * delta, 0 * delta, 0 * delta)
white = (25 * delta, 25 * delta, 25 * delta)
hover = (19 * delta, 2 * delta, 25 * delta)
bad = (255, 80, 80)
title_font = pygame.font.SysFont("arial", 64, bold=True)
button_font = pygame.font.SysFont("arial", 32)
object_font = pygame.font.SysFont("arial", 22, bold=True)
small_font = pygame.font.SysFont("arial", 18)

clock = pygame.time.Clock()

network = Network()
objects = []

turn = 1
client_counter = 2


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


def point_in_object(pos, obj):
    mx, my = pos
    x, y = obj["position"]

    if obj["type"] == "circle":
        return math.hypot(mx - x, my - y) <= obj["radius"]

    if obj["type"] == "square":
        s = obj["size"] // 2
        return x - s <= mx <= x + s and y - s <= my <= y + s

    if obj["type"] == "triangle":
        h = obj["size"] // 2
        p1 = (x, y - h)
        p2 = (x - h, y + h)
        p3 = (x + h, y + h)

        def s(p, a, b): return (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])

        b1 = s((mx, my), p1, p2) < 0
        b2 = s((mx, my), p2, p3) < 0
        b3 = s((mx, my), p3, p1) < 0
        return b1 == b2 == b3
    return None


def create_visual(node, obj_type, pos):
    return {
        "name": node.name,
        "node": node,
        "type": obj_type,
        "position": pos,
        "connections": [],
        "radius": 32,
        "size": 70,
        "display_text": node.name,
        "spawn": 0.0
    }


def spawn_router_near(obj):
    r = Router(f"R{len(network.routers) + 1}")
    network.add_router(r)
    x, y = obj["position"]
    objects.append(create_visual(r, "triangle", (x + 180, y + 60)))


def connect(a, b):
    na, nb = a["node"], b["node"]

    if isinstance(na, Client) and isinstance(nb, Router):
        if not nb.can_accept():
            spawn_router_near(a)
            return
        na.connect(nb)

    elif isinstance(na, Router) and isinstance(nb, Server):
        if not na.can_accept():
            return
        nb.connect(na)
    else:
        return

    a["connections"].append({"to": b["name"], "progress": 0.0, "pulse": 0.0})
    b["connections"].append({"to": a["name"], "progress": 1.0, "pulse": 0.0})


def draw_objects(surface, objects, selected):
    for obj in objects:
        for conn in obj["connections"]:
            target = next(o for o in objects if o["name"] == conn["to"])
            x1, y1 = obj["position"]
            x2, y2 = target["position"]

            conn["progress"] = min(1.0, conn["progress"] + 0.035)
            conn["pulse"] += 0.2

            px = x1 + (x2 - x1) * conn["progress"]
            py = y1 + (y2 - y1) * conn["progress"]

            w = 3 + int(abs(math.sin(conn["pulse"])) * 2)
            pygame.draw.line(surface, white, (x1, y1), (px, py), w)

    for obj in objects:
        obj["spawn"] = min(1.0, obj["spawn"] + 0.05)
        scale = obj["spawn"]

        x, y = obj["position"]
        node = obj["node"]

        color = hover if selected and selected["name"] == obj["name"] else white
        if isinstance(node, Router) and node.recieving_now >= node.maximum_recieving:
            color = bad

        if obj["type"] == "circle":
            pygame.draw.circle(surface, color, (int(x), int(y)),
                               int(obj["radius"] * scale), 4)

        elif obj["type"] == "square":
            s = int(obj["size"] * scale)
            r = pygame.Rect(0, 0, s, s)
            r.center = (x, y)
            pygame.draw.rect(surface, color, r, 4)

        elif obj["type"] == "triangle":
            h = int(obj["size"] * scale) // 2
            pygame.draw.polygon(surface, color,
                                [(x, y - h), (x - h, y + h), (x + h, y + h)], 4)

        if scale > 0.85:
            surface.blit(
                object_font.render(obj["display_text"], True, white),
                object_font.render(obj["display_text"], True, white)
                .get_rect(center=(x, y))
            )

            if isinstance(node, Router):
                txt = f"{node.recieving_now} / {node.maximum_recieving}"
                surface.blit(small_font.render(txt, True, color),
                             (x - 20, y + obj["size"] // 2 + 6))


def start_game():
    global turn, client_counter
    turn = 1
    client_counter = 2

    network.clients.clear()
    network.routers.clear()
    network.servers.clear()
    objects.clear()

    c1 = Client("C1")
    c2 = Client("C2")
    r1 = Router("R1")
    r2 = Router("R2")
    s1 = Server("S1")

    network.add_client(c1)
    network.add_client(c2)
    network.add_router(r1)
    network.add_router(r2)
    network.add_server(s1)

    objects.extend([
        create_visual(c1, "circle", (random.randint(100, 1820), random.randint(100, 980))),
        create_visual(c2, "circle", (random.randint(100, 1820), random.randint(100, 980))),
        create_visual(r1, "triangle", (random.randint(100, 1820), random.randint(100, 980))),
        create_visual(r2, "triangle", (random.randint(100, 1820), random.randint(100, 980))),
        create_visual(s1, "square", (random.randint(100, 1820), random.randint(100, 980))),
    ])


def next_turn():
    global turn, client_counter
    turn += 1
    client_counter += 1

    c = Client(f"C{client_counter}")
    network.add_client(c)

    if client_counter % 7 == 0:
        r = Router(f"R{int(client_counter / 7 + 2)}")
        network.add_router(r)
        x = random.randint(100, 1820)
        y = random.randint(100, 980)

        objects.append(create_visual(r, "triangle", (x, y)))

    x = random.randint(100, 1820)
    y = random.randint(100, 980)

    objects.append(create_visual(c, "circle", (x, y)))


def main():
    new_game_btn = Button("Новая игра", height // 2 + 40)
    exit_btn = Button("Выход", height // 2 + 150)

    next_turn_btn = Button("Следующий ход", height // 2 + 150)
    next_turn_btn.rect.center = (width - 220, height - 80)

    selected = None
    started = False

    while True:
        screen.fill(black)

        if not started:
            draw_logo(screen)
            title = title_font.render("Synaptic Transit", True, white)
            title_rect = title.get_rect(center=(width // 2, height // 2 - 110))
            screen.blit(title, title_rect)
            new_game_btn.draw(screen)
            exit_btn.draw(screen)
        else:
            draw_objects(screen, objects, selected)
            next_turn_btn.draw(screen)
            screen.blit(small_font.render(f"Ход: {turn}", True, white), (20, 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if not started:
                if new_game_btn.clicked(event):
                    start_game()
                    started = True
                if exit_btn.clicked(event):
                    pygame.quit()
                    sys.exit()
            else:
                if next_turn_btn.clicked(event):
                    next_turn()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for obj in objects:
                        if point_in_object(event.pos, obj):
                            if not selected:
                                selected = obj
                            else:
                                if selected != obj:
                                    connect(selected, obj)
                                selected = None
                            break

        pygame.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()