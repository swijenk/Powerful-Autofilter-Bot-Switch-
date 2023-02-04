import asyncio
from swibots import BotApp, BotContext, CommandEvent


def movies(app: BotApp):
    @app.on_command(["movie", "movies", "film", "films", "search"])
    async def show_movie_info(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        params = ctx.event.params
        if params is None or len(params) == 0:
            await message.reply_text(f"Please enter a movie name!\nType /{ctx.event.command} <movie name>")
            return
        mymessage = await message.reply_text(f"Searching for {params}...")
        await asyncio.sleep(2)
        await mymessage.edit_text(f"I couldn't found any result for {params}!")

    @app.on_command(["index"])
    async def index_channel(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        mymessage = await message.reply_text("Indexing channel...")
        total = 0
        await asyncio.sleep(2)
        await mymessage.edit_text(f"Done! I found {total} movies!")
