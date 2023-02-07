import asyncio
import re
from typing import List
from swibots import BotApp, BotContext, CommandEvent, InlineMarkup, InlineKeyboardButton, filters, Message, Group, Channel
from database.ia_filterdb import save_file
from utils import temp
import logging


lock = asyncio.Lock()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def media(app: BotApp):
    @app.on_command(["movie", "movies", "film", "films"])
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
        args = ctx.event.params

        params_regex = re.compile(r"^([a-zA-Z0-9\-]+) ?([0-9]+)? ?([0-9]+)?$")
        channel_or_group_id = None
        channel_or_group = None
        is_group = False

        if message.channel_id is not None:
            channel_or_group_id = message.channel_id
        elif message.group_id is not None:
            channel_or_group_id = message.channel_id
            is_group = True
        else:
            if not params_regex.match(args):
                await message.reply_text(f"Please enter a channel id!\nType /{ctx.event.command} <channel id>")
                return
            channel_or_group_id = params_regex.match(args).group(1)

        # get the channel
        try:
            channel_or_group = await app.get_channel(channel_or_group_id)
            if channel_or_group is None:
                await message.reply_text(f"Channel {channel_or_group_id} not found!")
                return
        except Exception as e:
            try:
                channel_or_group = await app.get_group(channel_or_group_id)
                is_group = True
                if channel_or_group is None:
                    await message.reply_text(f"Group {channel_or_group_id} not found!")
                    return
            except Exception as e:
                await message.reply_text(f"Channel or group {channel_or_group_id} not found!")
                return

        mymessage = await message.reply_text(f"Getting messages for {'Group' if is_group else 'Channel'} {channel_or_group_id}...")
        await index_files_to_db(channel_or_group=channel_or_group, is_group=is_group, msg=mymessage, app=app)

        # get the messages
        # messages = []
        # has_more = True
        # idx = 0
        # page_size = 100
        # while has_more:
        #     if is_group:
        #         history = await app.get_group_chat_history(channel_or_group_id, channel_or_group.community_id, message.user_id, page_size, idx*page_size)
        #     else:
        #         history = await app.get_channel_chat_history(channel_or_group_id, channel_or_group.community_id, message.user_id, page_size, idx*page_size)

        #     has_more = history.messages is not None and len(
        #         history.messages) > 0

        #     if has_more:
        #         messages.extend(history.messages)

        #     idx += 1

        # await mymessage.edit_text(f"Found {len(messages)} messages...")

        # media_messages = []
        # for msg in messages:
        #     if msg.media_id is not None and msg.media_id > 0:
        #         media_messages.append(msg)

        # await mymessage.edit_text(f"Found {len(media_messages)} messages with media...")

        # total = 0

        # # index the messages
        # for msg in media_messages:
        #     total += 1

        # await mymessage.edit_text(f"Done! I saved {total} media messages!")


async def index_files_to_db(channel_or_group: Group | Channel, is_group: bool, msg: Message, app: BotApp):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0
    idx = 0
    page_size = 100
    has_more = True
    # temp.CURRENT = 200
    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False
            while has_more:
                if is_group:
                    history = await app.get_group_chat_history(channel_or_group.id, channel_or_group.community_id, msg.user_id, page_size, current)
                else:
                    history = await app.get_channel_chat_history(channel_or_group.id, channel_or_group.community_id, msg.user_id, page_size, current)

                has_more = history.messages is not None and len(
                    history.messages) > 0

                if has_more:
                    messages: List[Message] = history.messages
                    for message in messages:
                        if temp.CANCEL:
                            await msg.edit_text(f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>")
                            break
                        current += 1
                        if current % 20 == 0:
                            can = [[InlineKeyboardButton(
                                app,
                                'Cancel', callback_data='index_cancel')]]
                            reply = InlineMarkup(app, can)
                            await msg.edit_text(
                                text=f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>",
                                inline_markup=reply)
                        if not message:
                            deleted += 1
                            continue
                        elif not message.media_link:
                            no_media += 1
                            continue
                        elif message.status not in [1, 2, 3, 7]:
                            unsupported += 1
                            continue
                        media = message.media_info
                        if not media:
                            unsupported += 1
                            continue
                        aynav, vnay = await save_file(media)
                        if aynav:
                            total_files += 1
                        elif vnay == 0:
                            duplicate += 1
                        elif vnay == 2:
                            errors += 1
        except Exception as e:
            logger.exception(e)
            await msg.edit_text(f'Error: {e}')
        else:
            await msg.edit_text(f'Succesfully saved <code>{total_files}</code> to dataBase!\nDuplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\nNon-Media messages skipped: <code>{no_media + unsupported}</code>(Unsupported Media - `{unsupported}` )\nErrors Occurred: <code>{errors}</code>')
