import random

import config
import server
import actuators

from services.netflix import Netflix

# MEDIA VARS
opened_apps = []
active_app = None
volume = 0
is_mute = False

# START SEQUENCE
def start():
    server.start()

def frontend_start_seq():
    load_apps()

def load_apps():
    apps_file = open('services/services.json', 'r')
    apps = apps_file.read()
    server.emit('apps', apps)
    
def start_offline():
    server.start_offline()

# APPS INIT SEQUENCE
def generate_id_identifier(prefix):
    global opened_apps

    identifier = random.randint(0, 1000000)
    id_ = prefix + '-' + str(identifier)

    exists = False
    for app in opened_apps:
        if app.id_ == id_:
            exists = True
            break

    if exists:
        id_ = generate_id_identifier(prefix)
    
    return id_

def start_app(id_):
    global opened_apps

    print("Called")

    if id_ == "netflix":
        netflix = Netflix()
        netflix.id_ = generate_id_identifier(netflix.id_)
        opened_apps.append(netflix)

        netflix.start()

def start_app_search(id_, search_url):
    print(id_, search_url)

def test():
    start_app("netflix")

    netflix = opened_apps[0]
    netflix.start_show("Rick and Morty", "some-url")