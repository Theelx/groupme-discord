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

from app2 import process_message
# avoid circular imports for discord_bot.py
from credentials import *

for instance in settings:
    GROUPME_ID = instance["bot_id"]
    CHANNEL_NAME = instance["channel_name"]
    WEBHOOK_URL = instance["webhook_url"]
    LOCAL_PORT = instance["local_port"]
    HTTPS = instance["https"]
    MAX_COUNT = instance["max_count"]

    try:
        gm_token = instance["groupme_token"]
    except KeyError:
        gm_token = GROUPME_TOKEN

# takes messages from groupme to discord
async def process_downtime():
    while True:
        with open("last_message_id.txt", "r+") as f:
            id_thing = int(f.read())
            if id_thing == "":
                id_thing = "0"

        with open("groupme_channels.txt", "r+") as f:
            try:
                group_ids = ast.literal_eval(f.read())
            except:
                group_ids = set()
        for group_id in group_ids:
            payload = {"since_id": id_thing}
            async with ClientSession() as session:
                async with session.get(f"https://api.groupme.com/v3/groups/{group_id}/messages?token={GROUPME_TOKEN}", data=json.dumps(payload)) as response:
                    newest_id = (await response.json())["response"]["messages"]
                    newest_id = int(newest_id[0]["id"])
            count = 0
            last_id = 0
            while last_id < newest_id and count < MAX_COUNT:
                # groupme doesn't seem to respect the limit arg
                payload = {"since_id": str(id_thing), "limit": str(MAX_COUNT)}
                async with ClientSession() as session:
                    async with session.get(f"https://api.groupme.com/v3/groups/{group_id}/messages?token={GROUPME_TOKEN}", data=json.dumps(payload)) as response:
                        # reverse to get oldest first
                        messages = (await response.json())["response"]["messages"]
                        messages.reverse()
                        last_id = int(messages[-1]["id"])
                        for message in messages.copy():
                            if count > MAX_COUNT:
                                break
                            elif int(message["id"]) < int(id_thing):
                                continue
                            await process_message(message)
                            print(message["id"], message["text"])
                            await asyncio.sleep(2)
                            count += 1
            # update last_message_id
            with open("last_message_id.txt", "w+") as f:
                f.write(str(newest_id))
        # messages get relayed from groupme to discord every 20s
        await asyncio.sleep(20)
    return 1