import json
import logging
from typing import Tuple
from swibots import BotApp, BotContext, MessageEvent, Message, filters, RestClient, RestResponse, JSONDict, NetworkError, filters, CallbackQueryEvent, CommandEvent
from .echo import echo
from .json_dump import json_dump
from .media import media
from .imdb import imdb
from .inline import inline
from .autofilter import autofilter
from config import ADMINS

log = logging.getLogger(__name__)

restclient = RestClient()


def parse_response(response: Tuple[int, bytes]) -> RestResponse[JSONDict]:
    decoded_s = response[1].decode("utf-8", "replace")
    try:
        jsonObject = json.loads(decoded_s)
    except ValueError as exc:
        jsonObject = decoded_s

    response = RestResponse(jsonObject, response[0], {})
    if response.is_error:
        raise NetworkError(response.error_message)
    return response


def init(app: BotApp):
    echo(app)
    json_dump(app)
    media(app)
    imdb(app)
    inline(app)
    autofilter(app)

    @app.on_callback_query(filters.text("close_data"))
    async def on_callback_query(ctx: BotContext[CallbackQueryEvent]):
        message: Message = ctx.event.message
        await message.delete()

    @app.on_command(["help", "start"])
    async def start(ctx: BotContext[CommandEvent]):
        message: Message = ctx.event.message
        text = ("Hello! here is a list of commands you can use:\n" +
                "/help - Show this message\n" +
                "/json - Dump the message as json\n" +
                "/imdb <movie name> - Search for a movie on IMDb\n" +
                "/search Search for a file on my database\n")

        if message.user_id in ADMINS:
            text += (
                "\nAdmin commands:\n" +
                "/index <group or channel> - Save media files from the channel or group\n" +
                "/addfilter <filter> - Add a filter\n" +
                "/delfilter <filter> - Delete a filter\n" +
                "/listfilters - List all filters\n" +
                "/delallfilters - Delete all filters\n"
            )

        await message.reply_text(text)
