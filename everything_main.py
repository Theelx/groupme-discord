"""Main entry point for running both server and bot."""

import app2
import discord_bot
import ssl
import time

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

    flask_options = {}

    if "false" not in str(LOCAL_PORT):
        flask_options = {"host": instance["ip"], "port": LOCAL_PORT}
    
    if "true" in str(HTTPS):
        #context = ssl.SSLContext()
        #context.load_cert_chain('/etc/letsencrypt/live/wedois.win/fullchain.pem', '/etc/letsencrypt/live/wedois.win/privkey.pem')
        flask_options.update({"certfile": '/etc/letsencrypt/live/wedois.win/cert.pem', "keyfile": "/etc/letsencrypt/live/wedois.win/privkey.pem"})

    discord_bot.main(BOT_TOKEN, gm_token, GROUPME_ID, CHANNEL_NAME, MAX_COUNT)
    app2.main(WEBHOOK_URL, **flask_options)
    time.sleep(1)
