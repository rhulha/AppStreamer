import cv2
import numpy as np
from flask import Flask, Response, render_template, request
import pyautogui
import pygetwindow as gw

app = Flask(__name__)

SCEENSHOT_DESKTOP = True

def getWindowWithTheLongestTitle():
    #window = gw.getWindowsWithTitle(window_title)[0]
    windows = [window for window in gw.getAllWindows() if window.title.strip()]
    for window in windows:
        if window.title == "Rechner" or window.title == "Calculator":
            return window
    if windows:
        longest_window = max(windows, key=lambda w: len(w.title))
        print(f"Window with the longest title: {longest_window.title}")
        return longest_window
    else:
        print("No windows with titles found.")



@app.route('/keypress', methods=['POST'])
def handle_keypress():
    data = request.get_json()
    key = data['key']

    window = getWindowWithTheLongestTitle()

    if window.isMinimized:
        window.restore()

    pyautogui.press(key)
    return '', 204

@app.route('/click', methods=['POST'])
def handle_click():
    data = request.get_json()
    cx = data['x']
    cy = data['y']

    window = getWindowWithTheLongestTitle()

    if window.isMinimized:
        window.restore()

    current_mouse_x, current_mouse_y = pyautogui.position()
    pyautogui.click(window.left + cx, window.top + cy)
    pyautogui.moveTo(current_mouse_x, current_mouse_y)
    return '', 204

def generate_frames():
    while True:
        
        window = getWindowWithTheLongestTitle()
        if window.isMinimized:
            window.restore()

        # better code: https://gemini.google.com/app/90812ec4339b7604


        x, y, width, height = window.left, window.top, window.width, window.height

        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        #ret, buffer = cv2.imencode('.jpg', frame, encode_param) # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    window = getWindowWithTheLongestTitle()

    if window.isMinimized:
        window.restore()
    return render_template('img.html', width=window.width, height=window.height)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
