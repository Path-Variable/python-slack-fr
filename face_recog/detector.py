import cv2
import face_recognition
from datetime import datetime
import logging
import os
import urllib.request as request

class Detector:

    def __init__(self, channel_id, slack_client, repository):
        self.channel_id = channel_id
        self.slack_client = slack_client
        self.repository = repository

    def detect(self, image_url):
        image = self._get_image(image_url)
        detected_embeddings, faces = self._get_embeddings(image)
        if len(detected_embeddings) == 0:
            logging.info("No faces detected")
            return
        
        all_embeddings = self.repository.get_all_embeddings()
        recognized, unknown = self._compare_with_existing(all_embeddings, detected_embeddings, faces)

        if len(recognized) > 0:
            logging.info("Sending message with recognized faces")
            self._send_recognized_message(image,recognized)
            
        if len(unknown) > 0:
            logging.info("Sending message with unknown faces")
            self._send_unknown_message(unknown, image)
            self._save_embeddings(unknown)

    def _get_image(self, image_url):
            logging.info("Downloading image from %s", image_url)
            req = request.Request(image_url)
            req.add_header('Authorization', 'Bearer ' + os.environ['SLACK_API_TOKEN'])
            return face_recognition.load_image_file(request.urlopen(req))
    
    def _get_embeddings(self, image):
            faces = face_recognition.face_locations(image)
            return face_recognition.face_encodings(image, faces), faces
    
    def _compare_with_existing(self, existing, detected, faces):
        if len(existing) == 0:
            logging.info("No existing embeddings found")
            return [], tuple(zip(detected, faces))
        
        recognized = []
        unknown = []

        for d in detected:
            box = faces[detected.index(d)]
            e, m = self._is_match(existing, d)
            if m:
                name = e["name"]
                logging.info(f"Found match - {name}")
                recognized.append((name, box))
            else:
                unknown.append((d,box))

        return recognized, unknown
        
        
    def _is_match(self, existing, detected):
        match = face_recognition.compare_faces([e["embedding"] for e in existing], detected)
        for i,m in enumerate(match):
            if m:
                return existing[i], True
        return None, False

    def _save_embeddings(self, embeddings):
        for embedding, _ in embeddings:
            self.repository.save_embedding({"name": "unknown", "embedding": embedding.tolist(), "created_date": datetime.now()})

    def _send_unknown_message(self, unknown, image):
        message = f"{len(unknown)} unknown faces detected"
        colorim = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        for _, (top, right, bottom, left) in unknown:
            cv2.rectangle(colorim, (left, top), (right, bottom),
                (0, 255, 225), 2)
        _, bts = cv2.imencode('.png', colorim)
        self.slack_client.send_image(self.channel_id, message, bts.tostring())

    def _send_recognized_message(self, image, recognized):
        for (name,(top, right, bottom, left)) in recognized:
            colorim = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.rectangle(colorim, (left, top), (right, bottom),(0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(colorim, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                .8, (0, 255, 255), 2)
            _, bts = cv2.imencode('.png', colorim)
            self.slack_client.send_image_no_msg(channel_id=self.channel_id, image=bts.tostring())
    


