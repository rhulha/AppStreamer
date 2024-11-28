import cv2
import numpy as np
from flask import Flask, Response, render_template, request, redirect
import pyautogui
import mss

app = Flask(__name__)

token = "vjgj4847thgkfoed928374uthgkfoe90394uthfg"

LOCAL_DEV = True

@app.route('/keypress', methods=['POST'])
def handle_keypress():
    auth = request.cookies.get('auth')
    if auth != token:
        return '', 401
    data = request.get_json()
    key = data['key']
    pyautogui.press(key)
    return '', 204

@app.route('/mousedown', methods=['GET'])
def handle_dragstart():
    auth = request.cookies.get('auth')
    if auth != token:
        return '', 401
    x = request.args.get('x', type=int)
    y = request.args.get('y', type=int)
    cbutton = request.args.get('button', type=int)

    button = 'left'
    if cbutton == 2:
        button = 'right'

    pyautogui.mouseDown(x, y, button=button)
    return '', 204

@app.route('/mouseup', methods=['GET'])
def handle_dragend():
    auth = request.cookies.get('auth')
    if auth != token:
        return '', 401

    x = request.args.get('x', type=int)
    y = request.args.get('y', type=int)
    cbutton = request.args.get('button', type=int)

    button = 'left'
    if cbutton == 2:
        button = 'right'

    pyautogui.mouseUp(x, y, button=button)
    return '', 204

@app.route('/mousemove', methods=['GET'])
def handle_mousemove():
    auth = request.cookies.get('auth')
    if auth != token:
        return '', 401
    x = request.args.get('x', type=int)
    y = request.args.get('y', type=int)
    if not LOCAL_DEV:
        pyautogui.moveTo(x, y)
    return '', 204

@app.route('/click', methods=['GET'])
def handle_click():
    auth = request.cookies.get('auth')
    if auth != token:
        return '', 401
    cx = request.args.get('x', type=int)
    cy = request.args.get('y', type=int)
    cbutton = request.args.get('button', type=int)

    button = 'left'
    if cbutton == 2:
        button = 'right'


    if LOCAL_DEV:
        current_mouse_x, current_mouse_y = pyautogui.position()
        pyautogui.click(cx, cy, button=button)
        pyautogui.moveTo(current_mouse_x, current_mouse_y)
    else:
        pyautogui.click(cx, cy)
    return '', 204

def generate_frames():
    while True:

        #screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)

        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        #ret, buffer = cv2.imencode('.jpg', frame, encode_param) # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    auth = request.cookies.get('auth')
    if auth != token:
        return redirect("/")
    return Response(generate_frames(),
                mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your authentication logic here
        if username == 'admin' and password == 'o@sis77':
            resp = render_template('img.html')
            response = app.make_response(resp)
            response.set_cookie('auth', token, max_age=60*60*24)
            return response
        else:
            return 'Invalid credentials', 401
        
    if request.cookies.get('auth') == token:
        return render_template('img.html')
    else:
        return render_template('login.html')

@app.route('/a')
def index():
    window = pyautogui.size()
    return render_template('img_disabled.html', width=window[0], height=window[1])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
