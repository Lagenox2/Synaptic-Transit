import pygame
from screeninfo import get_monitors
import sys
import math

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

black = (0, 0, 0)
white = (250, 250, 250)
hover = (190, 20, 250)
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
    def __init__(self, text, center):
        self.text = text
        self.rect = pygame.Rect(0, 0, 320, 70)
        self.rect.center = center

    def draw(self, surface):
        color = hover if self.rect.collidepoint(pygame.mouse.get_pos()) else white
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        surface.blit(
            button_font.render(self.text, True, black),
            button_font.render(self.text, True, black).get_rect(center=self.rect.center)
        )

    def clicked(self, e):
        return e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos)

def draw_logo(surface):
    cx, cy = width // 2, height // 2 - 420
    r = 68
    pygame.draw.rect(surface, white, pygame.Rect(cx - r, cy - r, r * 2, r * 2), 8, border_radius=10)
    pygame.draw.circle(surface, white, (cx, cy), r, 8)
    pygame.draw.polygon(surface, white,
        [(cx, cy - r), (cx - r, cy + r), (cx + r, cy + r)], 8)

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
        def s(p, a, b): return (p[0]-b[0])*(a[1]-b[1])-(a[0]-b[0])*(p[1]-b[1])
        b1 = s((mx, my), p1, p2) < 0
        b2 = s((mx, my), p2, p3) < 0
        b3 = s((mx, my), p3, p1) < 0
        return b1 == b2 == b3

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

    # connections
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

    # objects
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
        create_visual(c1, "circle", (300, 450)),
        create_visual(c2, "circle", (300, 550)),
        create_visual(r1, "triangle", (700, 500)),
        create_visual(r2, "triangle", (700, 650)),
        create_visual(s1, "square", (1100, 575)),
    ])

def next_turn():
    global turn, client_counter
    turn += 1
    client_counter += 1

    c = Client(f"C{client_counter}")
    network.add_client(c)

    x = 300 + (client_counter % 5) * 100
    y = 500 + (client_counter % 4) * 100

    objects.append(create_visual(c, "circle", (x, y)))


def main():
    new_game_btn = Button("Новая игра", (width // 2, height // 2 + 40))
    exit_btn = Button("Выход", (width // 2, height // 2 + 150))
    next_turn_btn = Button("Следующий ход", (width - 220, height - 80))

    selected = None
    started = False

    while True:
        screen.fill(black)

        if not started:
            draw_logo(screen)
            screen.blit(
                title_font.render("SYNAPTIC TRANSIT", True, white),
                title_font.render("SYNAPTIC TRANSIT", True, white)
                .get_rect(center=(width // 2, height // 2 - 110))
            )
            new_game_btn.draw(screen)
            exit_btn.draw(screen)
        else:
            draw_objects(screen, objects, selected)
            next_turn_btn.draw(screen)
            screen.blit(small_font.render(f"Ход: {turn}", True, white), (20, 20))

        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if not started:
                if new_game_btn.clicked(e):
                    start_game()
                    started = True
                if exit_btn.clicked(e):
                    pygame.quit()
                    sys.exit()

            else:
                if next_turn_btn.clicked(e):
                    next_turn()

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    for obj in objects:
                        if point_in_object(e.pos, obj):
                            if not selected:
                                selected = obj
                            else:
                                if selected != obj:
                                    connect(selected, obj)
                                selected = None
                            break

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
