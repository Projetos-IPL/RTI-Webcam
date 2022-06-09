#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response
import cv2
import base64
import requests
from flask_cors import CORS


# import camera driver
Camera = import_module('camera_opencv').Camera
app = Flask(__name__)
CORS(app)

is_taking_picture = False

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        if not is_taking_picture:
            frame = camera.get_frame()
            yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/photo/<movement_id>', methods=['GET'])
def take_photo_movement(movement_id):
    """Take a single photo from webcam"""
    
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    
    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)

    req = requests.post(
        'http://rti-api.afonsosantos.me/api/imagensMovimento.php',
        json={'entrance_log_id': movement_id, 'image': jpg_as_text},
        headers={'X-Auth-Token': "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6ImlvdCIsInRpbWVzdGFtcCI6MTY1NDU5MjQ3OX0.R_08zt-1S9vnC2OAh_IO7oHQlhrbNl-pHuAwZqCbKSY"}
    )
    
    return 'ok'


@app.route('/photo', methods=['GET'])
def take_photo():
    """Take a single photo from webcam"""
    cap = cv2.VideoCapture("http://localhost:8080/feed")
    ret, frame = cap.read()
    
    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
        
    return { "image": jpg_as_text }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
