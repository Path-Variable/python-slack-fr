from slack import WebClient

class SlackClient:

    def __init__(self, token):
        self.client = WebClient(token=token)

    def send_image(self, channel_id, message, image):
        self.client.files_upload(
            channels=channel_id,
            content=image,filename="image.png",
            initial_comment=message)
        
    def send_image_no_msg(self, channel_id, image):
        self.client.files_upload(
            channels=channel_id,
            content=image, filename="image.png")