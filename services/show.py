class Show:
    def __init__(self, name, url, container):
        self.name = name
        self.url = url
        self.container = container

        self.episodes = []


class Episode:
    def __init__(self, name, url, container):
        self.name = name
        self.url = url
        self.container = container