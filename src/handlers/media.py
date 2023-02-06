import asyncio
import re
from swibots import BotApp, BotContext, CommandEvent


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

        # get the messages
        messages = []
        has_more = True
        idx = 0
        page_size = 100
        while has_more:
            if is_group:
                history = await app.get_group_chat_history(channel_or_group_id, channel_or_group.community_id, message.user_id, page_size, idx*page_size)
            else:
                history = await app.get_channel_chat_history(channel_or_group_id, channel_or_group.community_id, message.user_id, page_size, idx*page_size)

            has_more = history.messages is not None and len(
                history.messages) > 0

            if has_more:
                messages.extend(history.messages)

            idx += 1

        await mymessage.edit_text(f"Found {len(messages)} messages...")

        media_messages = []
        for msg in messages:
            if msg.media_id is not None and msg.media_id > 0:
                media_messages.append(msg)

        await mymessage.edit_text(f"Found {len(media_messages)} messages with media...")

        total = 0

        # index the messages
        for msg in media_messages:
            total += 1

        await mymessage.edit_text(f"Done! I saved {total} media messages!")
