from picamera import PiCamera
from time import sleep
#test
camera = PiCamera()

camera.start_preview()
sleep(10)
camera.stop_preview()
