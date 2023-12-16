from flask import Flask, request
from face_recog.detector import Detector
from mongo_client.repository import Repository
import os
import logging
from threading import Thread

from slack_client.slack import SlackClient

class DetectorFacade:

    def __init__(self, detector, slack_verification_token, read_channel):
        self.detector = detector
        self.slack_verification_token = slack_verification_token
        self.read_channel = read_channel

    def process(self, content):
        if content["token"] != self.slack_verification_token:
            app.logger.info("Invalid token")
            return
        if "event" in content and "files" in content["event"]:
            app.logger.info("Received event contains files")
            # TODO: switch to manageable list of channel ids
            if content["event"]["channel"] == self.read_channel:
                detector.detect(content["event"]["files"][0]["url_private_download"])
            else: 
                app.logger.info(f'Channel ID {content["event"]["channel"]} is not on read list. Skipping event')

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
detector_facade = DetectorFacade(detector, os.environ['SLACK_VERIFICATION_TOKEN'], os.environ['READ_SLACK_CHANNEL_ID'])

@app.route('/api/events', methods=['POST'])
def add_message():
    content = request.get_json(silent=True)
    app.logger.info("received incoming event %s", content)
    if content["type"] == "url_verification":
        # TODO: get token from initial challenge instead of using env variable
        return content["challenge"]
    Thread(target=detector_facade.process, args=(content,)).start()
    return "OK"


    