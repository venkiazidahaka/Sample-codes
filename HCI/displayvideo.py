import cv2
from pynput import mouse
from waitress import serve
from flask import Flask, render_template, Response, request, redirect, url_for 
import requests

save_path="./output/"
app = Flask(__name__)

# camera1 = cv2.VideoCapture(0)
# camera2 = cv2.VideoCapture(1)
# camera3 = cv2.VideoCapture(2)
# camera4 = cv2.VideoCapture(3)

camera1 = cv2.VideoCapture("./videos/1.mp4")
camera2 = cv2.VideoCapture("./videos/2.mp4")
camera3 = cv2.VideoCapture(2)
camera4 = cv2.VideoCapture("rtsp://hcientrance:hci206266@192.168.0.105:556/live/ch1")


save_flag=0

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/video1')
def video1():
    
    return Response(generate_frames1(), mimetype='multipart/X-mixed-replace;boundary=frame')


def generate_frames1():
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    while True:
        success, frame = camera1.read()
        if save_flag == 1:
            cv2.imwrite(save_path+"1.jpg",frame)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame +
                  b'\r\n\r\n')

@app.route('/video_save', methods=['GET','POST'])
def video_save():
    data=requests.get()
    print("Entered")
    listener = mouse.Listener(on_click=on_click)
    listener.start()


def on_click(x, y, button, pressed):
    global save_flag
    if pressed:
        save_flag=1
        print("Pressed")
    if not pressed:
        save_flag=0
        # Stop listener

@app.route('/video2')
def video2():
    
    return Response(generate_frames2(), mimetype='multipart/X-mixed-replace;boundary=frame')


def generate_frames2():
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    while True:
        success, frame = camera2.read()
        if save_flag == 1:
            cv2.imwrite(save_path+"2.jpg",frame)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame +
                  b'\r\n\r\n')

@app.route('/video3')
def video3():
    return Response(generate_frames3(), mimetype='multipart/X-mixed-replace;boundary=frame')


def generate_frames3():
    
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    while True:
        success, frame = camera3.read()
        if save_flag == 1:
            cv2.imwrite(save_path+"3.jpg",frame)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame +
                  b'\r\n\r\n')

@app.route('/video4')
def video4():
    return Response(generate_frames4(), mimetype='multipart/X-mixed-replace;boundary=frame')


def generate_frames4():
    
    listener = mouse.Listener(on_click=on_click)
    listener.start()
    
    while True:
        success, frame = camera4.read()
        if save_flag == 1:
            cv2.imwrite(save_path+"4.jpg",frame)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame +
                  b'\r\n\r\n')
        
if __name__ == '__main__':
    app.debug = True
    app.run(host="192.168.0.81", port=3055)
    # serve(app,host="0.0.0.0",port=3055)
    