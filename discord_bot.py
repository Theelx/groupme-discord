"""Discord-side message parsing and posting to GroupMe."""

import ast
import asyncio
import json
from io import BytesIO
from multiprocessing import Process
from typing import List, Union, Callable

import discord

from discord.ext import commands
from aiohttp import ClientSession
from discord import Attachment, Message

from app import process_message

async def post(
    session: ClientSession,
    url: str,
    payload: Union[BytesIO, dict],
) -> str:
    """Post data to a specified url."""
    async with session.post(url, data=payload) as response:
        return await response.text()


def get_prefix(
    bot_instance: commands.Bot, message: Message
) -> Callable[[commands.Bot, Message], list]:
    """Decide prefixes of the Bot."""
    prefixes = ["chat!", ">"]
    return commands.when_mentioned_or(*prefixes)(bot_instance, message)


bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents.all())
endpoint = "https://api.groupme.com/v3/bots/post"

sent_buffer = []  # Buffer for webhook message deletions.


async def send_message(message: Message) -> str:
    """Send a message to the group chat."""
    text = f"{message.author.display_name}: {message.content}".strip()
    sent_buffer.append(text)
    if len(sent_buffer) > 10:
        sent_buffer.pop(0)
    payload = {"bot_id": GROUPME_ID, "text": message.content}
    cdn = await process_attachments(message.attachments)
    if cdn is not None:
        payload.update({"picture_url": cdn})
    async with ClientSession() as session:
        return await post(session, endpoint, json.dumps(payload))


async def process_attachments(attachments: List[Attachment]) -> str:
    """Process the attachments of a message and return GroupMe objects."""
    if not attachments:
        return
    attachment = attachments[0]
    url = "https://image.groupme.com/pictures"
    if not attachment.filename.endswith(("jpeg", "jpg", "png", "gif", "webp")):
        return
    extension = attachment.filename.partition(".")[-1]
    if extension == "jpg":
        extension = "jpeg"
    handler = BytesIO()
    await attachment.save(handler)
    headers = {"X-Access-Token": GROUPME_TOKEN, "Content-Type": f"image/{extension}"}
    async with ClientSession(headers=headers) as session:
        cdn = await post(session, url, handler.read())
        cdn = json.loads(cdn)["payload"]["url"]
    return cdn


async def process_downtime():
    with open("last_message_id.txt", "r+") as f:
        id = f.read()
        if id == "":
            id = "0"

    with open("groupme_channels.txt", "r+") as f:
        try:
            group_ids = ast.literal_eval(f.read())
        except:
            group_ids = set()
    
    for group_id in group_ids:
        count = 0 # make sure while loop stops after at most 100 iterations
        payload = {"since_id": id}
        async with ClientSession() as session:
            async with session.get("https://api.groupme.com/v3/groups/" + group_id + "/messages?token=" + GROUPME_TOKEN, data=json.dumps(payload)) as response:
                newest_id = (await response.json())["response"]["messages"]
                newest_id = newest_id[0]["id"]
        while id != newest_id and count < 100:
            payload = {"after_id": id, "limit": 100}
            async with ClientSession() as session:
                async with session.get("https://api.groupme.com/v3/groups/" + group_id + "/messages?token=" + GROUPME_TOKEN, data=json.dumps(payload)) as response:
                    # reverse to get oldest first
                    messages = (await response.json())["response"]["messages"]
                    messages.reverse()
                    id = messages[-1]["id"]
                    for message in messages.copy():
                        await process_message(message)
                        await asyncio.sleep(1.5)
            count += 1
    return 1

@bot.event
async def on_ready() -> None:
    """Called when the bot loads."""
    await process_downtime()
    print("-------------\nBot is ready!\n-------------")


@bot.event
async def on_message(message: Message) -> None:
    """Called on each message sent in a channel."""
    if CHANNEL_NAME in str(message.channel):
        if not message.author.bot:
            print(await send_message(message))
        elif message.content in sent_buffer:
            await message.delete()


def main(botToken, groupmeToken, groupmeID, channelName):
    global BOT_TOKEN, GROUPME_TOKEN, GROUPME_ID, CHANNEL_NAME
    BOT_TOKEN, GROUPME_TOKEN, GROUPME_ID, CHANNEL_NAME = (
        botToken,
        groupmeToken,
        groupmeID,
        channelName,
    )

    """Start the bot with the provided token."""
    Process(target=bot.run, args=(BOT_TOKEN,)).start()
