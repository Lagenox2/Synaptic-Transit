class Client:
    def __init__(self, name):
        self.name = name
        self.connected_routers = []
        self.required_server = None  # Сервер, к которому нужен путь

    def connect(self, router):
        if router not in self.connected_routers:
            self.connected_routers.append(router)
            router.add_client(self)

    def disconnect(self, router):
        if router in self.connected_routers:
            self.connected_routers.remove(router)
            router.remove_client(self)

    def has_path_to(self, server):
        """Проверяет, есть ли путь от клиента к указанному серверу"""
        if not self.connected_routers:
            return False

        # Используем поиск в ширину для нахождения пути
        visited = set()
        queue = []

        # Начинаем с всех подключенных роутеров
        for router in self.connected_routers:
            queue.append(router)
            visited.add(router)

        while queue:
            current = queue.pop(0)

            # Если текущий узел - сервер и это нужный сервер
            if hasattr(current, 'connected_servers'):
                for s in current.connected_servers:
                    if s == server:
                        return True
                    if s not in visited:
                        visited.add(s)
                        # Серверы могут быть подключены к роутерам
                        if hasattr(s, 'connected_routers'):
                            for r in s.connected_routers:
                                if r not in visited:
                                    queue.append(r)

            # Добавляем связанные роутеры
            if hasattr(current, 'connected_routers'):
                for r in current.connected_routers:
                    if r not in visited:
                        visited.add(r)
                        queue.append(r)

            # Добавляем связанные серверы
            if hasattr(current, 'connected_servers'):
                for s in current.connected_servers:
                    if s not in visited:
                        visited.add(s)
                        # Проверяем, это ли нужный сервер
                        if s == server:
                            return True
                        # Серверы могут вести к другим роутерам
                        if hasattr(s, 'connected_routers'):
                            for r in s.connected_routers:
                                if r not in visited:
                                    queue.append(r)

        return False