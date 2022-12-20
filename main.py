from io import BytesIO
import tkinter as tk
from ppadb.client import Client
import time
from PIL import Image, ImageTk
import os
import cv2
import pytesseract
from pytesseract import Output
import math

adb = Client(host='127.0.0.1', port=5037)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
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
    # Initial crop
    cropped_image = img[920:1790, 40:885]

    images = []
    prev = 0
    for i in range(7):
        cropped = cropped_image[prev:math.floor((i+1) * (cropped_image.shape[1]) / 7), 40:885]
        print(prev, math.floor((i+1) * (cropped_image.shape[1]) / 7))
        prev = math.floor((i+1) * (cropped_image.shape[1]) / 7)
        images.append(cropped)
        cv2.imshow("pic", cropped)

    cv2.waitKey(0)


    #d = pytesseract.image_to_string(cropped_image, output_type=Output.DICT)
    #print(d['text'])
