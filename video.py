import cv2
from datetime import datetime, time
import os

global rec, rec_frame, out, capture, switch
rec = 0
capture = 0
rec_frame = 0
out = 1
switch = True

camera = cv2.VideoCapture(0)
   
try:
    os.mkdir('./src_shots')
except OSError as error:
    pass

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.05)
        out.write(rec_frame)

def gen_frames():
    global out, capture, rec_frame
    while True:
        success, frame = camera.read()  # read the camera frame
        if success:
            if(capture):
                capture=0
                now = datetime.now()
                p = os.path.sep.join(['src_shots', "shot_{}.png".format(str(now).replace(":",''))])
                cv2.imwrite(p, frame)

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
            pass