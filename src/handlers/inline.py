import logging
from swibots import InlineKeyboardButton, InlineMarkup, InlineQueryResultDocument, InlineQuery, BotApp, BotContext, InlineQueryEvent, InlineQueryAnswer
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp
from config import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME


def inline(app: BotApp):
    async def inline_users(query: InlineQuery):
        return True
        if AUTH_USERS:
            if query.user and query.user.id in AUTH_USERS:
                return True
            else:
                return False
        if query.user and query.user.id not in temp.BANNED_USERS:
            return True
        return False

    @app.on_inline_query()
    async def answer(ctx: BotContext[InlineQueryEvent]):
        """Show search results for given inline query"""
        query: InlineQuery = ctx.event.query
        if not await inline_users(query):
            await query.answer(InlineQueryAnswer(
                results=[],
                cache_time=0,
                pm_text='okDa',
                pm_parameter="hehe"
            ))
            return

        # if AUTH_CHANNEL and not await is_subscribed(bot, query):
        #     await query.answer(results=[],
        #                     cache_time=0,
        #                     pm_text='You have to subscribe my channel to use the bot',
        #                     pm_parameter="subscribe")
        #     return

        results = []
        if '|' in query.query:
            string, file_type = query.query.split('|', maxsplit=1)
            string = string.strip()
            file_type = file_type.strip().lower()
        else:
            string = query.query.strip()
            file_type = None

        offset = int(query.offset or 0)
        reply_markup = get_reply_markup(query=string)
        files, next_offset, total = await get_search_results(string,
                                                             file_type=file_type,
                                                             max_results=10,
                                                             offset=offset)

        for file in files:
            title = file.file_name
            size = get_size(file.file_size)
            f_caption = file.caption
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
            if f_caption is None:
                f_caption = f"{file.file_name}"
            results.append(
                InlineQueryResultDocument(
                    id=file.file_id,
                    title=f_caption,
                    document_url=file.file_url,
                    mime_type=file.mime_type,
                    description=f'Size: {get_size(file.file_size)}\nType: {file.file_type}',
                    reply_markup=reply_markup))

        if results:
            pm_text = f"📁 Results - {total}"
            if string:
                pm_text += f" for {string}"
            try:
                await query.answer(InlineQueryAnswer(
                    results=results,
                    is_personal=True,
                    cache_time=cache_time,
                    pm_text=pm_text,
                    pm_parameter="start",
                    next_offset=str(next_offset)
                ))
            except Exception as e:
                logging.exception(str(e))
        else:
            pm_text = f'❌ No results'
            if string:
                pm_text += f' for "{string}"'

            await query.answer(InlineQueryAnswer(
                title=pm_text,
                results=[],
                is_personal=True,
                cache_time=cache_time,
                pm_text=pm_text,
                pm_parameter="okay"
            ))

    def get_reply_markup(query):
        buttons = [
            [
                InlineKeyboardButton(
                    app, 'Search again')
            ]
        ]
        return InlineMarkup(app, buttons)
