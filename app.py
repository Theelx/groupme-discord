"""A server-side Flask app to parse POST requests from GroupMe."""

from json import loads
from multiprocessing import Process

from io import BytesIO
import requests
from flask import Flask, request



app = Flask(__name__)

images = 0

@app.route('/', methods=['POST'])
def index():
    global images
    """Method for base route."""
    message_object = loads(request.data)
    msg_data = {
        'username': message_object['name'],
        'content': message_object['text'],
        'avatar_url': message_object['avatar_url'],
        }
    requests.post(WEBHOOK_URL, data=msg_data)
    
    if 'attachments' in message_object:
        ims = [(url['url'], BytesIO(requests.get(url['url']).content)) for url in message_object['attachments']]

        for id, (url, im) in enumerate(ims):
            extension = url.split('.')[-2]
            filename = f'./images/{images}.{extension}'
            with open(filename, "wb") as f:
                f.write(im.getbuffer())
            message_object['attachments'][id] = filename
            images += 1
        msg_data |= {'attachments': [{"id": id, "description": "Test", "filename": filename} for id, filename in enumerate(message_object['attachments'])]}
        attachment_data = []
        for id, filename in enumerate(message_object['attachments']):
            with open(filename, 'rb') as file:
                attachment_data.append({
                        "name": f"files[{id}]",
                        "value": file.read(),
                        "filename": filename,
                        "content_type": "application/octet-stream",
                    })
        attachment_data.append({"name": "payload_json", "value": msg_data.copy()})
        file_data = {}
        for p in attachment_data:
            name = p["name"]
            if name == "payload_json":
                attachment_data = {"payload_json": p["value"]}
            else:
                file_data[name] = (p["filename"], p["value"], p["content_type"])
        requests.post(WEBHOOK_URL, data=attachment_data, files=file_data)
    return ''


def main(webhookURL,*args, **kwargs):
    global WEBHOOK_URL
    WEBHOOK_URL = webhookURL
    """Start the webserver with the provided options."""
    Process(target=app.run, args=args, kwargs=kwargs).start()
