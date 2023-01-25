import logging
from swibots import BotApp
from .echo import echo
from .json_dump import json_dump
from .movies import movies

log = logging.getLogger(__name__)


def init(app: BotApp):
    echo(app)
    json_dump(app)
    movies(app)
