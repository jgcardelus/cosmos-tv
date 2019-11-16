class Show:
    def __init__(self, name, url, container):
        self.name = name
        self.url = url
        self.container = container

        self.seasons = []

class Season:
    def __init__(self, number):
        self.number = number
        self.episodes = []

class Episode:
    def __init__(self, name, url, number):
        self.name = name
        self.url = url
        self.number = number