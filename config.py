import random, math, time, json
import data

# Глобальные счетчики
client_counter = 0
server_counter = 0
all_objects = []  # Для совместимости


def update_waves():
    current_time = time.time()

    for obj in all_objects:
        if obj["type"] == "circle" and "waves" in obj:
            for wave in obj["waves"]:
                if wave["active"]:
                    wave["radius"] += wave["speed"]

                    wave_age = current_time - wave["start_time"]
                    wave["opacity"] = max(0, 1.0 - wave_age * 0.5)

                    base_idx = obj["waves"].index(wave) % 3
                    base_color = data.wave_colors[base_idx]
                    wave["color"] = [
                        int(base_color[0] * wave["opacity"]),
                        int(base_color[1] * wave["opacity"]),
                        int(base_color[2] * wave["opacity"])
                    ]

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

        points = [
            (x, y - half),
            (x - half, y + half),
            (x + half, y + half)
        ]

        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)

        obj["hover"] = (min_x <= mouse_pos[0] <= max_x and
                        min_y <= mouse_pos[1] <= max_y)

    return obj["hover"]


def get_hover_color(obj):
    return data.hover if obj.get("hover", False) else (255, 255, 255)


def spawn_node(x, y, obj_type, name=None):
    """Создает узел сети и соответствующий визуальный объект"""
    from client import Client
    from router import Router
    from server import Server

    global client_counter, server_counter

    if not (data.safe_zone <= x <= data.width - data.safe_zone and
            data.safe_zone <= y <= data.height - data.safe_zone):
        return None

    # Проверяем расстояние до других объектов
    for obj in data.objects:
        ox, oy = obj['position']
        dist = math.hypot(x - ox, y - oy)
        if dist < 150:  # Минимальное расстояние между объектами
            return None

    # Создаем соответствующий узел сети
    node = None
    display_name = ""

    if obj_type == 'client':
        if name is None:
            name = f'C{len(data.network.clients) + 1}'
        node = Client(name)
        data.network.add_client(node)
        display_name = name

    elif obj_type == 'router':
        if name is None:
            name = f'R{len(data.network.routers) + 1}'
        node = Router(name)
        data.network.add_router(node)
        display_name = name

    elif obj_type == 'server':
        if name is None:
            name = f'S{len(data.network.servers) + 1}'
        node = Server(name)
        data.network.add_server(node)
        display_name = name
    else:
        return None

    # Создаем визуальный объект
    visual_obj = {
        'name': name,
        'node': node,
        'type': 'circle' if obj_type == 'client' else 'triangle' if obj_type == 'router' else 'square',
        'position': (x, y),
        'connections': [],
        'radius': 32 if obj_type == 'client' else 0,
        'size': 70,
        'display_text': display_name,
        'spawn': 0.0,
        'unconnected_turns': 0,
        'required_server': None if obj_type != 'client' else None
    }

    # Для роутеров показываем количество подключений
    if obj_type == 'router':
        visual_obj['display_text'] = f"{node.recieving_now}/{node.maximum_recieving}"

    data.objects.append(visual_obj)
    return visual_obj


def spawn(x, y, obj_type, generate_waves=True, name=None):
    """Создает только визуальный объект (для обратной совместимости)"""
    if obj_type == 1:  # Клиент
        return spawn_node(x, y, 'client', name)
    elif obj_type == 2:  # Роутер
        return spawn_node(x, y, 'router', name)
    elif obj_type == 3:  # Сервер
        return spawn_node(x, y, 'server', name)
    return None


def randspawn(obj_type=None):
    for _ in range(1000):
        x = random.randint(data.safe_zone, data.width - data.safe_zone)
        y = random.randint(data.safe_zone, data.height - data.safe_zone)

        safe = True
        for obj in data.objects:
            ox, oy = obj['position']
            dist = math.hypot(x - ox, y - oy)
            if dist < 150:
                safe = False
                break

        if safe:
            if obj_type == 'client':
                return spawn_node(x, y, 'client')
            elif obj_type == 'router':
                return spawn_node(x, y, 'router')
            elif obj_type == 'server':
                return spawn_node(x, y, 'server')
            else:
                nova = random.random()
                if nova <= 0.8:
                    return spawn_node(x, y, 'client')
                elif 0.8 > nova <= 0.95:
                    return spawn_node(x, y, 'router')
                else:
                    return spawn_node(x, y, 'server')

    return None


def find_safe_position(min_distance=150, attempts=500):
    for _ in range(attempts):
        x = random.randint(data.safe_zone, data.width - data.safe_zone)
        y = random.randint(data.safe_zone, data.height - data.safe_zone)
        safe = True

        for obj in data.objects:
            ox, oy = obj['position']
            distance = math.hypot(x - ox, y - oy)
            if distance < min_distance:
                safe = False
                break

        if safe:
            return (x, y)

    return None


def import_level(filename, generate_waves=False):
    global all_objects, client_counter, server_counter

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            level_data = json.load(f)

        reset_all()

        for shape in level_data.get("shapes", []):
            shape_type = shape.get("type", "").lower()
            position = shape.get("position", [0, 0])
            name = shape.get("name", "")

            x, y = position

            if shape_type == "circle":
                spawn_node(x, y, 'client', name)
            elif shape_type == "triangle":
                spawn_node(x, y, 'router', name)
            elif shape_type == "square":
                spawn_node(x, y, 'server', name)
        return True

    except FileNotFoundError:
        return False
    except json.JSONDecodeError as e:
        return False
    except Exception as e:
        return False


def reset_all():
    global all_objects, client_counter, server_counter
    all_objects = []
    client_counter = 0
    server_counter = 0

    # Также сбрасываем данные игры
    data.objects.clear()
    if data.network:
        data.network.clients.clear()
        data.network.routers.clear()
        data.network.servers.clear()


def get_all_objects():
    return data.objects