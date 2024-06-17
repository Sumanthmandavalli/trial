# app.py
from flask import Flask, render_template, Response
import threading
from detect import detect_and_alert

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def generate_frames():
    for frame in detect_and_alert():
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    threading.Thread(target=detect_and_alert).start()
    app.run(host='0.0.0.0', port=80, debug=True)
