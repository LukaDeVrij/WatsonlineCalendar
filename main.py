from io import BytesIO
import tkinter as tk
from ppadb.client import Client
import time
from PIL import Image, ImageTk
import os
import pytesseract

adb = Client(host='127.0.0.1', port=5037)
devices = adb.devices()
if __name__ == '__main__':

    if len(devices) == 0:
        print("no devies attached")
        quit()

    device = devices[0]
    # Navigate to Watsonline, click schedules
    device.shell('input touchscreen swipe 550 2380 550 2000 200')
    time.sleep(1)
    device.shell('input touchscreen tap 550 2200')
    time.sleep(1)
    device.shell('input text "watsonline"')
    time.sleep(1)
    device.shell('input touchscreen tap 125 400')
    time.sleep(1)
    device.shell('input touchscreen tap 550 2200')
    time.sleep(1)
    device.shell('input touchscreen tap 515 360')

    # Tesseract OCR

    data = device.shell('screencap -p /sdcard/screen.png')
    try:
        os.mkdir('tmp')
    except:
        print('tmp folder already present')
    pulled = device.pull('/sdcard/screen.png', 'tmp/screen.png')
    pytesseract.pytesseract.tesseract_cmd = r'D:\Programming\GitHub\WatsonlineCalender\.idea\venv\Scripts\pytesseract.exe'
    print(pytesseract.image_to_string(Image.open('tmp/screen.png'), lang='en'))
