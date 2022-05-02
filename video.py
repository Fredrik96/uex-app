import cv2
from datetime import time

global rec, rec_frame, out, switch, camera
rec = 0
rec_frame = 0
switch = 0

def getCam(param):
    global camera
    if param == 1:
        camera = cv2.VideoCapture(0)
    elif param == 0:
        camera.release()
        cv2.destroyAllWindows()
    return camera

def record(out):
    global rec_frame
    while(rec):
        time.sleep(0.5)
        out.write(rec_frame)

def gen_frames():
    global rec_frame
    camera = getCam(1)
    while True:
        success, frame = camera.read()
        if success:
            if(rec):
                print("Recording!", flush=True)
                rec_frame=frame
            
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
        else:
            break