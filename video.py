import threading
import binascii
from time import sleep
from utils import base64_to_img, img_to_base64


class Camera(object):
    def __init__(self, process):
        self.to_process = []
        self.to_output = []
        self.process = process

        thread = threading.Thread(target=self.keep_processing, args=())
        thread.daemon = True
        thread.start()

    def process_one(self):
        if not self.to_process:
            return

        input_str = self.to_process.pop(0)
        input_img = base64_to_img(input_str)

       
        output_img = self.process.process(input_img)
        output_str = img_to_base64(output_img)

        self.to_output.append(binascii.a2b_base64(output_str))

    def keep_processing(self):
        while True:
            self.process_one()
            sleep(0.01)

    def enqueue_input(self, input):
        self.to_process.append(input)

    def get_frame(self):
        while not self.to_output:
            sleep(0.05)
        return self.to_output.pop(0)