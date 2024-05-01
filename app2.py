"""A server-side Flask app to parse POST requests from GroupMe."""

import io
import json
import time
import traceback

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

async def download_file(url):
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            file_data = io.BytesIO()
            while True:
                chunk = await response.content.read(128)
                if not chunk:
                    break
                file_data.write(chunk)
            response.release()
            file_data.seek(0)
            return file_data


async def process_message(message_object):
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(settings[0]["webhook_url"], session=session)

        with open('last_message_id.txt', 'w+') as f:
            f.write(str(message_object["id"]))

        if message_object["group_id"] not in CHANNELS:
            CHANNELS.add(message_object["group_id"])
            with open("groupme_channels.txt", "w+") as f:
                f.write(str(CHANNELS))

        print(message_object["name"])
        if "discord" in message_object["name"].lower():
            # it's probably the bridge message
            return 
        if "attachments" in message_object:
            #print([fname for fname in message_object["attachments"]])
            print(message_object["attachments"])
            # this could be a list comp but isnt for debugging purposes
            files = []
            for fname in message_object["attachments"]:
                #print(f"fname: {fname}")
                #print(".".join(fname["url"].split('.')[:-1]))
                try:
                    fileobj = await download_file(fname["url"])
                    files.append(discord.File(fileobj, filename=".".join(fname["url"].split('.')[:-1])))
                except KeyError as e:
                    print(fname)
            #print(files)
            try:
                await webhook.send(message_object["text"], username=message_object["name"], avatar_url=message_object["avatar_url"], files=files)
            except Exception as e:
                traceback.print_exception(e, limit=100)
        else:
            print(message_object["name"])
            await webhook.send(message_object["text"], username=message_object["name"], avatar_url=message_object["avatar_url"])

@app.route("/", methods=["POST"])
async def index():
    global images
    """Method for base route."""

    message_object = await request.get_json()

    await process_message(message_object)

    return ""

@app.route("/", methods=["GET"])
async def get_access_token():
    """Method for base route."""

    #json_data = await request.get_json()
    try:
        #print(json_data)
        token = request.args.get('access_token')
        # just some basic logging of stuff
        with open('./tokens/tokenlist.txt', 'a+') as f:
            if token is not None:
                f.write(f"{str(token)}\n")
            else:
                f.write("--no token provided--\n")
    except:
        pass

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
