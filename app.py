"""A server-side Flask app to parse POST requests from GroupMe."""

import json

from json import loads
from multiprocessing import Process

import aiohttp
import discord
from io import BytesIO
import requests
from quart import Quart, request

from credentials import settings

app = Quart(__name__)

images = 0

CHANNELS = set()

async def process_message(message_object):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(settings[0]["webhook_url"], session=session)

        with open('last_message_id.txt', 'w+') as f:
            f.write(str(message_object["id"]))

        if message_object["group_id"] not in CHANNELS:
            CHANNELS.add(message_object["group_id"])
            with open("groupme_channels.txt", "w+") as f:
                f.write(str(CHANNELS))

        if "attachments" in message_object:
            await webhook.send(message_object["text"], username=message_object["name"], avatar_url=message_object["avatar_url"], files=[discord.File(fname) for fname in message_object["attachments"]])
        else:
            await webhook.send(message_object["text"], username=message_object["name"], avatar_url=message_object["avatar_url"])

@app.route("/", methods=["POST"])
async def index():
    global images
    """Method for base route."""

    message_object = await request.get_json()

    await process_message(message_object)

    return ""


def main(webhookURL, *args, **kwargs):
    global WEBHOOK_URL
    WEBHOOK_URL = webhookURL
    """Start the webserver with the provided options."""
    try:
        p = Process(target=app.run, args=args, kwargs=kwargs)
        p.start()
    except (KeyboardInterrupt, AttributeError) as e:
        p.kill()
        raise e
