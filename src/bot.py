
from dotenv import load_dotenv
import yaml
import os
import swibots


env_file = os.path.join(os.path.dirname(__file__), "..",  ".env")  # noqa : E402
load_dotenv(env_file, override=True)
swibots.reload_config()


import logging.config  # noqa : E402
import logging  # noqa : E402
from swibots import BotApp, RegisterCommand  # noqa : E402
from handlers import init  # noqa : E402
import config  # noqa : E402

WS_URL = os.getenv("CHAT_SERVICE_WS_URL")
CONFIG_WS_URL = swibots.get_config()["CHAT_SERVICE"]["WS_URL"]

# # Get logging configurations
# logging.basicConfig(level=logging.DEBUG)
configfile = os.path.join(os.path.dirname(__file__), 'logging.yaml')
with open(configfile, 'r') as stream:
    log_config = yaml.load(stream, Loader=yaml.FullLoader)

logging.config.dictConfig(log_config)


log = logging.getLogger(__name__)


app = BotApp(
    config.BOT_TOKEN,
    "A cool bot with annotations and everything you could possibly want :)"
).register_command(
    [
        RegisterCommand("json", "Prints the message json", True),
        RegisterCommand("echo", "Echoes the message", True),
        RegisterCommand("buttons", "Shows buttons", True),
        RegisterCommand(["movie", "movies", "film", "films", "imdb"],
                        "Show info about movies", True),
        RegisterCommand(["movie", "movies", "film", "films", "imdb"],
                        "Show info about movies", True),
        RegisterCommand("index", "Index channel", True),
    ]
)


async def on_startup(app: BotApp):
    log.info("Bot started")

init(app)

app.run()
