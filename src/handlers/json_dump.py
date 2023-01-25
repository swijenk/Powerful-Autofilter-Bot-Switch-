from swibots import BotApp, BotContext, CommandEvent
import json


def json_dump(app: BotApp):
    @app.on_command("json")
    async def json_dump(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        await message.reply_text(json.dumps(message.to_json(), indent=2))
