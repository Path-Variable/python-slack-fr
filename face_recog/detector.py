import requests
import cv2
import io
import face_recognition
import datetime
import numpy as np
import logging

class Detector:

    haar_cascade = "haarcascade_frontalface_default.xml"

    def __init__(self, channel_id, slack_client, repository):
        self.channel_id = channel_id
        self.slack_client = slack_client
        self.repository = repository
        self.detector = cv2.CascadeClassifier(Detector.haar_cascade)


    def detect(self, image_url):
        image = self._get_image(image_url)
        detected_embeddings, boxes = self._get_embeddings(image)
        if len(detected_embeddings) == 0:
            logging.info("No faces detected")
            return
        
        all_embeddings = self.repository.get_all_embeddings()
        recognized = []
        for existing in all_embeddings:
            for d_embedding in detected_embeddings:
                if self._is_match(existing, d_embedding):
                    recognized.append(existing["name"], boxes[detected_embeddings.index(d_embedding)])

        if len(recognized) > 0:
            self._send_recognized_message(image,recognized)
            return
                          
        self._save_embeddings(detected_embeddings)
        self._send_unknown_message(boxes, image)

    def _get_image(self, image_url):
        img_stream = io.BytesIO(requests.get(image_url).content)
        return cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8), 1)
    
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
            self.repository.save_embedding({"name": "unknown", "embedding": embedding, "created_date": datetime.now()})

    def _send_unknown_message(self, boxes, image):
        message = f"{len(boxes)} unknown faces detected"
        for (top, right, bottom, left) in zip(boxes):
            cv2.rectangle(image, (left, top), (right, bottom),
                (0, 255, 225), 2)
        self.slack_client.send_image(self.channel_id, message, image)

    def _send_recognized_message(self, image, recognized):
        for ((top, right, bottom, left), name) in recognized:
            cv2.rectangle(image, (left, top), (right, bottom),(0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                .8, (0, 255, 255), 2)
        self.slack_client.send_image(self.channel_id, image.tobytes())


