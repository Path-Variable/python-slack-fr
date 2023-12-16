import requests
import cv2
import face_recognition
from datetime import datetime
import logging
import os
import tempfile

class Detector:

    haar_cascade = "haarcascade_frontalface_default.xml"

    def __init__(self, channel_id, slack_client, repository):
        self.channel_id = channel_id
        self.slack_client = slack_client
        self.repository = repository
        self.detector = cv2.CascadeClassifier(self.haar_cascade)


    def detect(self, image_url):
        image = self._get_image(image_url)
        detected_embeddings, boxes = self._get_embeddings(image)
        if len(detected_embeddings) == 0:
            logging.info("No faces detected")
            return
        
        all_embeddings = self.repository.get_all_embeddings()
        recognized = []
        unknown = []
        for existing in all_embeddings:
            for d_embedding in detected_embeddings:
                box = boxes[detected_embeddings.index(d_embedding)]
                if self._is_match(existing, d_embedding):
                    name = existing["name"]
                    logging.info(f"Found match - {name}")
                    recognized.append((name, box))
                else:
                    unknown.append(box)

        if len(recognized) > 0:
            logging.info("Sending message with recognized faces")
            self._send_recognized_message(image,recognized)
            
        if len(unknown) > 0:
            logging.info("Sending message with unknown faces")
            self._send_unknown_message(unknown, image.tobytes())
            self._save_embeddings(unknown)

    def _get_image(self, image_url):
            logging.info("Downloading image from %s", image_url)
            headers = {'Authorization': 'Bearer ' + os.environ['SLACK_API_TOKEN']}
            with tempfile.NamedTemporaryFile() as tmpfile:
                img_stream = requests.get(image_url, headers=headers).content
                tmpfile.write(img_stream)
                return cv2.imread(tmpfile.name, cv2.IMREAD_COLOR)
    
    def _get_embeddings(self, image):
        rectangles = self.detector.detectMultiScale(image, scaleFactor=1.1, 
                        minNeighbors=5, minSize=(50, 50),
                        flags=cv2.CASCADE_SCALE_IMAGE)
        if len(rectangles) > 0:
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rectangles]
            return face_recognition.face_encodings(image, boxes), boxes
        return [], []
        
    def _is_match(self, existing, detected):
        match = face_recognition.compare_faces([existing['embedding']], detected)
        return True in match

    def _save_embeddings(self, embeddings):
        for embedding in embeddings:
            self.repository.save_embedding({"name": "unknown", "embedding": embedding.tolist(), "created_date": datetime.now()})

    def _send_unknown_message(self, boxes, image):
        message = f"{len(boxes)} unknown faces detected"
        for (top, right, bottom, left) in boxes:
            cv2.rectangle(image, (left, top), (right, bottom),
                (0, 255, 225), 2)
        self.slack_client.send_image(self.channel_id, message, image)

    def _send_recognized_message(self, image, recognized):
        for (name,(top, right, bottom, left)) in recognized:
            cv2.rectangle(image, (left, top), (right, bottom),(0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                .8, (0, 255, 255), 2)
        with tempfile.NamedTemporaryFile(suffix=".png") as tmpfile:
            cv2.imwrite(tmpfile.name, image)
            f1 = open(tmpfile.name, 'rb')
            self.slack_client.send_image_no_msg(channel_id=self.channel_id, image=f1.read())
    


