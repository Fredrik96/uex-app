import cv2
from datetime import datetime, time
import os

global rec, rec_frame, out, switch, camera
rec = 0
rec_frame = 0
switch = 0

try:
    os.mkdir('./src_shots')
except OSError as error:
    pass

def getCam(param):
    global camera
    if param == 1:
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    elif param == 0:
        camera.release()
        cv2.destroyAllWindows()
    return camera

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

def gen_frames():
    global rec_frame
    camera = getCam(1)
    while True:
        success, frame = camera.read()
        if success:
            if(rec):
                rec_frame=frame
                frame= cv2.putText(cv2.flip(frame,1),"Recording...", (0,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),4)
                frame=cv2.flip(frame,1)
            
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
        else:
            break