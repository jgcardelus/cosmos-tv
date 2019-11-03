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
def start_app(id_):
    if id_ == "netflix":
        netflix = Netflix()
        opened_apps.append(netflix)

        netflix.start()

def start_app_search(id_, search_url):
    print(id_, search_url)
