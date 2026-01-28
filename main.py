import pygame, sys, math, random
import data, Levels.one_text, rendering, config
from object.network import Network
from object.client import Client
from object.router import Router
from object.server import Server
import time

data.network = Network()
one_text = Levels.one_text

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

def spawn_router_near(obj):
    x, y = obj['position']
    new_x, new_y = x + 180, y + 60

    if (data.safe_zone <= new_x <= data.width - data.safe_zone and
            data.safe_zone <= new_y <= data.height - data.safe_zone):
        return config.spawn(new_x, new_y, 'router')

    return config.randspawn('router')

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
    elif isinstance(na, Router) and isinstance(nb, Client):
        if not na.can_accept():
            spawn_router_near(b)
            return
        nb.connect(na)
    elif isinstance(na, Router) and isinstance(nb, Server):
        if not na.can_accept():
            return
        nb.connect(na)
    elif isinstance(na, Server) and isinstance(nb, Router):
        if not nb.can_accept():
            return
        na.connect(nb)
    else:
        return

    a['connections'].append({'to': b['name'], 'progress': 0.0, 'pulse': 0.0, 'path': []})
    b['connections'].append({'to': a['name'], 'progress': 1.0, 'pulse': 0.0, 'path': []})

def check_client_connection(client_obj):
    if not isinstance(client_obj['node'], Client):
        return True

    client_node = client_obj['node']
    required_server = client_obj.get('required_server')

    if not required_server:
        return True

    server_obj = None
    for obj in data.objects:
        if obj['name'] == required_server and isinstance(obj['node'], Server):
            server_obj = obj
            break

    if not server_obj:
        return False

    return client_node.has_path_to(server_obj['node'])

def draw_objects(surface, objects, selected, dragging, start_point, path_points):
    for obj in objects:
        for conn in obj['connections']:
            target = next((o for o in objects if o['name'] == conn['to']), None)
            if not target:
                continue

            x1, y1 = obj['position']
            x2, y2 = target['position']
            conn['progress'] = min(1.0, conn['progress'] + 0.035)
            conn['pulse'] += 0.2

            w = 3
            pygame.draw.line(surface, data.white, (x1, y1), (x2, y2), w)

            if w > 2:
                pulse_w = w - 1
                pygame.draw.line(surface, data.white, (x1, y1), (x2, y2), pulse_w)

    for obj in objects:
        obj['spawn'] = min(1.0, obj['spawn'] + 0.05)
        scale = obj['spawn']
        x, y = obj['position']
        node = obj['node']

        if obj['type'] == 'circle' and obj['unconnected_turns'] > 0:
            blink_speed = 500
            current_time = pygame.time.get_ticks()
            if (current_time // blink_speed) % 2 == 0:
                color = (255, 0, 0)
            else:
                color = data.white
        else:
            color = data.hover if selected and selected['name'] == obj['name'] else data.white

        if isinstance(node, Router) and node.recieving_now >= node.max_connected:
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
            text_surface = data.object_font.render(obj['display_text'], True, data.white)
            text_rect = text_surface.get_rect(center=(x, y))
            surface.blit(text_surface, text_rect)

            if isinstance(node, Router):
                txt = f'{node.recieving_now}/{node.max_connected}'
                txt_surface = data.small_font.render(txt, True, color)
                txt_rect = txt_surface.get_rect(center=(x, y + obj['size'] // 2 + 10))
                surface.blit(txt_surface, txt_rect)

            if isinstance(node, Client) and obj.get('required_server'):
                server_text = f"→ {obj['required_server']}"
                server_surface = data.small_font.render(server_text, True, (200, 200, 100))
                server_rect = server_surface.get_rect(center=(x, y + obj['radius'] + 15))
                surface.blit(server_surface, server_rect)

    if dragging and start_point and len(path_points) >= 1:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        points = [start_point] + path_points + [(mouse_x, mouse_y)]
        for i in range(len(points) - 1):
            pygame.draw.line(surface, data.white, points[i], points[i + 1], 3)
        if len(path_points) > 0:
            pygame.draw.circle(surface, data.white, points[-1], 6, 2)



def start_game():
    data.turn = 1
    data.client_counter = 2
    data.game_over = False
    data.game_over_timer = 0
    data.last_turn_time = time.time()

    config.reset_all()

    client1 = config.randspawn('client')
    client2 = config.randspawn('client')
    router1 = config.randspawn('router')
    router2 = config.randspawn('router')
    server1 = config.randspawn('server')
    server2 = config.randspawn('server')

    if client1 and server1:
        client1['required_server'] = server1['name']
        client1['node'].required_server = server1['node']

    if client2 and server2:
        client2['required_server'] = server2['name']
        client2['node'].required_server = server2['node']


def assign_required_server(client_obj):
    available_servers = [obj for obj in data.objects if obj['type'] == 'square']
    if available_servers:
        server = random.choice(available_servers)
        client_obj['required_server'] = server['name']
        client_obj['node'].required_server = server['node']
        return True
    return False


def next_turn():
    data.turn += 1
    data.client_counter += 1

    new_client = config.randspawn()

    if new_client is None:
        data.client_counter -= 1

    else:
        assign_required_server(new_client)
        data.client_counter = len([obj for obj in data.objects if obj['type'] == 'circle'])

    for obj in data.objects:
        if obj['type'] == 'circle' and isinstance(obj['node'], Client):
            if obj != new_client:
                if not check_client_connection(obj):
                    obj['unconnected_turns'] += 1
                    if obj['unconnected_turns'] >= 5 and not data.test:
                        data.game_over = True
                        data.game_over_timer = pygame.time.get_ticks()
                else:
                    obj['unconnected_turns'] = 0

    for obj in data.objects:
        if obj['type'] == 'circle' and isinstance(obj['node'], Client):
            assign_required_server(obj)

    if data.client_counter % 10 == 0:
        config.randspawn('router')

    data.last_turn_time = time.time()


def main():
    omega_game_btd = rendering.Button('Бесконечный режим', data.height // 2 + 260)
    new_game_btn = rendering.Button('Новая игра', data.height // 2 + 40)
    exit_btn = rendering.Button('Выход', data.height // 2 + 150)

    next_turn_btn = rendering.Button('Следующий ход', data.height // 2 + 150)

    next_turn_btn.rect.center = (data.width - 220, data.height - 80)
    back_to_menu_btn = rendering.Button('В главное меню', data.height // 2 + 100)

    selected = None
    started = False
    dragging = False
    start_point = None
    path_points = []
    tutorial = one_text.Tutorial()

    while True:
        if data.turn != 1:
            data.times = time.time()
        data.screen.fill(data.black)

        if started and not data.game_over and data.times - data.last_turn_time >= data.turn_update:
            next_turn()

        if data.win_timer >= 10:
            data.win = True

        if data.test and pygame.key.get_pressed()[pygame.K_UP]:
            data.win_timer += 1
        if data.test and pygame.key.get_pressed()[pygame.K_DOWN]:
            data.game_over_timer += 1

        if data.game_over:
            overlay = pygame.Surface((data.width, data.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            data.screen.blit(overlay, (0, 0))

            fonts = pygame.font.SysFont('arial', 72, bold=True)
            texts = fonts.render('GAME OVER', True, (255, 0, 0))
            data.screen.blit(texts, texts.get_rect(center=(data.width // 2, data.height // 2 - 100)))

            reason_font = pygame.font.SysFont('arial', 32)
            reason_text = reason_font.render('Клиент остался без подключения 3 хода', True, data.white)
            data.screen.blit(reason_text, reason_text.get_rect(center=(data.width // 2, data.height // 2)))

            back_to_menu_btn.draw(data.screen)

        if data.win:
            overlay = pygame.Surface((data.width, data.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            data.screen.blit(overlay, (0, 0))

            fonts = pygame.font.SysFont('arial', 72, bold=True)
            texts = fonts.render('YOU WINNERS', True, data.hover)
            data.screen.blit(texts, texts.get_rect(center=(data.width // 2, data.height // 2 - 100)))

            data.omega_unlock = True

            back_to_menu_btn.draw(data.screen)

        elif not started:
            draw_logo(data.screen)
            title = data.title_font.render('Synaptic Transit', True, data.white)
            title_rect = title.get_rect(center=(data.width // 2, data.height // 2 - 110))
            data.screen.blit(title, title_rect)
            new_game_btn.draw(data.screen)
            exit_btn.draw(data.screen)
            if not data.win or data.test:
                omega_game_btd.draw(data.screen)

        else:
            draw_objects(data.screen, data.objects, selected, dragging, start_point, path_points)
            next_turn_btn.draw(data.screen)

            data.screen.blit(data.small_font.render(f'Ход: {data.turn}', True, data.white), (20, 20))

            if data.turn != 1:
                data.screen.blit(data.small_font.render(f'Следующий ход через: {max(0, min(data.turn_update, data.turn_update - (data.times - data.last_turn_time))):.1f}с', True, data.white), (20, 50))

            if not data.omega:
                if data.win_timer != 0 or data.test:
                    data.screen.blit(data.small_font.render(f'Победа через: {max(0, 10 - data.win_timer):.1f} ходов', True, data.white), (data.width // 2 - 100, 20))


            warning_y = 80
            for obj in data.objects:
                if obj['type'] == 'circle' and obj['unconnected_turns'] > 0:
                    warning_text = f"Клиент {obj['display_text']}: {obj['unconnected_turns']}/3 → {obj.get('required_server', '?')}"
                    warning_surface = data.small_font.render(warning_text, True, (255, 0, 0))
                    data.screen.blit(warning_surface, (20, warning_y))
                    warning_y += 25

        if data.tutorial_active and started and not data.game_over:
            tutorial.draw(data.screen, data.tutorial_step)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if data.game_over or data.win:
                if back_to_menu_btn.clicked(event):
                    data.game_over = False
                    started = False
                    data.tutorial_active = False
                    data.tutorial_step = 0
                    data.win = False
                    data.win_timer = 0
                    data.omega = False
                continue

            if data.tutorial_active and started:
                if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                    if data.tutorial_step < 3:
                        data.tutorial_step += 1
                    else:
                        data.tutorial_active = False
                        data.tutorial_step = 0
                continue

            if not started:
                if omega_game_btd.clicked(event):
                    start_game()
                    started = True
                    data.omega = True
                if new_game_btn.clicked(event):
                    start_game()
                    started = True
                    data.tutorial_active = True
                    data.tutorial_step = 0
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
                                    target = next((o for o in data.objects if o['name'] == conn['to']), None)
                                    if target:
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