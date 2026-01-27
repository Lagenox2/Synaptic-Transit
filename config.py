import random, math, time, json
import data



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
                    base_color = data.wave_colors[base_idx]
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
    return data.hover if obj.get("hover", False) else (255, 255, 255)

def spawn(x, y, obj_type, generate_waves=True):
    global client_counter, server_counter

    # Проверка на валидность координат
    if not (data.safe_zone <= x <= data.width - data.safe_zone and
            data.safe_zone <= y <= data.height - data.safe_zone):
        return None

    # Проверка коллизий
    for obj in all_objects:
        ox, oy = obj["position"]
        dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
        if dist < 150:  # минимальное расстояние
            return None

    if obj_type == 1:  # Клиент
        # буква для отображения
        if client_counter < len(data.client_letters):
            display_text = data.client_letters[client_counter]
        else:
            idx = client_counter % len(data.client_letters)
            num = client_counter // len(data.client_letters)
            display_text = f"{data.client_letters[idx]}{num}"

        client_counter += 1

        # создаем волны если нужно
        waves = []
        if generate_waves:
            current_time = time.time()
            for i in range(3):
                wave = {
                    "radius": data.client_radius + (i + 1) * 20,
                    "color": list(data.wave_colors[i]),
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
            "radius": data.client_radius,
            "waves": waves,
            "hover": False
        }

        all_objects.append(client_obj)
        return client_obj

    elif obj_type == 2:  # Роутер
        # количество соединений
        connections = random.randint(3, 10)

        # объект роутера
        router_obj = {
            "type": "triangle",
            "name": f"R{len([o for o in all_objects if o['type'] == 'triangle']) + 1}",
            "display_text": str(connections),
            "position": [x, y],
            "size": data.router_size,
            "max_connections": connections,
            "hover": False
        }

        all_objects.append(router_obj)
        return router_obj

    elif obj_type == 3:  # Сервер
        # объект сервера
        server_obj = {
            "type": "square",
            "name": f"S{server_counter}",
            "display_text": str(server_counter),
            "position": [x, y],
            "size": data.server_size,
            "hover": False
        }

        server_counter += 1
        all_objects.append(server_obj)
        return server_obj

    return None

def randspawn(chance, spawn_type=0, waves=True):
    x, y = 0, 0
    for _ in range(1000):
        x = random.randint(data.safe_zone, data.width - data.safe_zone)
        y = random.randint(data.safe_zone, data.height - data.safe_zone)

        valid = True
        for obj in all_objects:
            ox, oy = obj["position"]
            dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if dist < 150:
                valid = False
                break

        if valid:
            break
        else:
            return None

    spawn(x, y, spawn_type, )


def import_level(filename, generate_waves=False):
    global all_objects, client_counter, server_counter

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        reset_all()

        for shape in data.get("shapes", []):
            shape_type = shape.get("type", "").lower()
            position = shape.get("position", [0, 0])
            name = shape.get("name", "")

            x, y = position

            obj_type = 0
            if shape_type == "circle":
                obj_type = 1
            elif shape_type == "triangle":
                obj_type = 2
            elif shape_type == "square":
                obj_type = 3

            # Создаем объект (игнорируем connections)
            if obj_type == 1:  # Клиент
                obj = spawn(x, y, 1, generate_waves, name)
            elif obj_type == 2:  # Роутер
                obj = spawn(x, y, 2, False, name)
            elif obj_type == 3:  # Сервер
                obj = spawn(x, y, 3, False, name)
        return True

    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден")
        return False
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка при загрузке уровня: {e}")
        return False

def reset_all():
    global all_objects, client_counter, server_counter
    all_objects = []
    client_counter = 0
    server_counter = 0

def get_all_objects():
    return all_objects