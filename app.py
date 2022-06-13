#!/usr/bin/env python
import base64
from importlib import import_module

import cv2
import requests
from flask import Flask, Response
from flask_cors import CORS

# constants
API_URL = "http://10.20.229.81:8080/api/"
HEADERS = {"X-Auth-Token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImlvdCIsInRpbWVzdGFtcCI6MTY1NDU5MjQ3OX0.R_08zt-1S9vnC2OAh_IO7oHQlhrbNl-pHuAwZqCbKSY"}

# import camera driver
Camera = import_module("camera_opencv").Camera

# setup Flask app
app = Flask(__name__)

# setup CORS
CORS(app)


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route("/feed")
def video_feed():
    """
    Video feed route. Used in a <img> tag.
    """

    return Response(gen(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/photo/<movement_id>", methods=["GET"])
def take_photo_movement(movement_id):
    """Take a single photo from webcam and link it to a movement record."""

    cap = cv2.VideoCapture(0)
    _, frame = cap.read()

    _, buffer = cv2.imencode(".jpg", frame)
    jpg_as_text = base64.b64encode(buffer)

    res = requests.post(
        API_URL + "imagensMovimento.php",
        json={"entrance_log_id": movement_id, "image": jpg_as_text},
        headers=HEADERS
    )

    print(res.text)
    return 'OK'


@app.route("/photo", methods=["GET"])
def take_photo():
    """Take a single photo from webcam."""
    cap = cv2.VideoCapture("http://localhost:8080/feed")
    _, frame = cap.read()

    _, buffer = cv2.imencode(".jpg", frame)
    jpg_as_text = base64.b64encode(buffer)

    return {"image": jpg_as_text}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, threaded=True, debug=False)
