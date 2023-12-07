from flask import Flask, request
from face_recog.detector import Detector
from mongo_client.repository import Repository
import os
import logging

from slack_client.slack import SlackClient

app = Flask(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

slack_client = SlackClient(os.environ['SLACK_API_TOKEN'])
repository = Repository(os.environ['MONGO_CONNECTION_STRING'])
detector = Detector(os.environ['WRITE_SLACK_CHANNEL_ID'], slack_client, repository)

@app.route('/api/events', methods=['POST'])
def add_message():
    content = request.get_json(silent=True)
    app.logger.info("received incoming event %s", content)
    if content["type"] == "url_verification":
        return content["challenge"]
    if content["token"] != os.environ['SLACK_VERIFICATION_TOKEN']:
        return "Invalid token"
    if "event" in content and "files" in content["event"]:
        if content["event"]["channel"] == os.environ['READ_SLACK_CHANNEL_ID']:
            detector.detect(content["event"]["files"][0]["url_private_download"])
    return "OK"

    