import cv2
import threading
import time
from flask_login import current_user

class RecordingThread (threading.Thread):
    def __init__(self, name, camera, number, row):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True

        self.cap = camera
        w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #use -1 instead of fourcc. -1 means the videowriter choose for you
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('app/static/videos/{}video{}user{}.mp4'.format(str(row),str(number),str(current_user.id)),-1, 20.0, (int(w),int(h)))
        print(row, flush=True)

    def run(self):
        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
        self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()

class VideoCamera(object):
    def __init__(self,number,row):
        self.cap = None
        # Initialize video
        self.is_record = False
        self.out = None
        self.is_open = True
        self.number = number
        self.row = row

        # initialize recording tread
        self.recordingThread = None
    def __del__(self):
        try: 
            self.cap.release()
        except:
            print('probably no cap yet',flush=True)
        cv2.destroyAllWindows()

    def get_frame(self):
        if self.cap == None and self.is_open == True:
            self.cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)
            self.cap = cv2.VideoStream(src=0).start()
            time.sleep(2.0)
        ret, frame = self.cap.read()

        if ret:
            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()
        else:
            self.is_open = False
            self.cap.release()

    def start_cam(self):
        self.is_open = True
        self.cap = cv2.VideoCapture(1,cv2.CAP_DSHOW)

    def start_record(self,number,row):
        self.is_open=True
        self.is_record = True
        self.recordingThread = RecordingThread("Recording Thread", self.cap, number, row)
        time.sleep(0.3)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False
        self.is_open = False

        if self.recordingThread != None:
            self.recordingThread.stop()
            self.cap.release()
            cv2.destroyAllWindows()
            self.cap = None
        
cv2.destroyAllWindows()