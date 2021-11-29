# This file is a part of TG-FileStreamBot
# Coding : Jyothis Jayanth [@EverythingSuckz]

from os import getenv, environ
from dotenv import load_dotenv

load_dotenv()

class Var(object):
    API_ID = int(getenv('API_ID'))
    API_HASH = str(getenv('API_HASH'))
    BOT_TOKEN = str(getenv('BOT_TOKEN'))
    SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))
    WORKERS = int(getenv('WORKERS', '3'))
    BIN_CHANNEL = int(getenv('BIN_CHANNEL', None))     
    PORT = int(getenv('PORT', 8080))
    BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
    HAS_SSL = getenv('HAS_SSL', False)
    HAS_SSL = True if str(HAS_SSL).lower() == 'true' else False
    # OWNER_ID = int(getenv('OWNER_ID')) #TODO
    NO_PORT = getenv('NO_PORT', False)
    NO_PORT = True if str(NO_PORT).lower() == 'true' else False
    CLIENT_URL= getenv('CLIENT_URL')
    HOST_URL= getenv('HOST_URL')
    if 'DYNO' in environ:
        ON_HEROKU = True
        APP_NAME = str(getenv('APP_NAME'))
    else:
        ON_HEROKU = False
    FQDN = str(getenv('FQDN', BIND_ADRESS)) if not ON_HEROKU or getenv('FQDN') else APP_NAME+'.herokuapp.com'
    if ON_HEROKU:
        URL = f"https://{FQDN}/"     
    else:
        URL = "http{}://{}{}/".format('s' if HAS_SSL else '', FQDN, '' if NO_PORT else ':'+ str(PORT))
