class Server:
    def __init__(self, name):
        self.name = name
        self.connected_routers = []

    def connect(self, router):
        if router not in self.connected_routers:
            self.connected_routers.append(router)
            router.connect_server(self)

    def disconnect(self, router):
        if router in self.connected_routers:
            self.connected_routers.remove(router)
            router.disconnect_server(self)