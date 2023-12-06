from flask import Flask, request
from face_recog.detector import Detector
from mongo_client.repository import Repository
import os

from slack_client.slack import SlackClient

app = Flask(__name__)

slack_client = SlackClient(os.environ['SLACK_API_TOKEN'])
repository = Repository(os.environ['MONGO_CONNECTION_STRING'])
detector = Detector(os.environ['SLACK_CHANNEL_ID'], slack_client, repository)

@app.route('/api/message_event', methods=['POST'])
def add_message():
    content = request.get_json(silent=True)
    if content["subtype"] == "file_share":
        detector.detect(content["file"]["url_private_download"])
    