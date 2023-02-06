import asyncio
import re
from swibots import BotApp, BotContext, CommandEvent, CallbackQueryEvent, InlineKeyboardButton, InlineMarkup, filters
from utils import get_poster


def imdb(app: BotApp):
    @app.on_command(["imdb", "search"])
    async def imdb_search(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        params = ctx.event.params
        if params is None or len(params) == 0:
            await message.reply_text(f"Please enter a movie name!\nType /{ctx.event.command} <movie name>")
            return
        mymessage = await message.reply_text(f"Searching for {params}...")
        movies = await get_poster(params, bulk=True)
        if not movies:
            await mymessage.edit_text(f"I couldn't found any result for {params}!")
            return

        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} - {movie.get('year')}",
                    callback_data=f"imdb#{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await mymessage.edit_text(f"Here is what i found on IMDb", inline_markup=InlineMarkup(app, btn))

    @app.on_callback_query(filters.regex('^imdb'))
    async def imdb_callback(ctx: BotContext[CallbackQueryEvent]):
        i, movie = ctx.event.data.split('#')
        imdb = await get_poster(query=movie, id=True)
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{imdb.get('title')} - {imdb.get('year')}",
                    url=imdb['url'],
                )
            ]
        ]
        # if imdb.get('poster'):
        #     await query.message.reply_photo(photo=imdb['poster'], caption=f"IMDb Data:\n\n🏷 Title:<a href={imdb['url']}>{imdb.get('title')}</a>\n🎭 Genres: {imdb.get('genres')}\n📆 Year:<a href={imdb['url']}/releaseinfo>{imdb.get('year')}</a>\n🌟 Rating: <a href={imdb['url']}/ratings>{imdb.get('rating')}</a> / 10\n🖋 StoryLine: <code>{imdb.get('plot')} </code>", reply_markup=InlineKeyboardMarkup(btn))
        #     await query.message.delete()
        # else:
        #     await query.message.edit(f"IMDb Data:\n\n🏷 Title:<a href={imdb['url']}>{imdb.get('title')}</a>\n🎭 Genres: {imdb.get('genres')}\n📆 Year:<a href={imdb['url']}/releaseinfo>{imdb.get('year')}</a>\n🌟 Rating: <a href={imdb['url']}/ratings>{imdb.get('rating')}</a> / 10\n🖋 StoryLine: <code>{imdb.get('plot')} </code>", reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=True)
        # await query.answer()


