import pygame
from screeninfo import get_monitors
import sys
import math
import random
import data

from network import Network
from client import Client
from router import Router
from server import Server


pygame.init()
pygame.font.init()

data.turn = 1
data.client_counter = 2

class Button:
    def __init__(self, text, center_y):
        self.current_color = data.white
        self.text = text
        self.width = 420
        self.height = 80
        self.rect = pygame.Rect((data.width - self.width) // 2, center_y - self.height // 2, self.width,self.height)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        n = data.delta
        target_color = data.hover if self.rect.collidepoint(mouse_pos) else data.white
        current = self.current_color
        color = tuple(current[i] + n if current[i] < target_color[i] else current[i] - n if current[i] > target_color[i] else current[i] for i in range(3))
        self.current_color = color
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        label = data.button_font.render(self.text, True, data.black)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_logo(surface):
    cx, cy = data.width // 2, data.height // 2 - 420
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
    x, y = obj['position']

    if obj['type'] == 'circle':
        return math.hypot(mx - x, my - y) <= obj['radius']

    if obj['type'] == 'square':
        s = obj['size'] // 2
        return x - s <= mx <= x + s and y - s <= my <= y + s

    if obj['type'] == 'triangle':
        h = obj['size'] // 2
        p1 = (x, y - h)
        p2 = (x - h, y + h)
        p3 = (x + h, y + h)

        def s(p, a, b): return (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])

        b1 = s((mx, my), p1, p2) < 0
        b2 = s((mx, my), p2, p3) < 0
        b3 = s((mx, my), p3, p1) < 0
        return b1 == b2 == b3
    return None


def find_safe_position(objects, min_distance=75, attempts=100):
    for _ in range(attempts):
        x = random.randint(100, data.width - 100)
        y = random.randint(100, data.height - 100)
        safe = True

        for obj in objects:
            ox, oy = obj['position']
            distance = math.hypot(x - ox, y - oy)
            if distance < min_distance:
                safe = False
                break

        if safe:
            return (x, y)

    return (random.randint(100, data.width - 100), random.randint(100, data.height - 100))


def create_visual(node, obj_type, pos):
    return {
        'name': node.name,
        'node': node,
        'type': obj_type,
        'position': pos,
        'connections': [],
        'radius': 32,
        'size': 70,
        'display_text': node.name,
        'spawn': 0.0
    }


def spawn_router_near(obj):
    r = Router(f'R{len(data.network.routers) + 1}')
    data.network.add_router(r)
    x, y = obj['position']
    data.objects.append(create_visual(r, 'triangle', (x + 180, y + 60)))


def disconnect(a, b):
    a_name, b_name = a['name'], b['name']
    a['connections'] = [conn for conn in a['connections'] if conn['to'] != b_name]
    b['connections'] = [conn for conn in b['connections'] if conn['to'] != a_name]
    na, nb = a['node'], b['node']
    if isinstance(na, Client) and isinstance(nb, Router):
        na.disconnect(nb)
    elif isinstance(na, Router) and isinstance(nb, Client):
        nb.disconnect(na)
    elif isinstance(na, Router) and isinstance(nb, Server):
        nb.disconnect(na)
    elif isinstance(na, Server) and isinstance(nb, Router):
        na.disconnect(nb)


def connect(a, b):
    na, nb = a['node'], b['node']
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
    a['connections'].append({'to': b['name'], 'progress': 0.0, 'pulse': 0.0, 'path': []})
    b['connections'].append({'to': a['name'], 'progress': 1.0, 'pulse': 0.0, 'path': []})


def draw_objects(surface, objects, selected, dragging, start_point, path_points):
    for obj in objects:
        for conn in obj['connections']:
            target = next(o for o in objects if o['name'] == conn['to'])
            x1, y1 = obj['position']
            x2, y2 = target['position']
            conn['progress'] = min(1.0, conn['progress'] + 0.035)
            conn['pulse'] += 0.2
            px = x1 + (x2 - x1) * conn['progress']
            py = y1 + (y2 - y1) * conn['progress']
            w = 3 + int(abs(math.sin(conn['pulse'])) * 2)
            pygame.draw.line(surface, data.white, (x1, y1), (px, py), w)

    if dragging and start_point and len(path_points) >= 1:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        points = [start_point] + path_points + [(mouse_x, mouse_y)]
        for i in range(len(points) - 1):
            pygame.draw.line(surface, data.white, points[i], points[i + 1], 3)
        if len(path_points) > 0:
            pygame.draw.circle(surface, data.white, points[-1], 6, 2)

    for obj in objects:
        obj['spawn'] = min(1.0, obj['spawn'] + 0.05)
        scale = obj['spawn']
        x, y = obj['position']
        node = obj['node']
        color = data.hover if selected and selected['name'] == obj['name'] else data.white
        if isinstance(node, Router) and node.recieving_now >= node.maximum_recieving:
            color = data.bad
        if obj['type'] == 'circle':
            pygame.draw.circle(surface, color, (int(x), int(y)), int(obj['radius'] * scale), 4)
        elif obj['type'] == 'square':
            s = int(obj['size'] * scale)
            r = pygame.Rect(0, 0, s, s)
            r.center = (x, y)
            pygame.draw.rect(surface, color, r, 4)
        elif obj['type'] == 'triangle':
            h = int(obj['size'] * scale) // 2
            pygame.draw.polygon(surface, color, [(x, y - h), (x - h, y + h), (x + h, y + h)], 4)
        if scale > 0.85:
            surface.blit(data.object_font.render(obj['display_text'], True, data.white), data.object_font.render(obj['display_text'], True, data.white).get_rect(center=(x, y)))
            if isinstance(node, Router):
                txt = f'{node.recieving_now} / {node.maximum_recieving}'
                surface.blit(data.small_font.render(txt, True, color), (x - 20, y + obj['size'] // 2 + 6))


def start_game():
    global turn, client_counter
    turn = 1
    client_counter = 2
    data.network.clients.clear()
    data.network.routers.clear()
    data.network.servers.clear()
    data.objects.clear()
    c1 = Client('C1')
    c2 = Client('C2')
    r1 = Router('R1')
    r2 = Router('R2')
    s1 = Server('S1')
    data.network.add_client(c1)
    data.network.add_client(c2)
    data.network.add_router(r1)
    data.network.add_router(r2)
    data.network.add_server(s1)
    pos1 = find_safe_position(data.objects)
    pos2 = find_safe_position(data.objects)
    pos3 = find_safe_position(data.objects)
    pos4 = find_safe_position(data.objects)
    pos5 = find_safe_position(data.objects)
    data.objects.extend([
        create_visual(c1, 'circle', pos1),
        create_visual(c2, 'circle', pos2),
        create_visual(r1, 'triangle', pos3),
        create_visual(r2, 'triangle', pos4),
        create_visual(s1, 'square', pos5),
    ])


def next_turn():
    global turn, client_counter
    turn += 1
    client_counter += 1
    c = Client(f'C{client_counter}')
    data.network.add_client(c)
    x, y = find_safe_position(data.objects)
    data.objects.append(create_visual(c, 'circle', (x, y)))
    if client_counter % 7 == 0:
        r = Router(f'R{int(client_counter / 7 + 2)}')
        data.network.add_router(r)
        x, y = find_safe_position(data.objects)
        data.objects.append(create_visual(r, 'triangle', (x, y)))


def main():
    new_game_btn = Button('Новая игра', data.height // 2 + 40)
    exit_btn = Button('Выход', data.height // 2 + 150)
    next_turn_btn = Button('Следующий ход', data.height // 2 + 150)
    next_turn_btn.rect.center = (data.width - 220, data.height - 80)
    selected = None
    started = False
    dragging = False
    start_point = None
    path_points = []

    while True:
        data.screen.fill(data.black)
        if not started:
            draw_logo(data.screen)
            title = data.title_font.render('Synaptic Transit', True, data.white)
            title_rect = title.get_rect(center=(data.width // 2, data.height // 2 - 110))
            data.screen.blit(title, title_rect)
            new_game_btn.draw(data.screen)
            exit_btn.draw(data.screen)
        else:
            draw_objects(data.screen, data.objects, selected, dragging, start_point, path_points)
            next_turn_btn.draw(data.screen)
            data.screen.blit(data.small_font.render(f'Ход: {turn}', True, data.white), (20, 20))

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
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not dragging:
                            clicked = False
                            for obj in data.objects:
                                if point_in_object(event.pos, obj):
                                    if not selected:
                                        selected = obj
                                    else:
                                        if selected != obj:
                                            connect(selected, obj)
                                        selected = None
                                    clicked = True
                                    break
                            if not clicked:
                                dragging = True
                                start_point = event.pos
                                path_points = []
                        else:
                            if start_point:
                                for obj in data.objects:
                                    if point_in_object(event.pos, obj):
                                        if selected and selected != obj:
                                            connect(selected, obj)
                                        selected = None
                                        break
                                else:
                                    path_points.append(event.pos)
                    elif event.button == 3:
                        for obj in data.objects:
                            if point_in_object(event.pos, obj):
                                for conn in obj['connections']:
                                    target = next(o for o in data.objects if o['name'] == conn['to'])
                                    disconnect(obj, target)
                                    selected = None
                                    break
                                else:
                                    selected = None
                                break
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if dragging:
                        dragging = False
                        start_point = None
                        path_points = []

        pygame.display.flip()
        data.clock.tick(120)


if __name__ == '__main__':
    main()