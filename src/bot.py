import sys
import os

import swibots
from swibots import BotApp, RegisterCommand
import logging
import logging.config
import os


import yaml
from dotenv import load_dotenv
from handlers import init

env_file = os.path.join(os.path.dirname(__file__), "..",  ".env")
load_dotenv(env_file, override=True)
swibots.reload_config()

WS_URL = os.getenv("CHAT_SERVICE_WS_URL")
CONFIG_WS_URL = swibots.get_config()["CHAT_SERVICE"]["WS_URL"]

# # Get logging configurations
# logging.basicConfig(level=logging.DEBUG)
configfile = os.path.join(os.path.dirname(__file__), 'logging.yaml')
with open(configfile, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(config)


log = logging.getLogger(__name__)


token = os.getenv("TOKEN")
username = os.getenv("USERNAME") or "test"
password = os.getenv("PASSWORD") or "test"

app = BotApp(
    username,
    password,
    token,
    "A cool bot with annotations and everything you could possibly want :)"
).register_command(
    [
        RegisterCommand("json", "Prints the message json", True),
        RegisterCommand("echo", "Echoes the message", True),
        RegisterCommand("buttons", "Shows buttons", True),
        RegisterCommand(["movie", "movies", "film", "films", "search"],
                        "Show info about movies", True),
    ]
)
init(app)
app.run()
