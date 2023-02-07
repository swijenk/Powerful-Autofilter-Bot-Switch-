import asyncio
import re
from swibots import BotApp, BotContext, CommandEvent, CallbackQueryEvent, InlineKeyboardButton, InlineMarkup, filters, Message
from utils import get_poster
from config import IMDB_TEMPLATE


def imdb(app: BotApp):
    async def show_results(search: str, message: Message):
        movies = await get_poster(search, bulk=True)
        if not movies:
            await message.edit_text(f"I couldn't found any result for {search}!")
            return

        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} - {movie.get('year')}",
                    callback_data=f"imdb#{movie.movieID}#{search}",
                )
            ]
            for movie in movies
        ]
        await message.edit_text(f"Here is what i found on IMDb", inline_markup=InlineMarkup(app, btn))

    @app.on_command(["imdb", "search"])
    async def imdb_search(ctx: BotContext[CommandEvent]):
        message = ctx.event.message
        params = ctx.event.params
        if params is None or len(params) == 0:
            await message.reply_text(f"Please enter a movie name!\nType /{ctx.event.command} <movie name>")
            return

        mymessage = await message.reply_text(f"Searching for {params}...")
        await show_results(params, mymessage)

    @app.on_callback_query(filters.regexp('^search'))
    async def imdb_search_callback(ctx: BotContext[CallbackQueryEvent]):
        _, search_params = ctx.event.callback_data.split('#')
        # delete the message
        mymessage = await ctx.event.message.edit_text(f"Searching for {search_params}...")
        await show_results(search_params, mymessage)

    @app.on_callback_query(filters.regexp('^imdb'))
    async def imdb_callback(ctx: BotContext[CallbackQueryEvent]):
        i, movie, search_params = ctx.event.callback_data.split('#')
        imdb = await get_poster(query=movie, id=True)
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{imdb.get('title')} - {imdb.get('year')}",
                    url=imdb['url'],
                )

            ],
            [
                InlineKeyboardButton(
                    text=f"Back to Search",
                    callback_data=f"search#{search_params}",
                )
            ]
        ]
        message: Message = ctx.event.message

        caption = IMDB_TEMPLATE.format(
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )

        if imdb.get('poster'):
            m = Message(app)
            m.media_link = imdb['poster']
            m.status = 1  # 1 image, 2 video, 3 audio
            m.message = caption
            m.inline_markup = InlineMarkup(app, btn)
            m.replied_to_id = message.replied_to_id  # reply to the original message
            # send the new message
            await m.send()
            # delete the old message
            await message.delete()

        else:
            await message.edit_text(caption, inline_markup=InlineMarkup(app, btn))
