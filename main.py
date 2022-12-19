from io import BytesIO
import tkinter as tk
from ppadb.client import Client
import time
from PIL import Image, ImageTk
import os
import cv2
import pytesseract
from pytesseract import Output

adb = Client(host='127.0.0.1', port=5037)
#pytesseract.pytesseract.tesseract_cmd = r'D:\Programming\GitHub\WatsonlineCalender\.idea\venv\Scripts\pytesseract'
devices = adb.devices()


if __name__ == '__main__':

    if len(devices) == 0:
        print("no devies attached")
        quit()
    print('Use phone? (y/n)')
    inp = input()
    if inp == 'y':
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


    img = cv2.imread('tmp/screen.png')
    print(img.shape)  # Print image shape
    # Cropping an image
    cropped_image = img[920:1790, 40:885]

    # Display cropped image
    cv2.imshow("cropped", cropped_image)
    # Save the cropped image
    cv2.imwrite("tmp/Cropped Image.jpg", cropped_image)

    custom_config = r'--oem 3 --psm 6'
    pytesseract.image_to_string(img, config=custom_config)

    #d = pytesseract.image_to_string(img, output_type=Output.DICT)
    #print(d.keys())
