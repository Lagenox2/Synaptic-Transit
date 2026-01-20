import pygame
import random
import math
import time

# константы экрана (из main.py)
screen_width = 1920
screen_height = 1080
safe_zone = 75

# размеры объектов
client_radius = 50
router_size = 100
server_size = 100

# цвета волн (кратно 10)
wave_colors = [
    (200, 200, 200),
    (190, 190, 190),
    (180, 180, 180)
]
hover_color = (190, 20, 250)

# глобальные переменные
all_objects = []
client_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
client_counter = 0
server_counter = 0


def spawn_client(generate_waves=True):
    global client_counter

    # ищем свободную позицию
    x, y = 0, 0
    found = False

    for _ in range(100):
        x = random.randint(safe_zone, screen_width - safe_zone)
        y = random.randint(safe_zone, screen_height - safe_zone)

        # проверка пересечений
        valid = True
        for obj in all_objects:
            ox, oy = obj["position"]
            dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if dist < 150:  # 75 + 75
                valid = False
                break

        if valid:
            found = True
            break

    if not found:
        return None

    # буква для отображения
    if client_counter < len(client_letters):
        display_text = client_letters[client_counter]
    else:
        idx = client_counter % len(client_letters)
        num = client_counter // len(client_letters)
        display_text = f"{client_letters[idx]}{num}"

    client_counter += 1

    # создаем волны если нужно
    waves = []
    if generate_waves:
        current_time = time.time()
        for i in range(3):
            wave = {
                "radius": client_radius + (i + 1) * 20,
                "color": list(wave_colors[i]),
                "opacity": 1.0,
                "speed": 0.5,
                "start_time": current_time + i * 0.2,
                "active": True
            }
            waves.append(wave)

    # объект клиента
    client_obj = {
        "type": "circle",
        "name": f"C{client_counter}",
        "display_text": display_text,
        "position": [x, y],
        "radius": client_radius,
        "waves": waves,
        "hover": False
    }

    all_objects.append(client_obj)
    return client_obj


def spawn_router():
    # ищем свободную позицию
    x, y = 0, 0
    found = False

    for _ in range(100):
        x = random.randint(safe_zone, screen_width - safe_zone)
        y = random.randint(safe_zone, screen_height - safe_zone)

        # проверка пересечений
        valid = True
        for obj in all_objects:
            ox, oy = obj["position"]
            dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if dist < 150:
                valid = False
                break

        if valid:
            found = True
            break

    if not found:
        return None

    # количество соединений
    connections = random.randint(3, 10)

    # объект роутера
    router_obj = {
        "type": "triangle",
        "name": f"R{len([o for o in all_objects if o['type'] == 'triangle'])}",
        "display_text": str(connections),
        "position": [x, y],
        "size": router_size,
        "max_connections": connections,
        "hover": False
    }

    all_objects.append(router_obj)
    return router_obj


def spawn_server():
    global server_counter

    # центральная область
    center_x = screen_width // 2
    center_y = screen_height // 2
    center_area = 400

    # ищем позицию в центре
    x, y = 0, 0
    found = False

    for _ in range(100):
        x = random.randint(center_x - center_area // 2, center_x + center_area // 2)
        y = random.randint(center_y - center_area // 2, center_y + center_area // 2)

        # проверка пересечений
        valid = True
        for obj in all_objects:
            ox, oy = obj["position"]
            dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if dist < 150:
                valid = False
                break

        if valid:
            found = True
            break

    if not found:
        # ищем везде
        for _ in range(100):
            x = random.randint(safe_zone, screen_width - safe_zone)
            y = random.randint(safe_zone, screen_height - safe_zone)

            valid = True
            for obj in all_objects:
                ox, oy = obj["position"]
                dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
                if dist < 150:
                    valid = False
                    break

            if valid:
                found = True
                break

    if not found:
        return None

    # объект сервера
    server_obj = {
        "type": "square",
        "name": f"S{server_counter}",
        "display_text": str(server_counter),
        "position": [x, y],
        "size": server_size,
        "hover": False
    }

    server_counter += 1
    all_objects.append(server_obj)
    return server_obj


def update_waves():
    current_time = time.time()

    for obj in all_objects:
        if obj["type"] == "circle" and "waves" in obj:
            for wave in obj["waves"]:
                if wave["active"]:
                    # обновляем радиус
                    wave["radius"] += wave["speed"]

                    # обновляем непрозрачность
                    wave_age = current_time - wave["start_time"]
                    wave["opacity"] = max(0, 1.0 - wave_age * 0.5)

                    # обновляем цвет
                    base_idx = obj["waves"].index(wave) % 3
                    base_color = wave_colors[base_idx]
                    wave["color"] = [
                        int(base_color[0] * wave["opacity"]),
                        int(base_color[1] * wave["opacity"]),
                        int(base_color[2] * wave["opacity"])
                    ]

                    # если волна исчезла
                    if wave["opacity"] <= 0:
                        wave["active"] = False


def check_hover(mouse_pos, obj):
    x, y = obj["position"]

    if obj["type"] == "circle":
        dist = math.sqrt((mouse_pos[0] - x) ** 2 + (mouse_pos[1] - y) ** 2)
        obj["hover"] = dist <= obj["radius"]

    elif obj["type"] == "square":
        half = obj["size"] // 2
        obj["hover"] = (x - half <= mouse_pos[0] <= x + half and
                        y - half <= mouse_pos[1] <= y + half)

    elif obj["type"] == "triangle":
        size = obj["size"]
        half = size // 2

        # точки треугольника
        points = [
            (x, y - half),
            (x - half, y + half),
            (x + half, y + half)
        ]

        # упрощенная проверка (ограничивающий прямоугольник)
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        obj["hover"] = (min_x <= mouse_pos[0] <= max_x and
                        min_y <= mouse_pos[1] <= max_y)

    return obj["hover"]


def get_hover_color(obj):
    return hover_color if obj.get("hover", False) else (255, 255, 255)


def randspawn(chance, spawn_type=0, waves=True):
    if random.random() > chance:
        return None

    if spawn_type == 0:  # случайный
        r = random.random()
        if r < 0.79:
            return spawn_client(waves)
        elif r < 0.99:
            return spawn_router()
        else:
            return spawn_server()

    elif spawn_type == 1:  # клиент
        return spawn_client(waves)

    elif spawn_type == 2:  # роутер
        return spawn_router()

    elif spawn_type == 3:  # сервер
        return spawn_server()

    return None


def reset_all():
    global all_objects, client_counter, server_counter
    all_objects = []
    client_counter = 0
    server_counter = 0


def get_all_objects():
    return all_objects