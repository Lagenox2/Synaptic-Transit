'''
Кружок A по центру сверху, соединен с треугольником B. Кружок C справа сверху, соединен с треугольником B.
Кружок D слева сверху, соединен с треугольником E (левый нижний угол). Кружок F слева сверху,
соединен с треугольником G (правый нижний угол). Треугольник G соединен с треуг. E.
Все треугольники соединены с квадратом, расположенным по центру.

Кружок - клиент
Треугольник - роутер
Все треугольники подключены к центру (сервер)
'''




class Network:
    def __init__(self):
        self.clients = []
        self.routers = []
        self.servers = []

    def add_client(self, client):
        self.clients.append(client)

    def add_router(self, router):
        self.routers.append(router)

    def add_server(self, server):
        self.servers.append(server)

    def find_node(self, name):
        for group in (self.clients, self.routers, self.servers):
            for node in group:
                if node.name == name:
                    return node
        return None
