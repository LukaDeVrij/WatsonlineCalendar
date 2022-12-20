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

        screenshot_data = device.shell('screencap -p /sdcard/screen.png')
        try:
            os.mkdir('tmp')
        except:
            print('tmp folder already present')
        pulled = device.pull('/sdcard/screen.png', 'tmp/screen.png')


    img = cv2.imread('tmp/screen.png')
    # Initial crop
    cropped_image = img[920:1795, 40:885]
    # Print image shape
    # Crop for better size
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    # mon_date = cropped_image[60:120, 10:150]
    # cv2.imshow('', mon_date)
    # cv2.waitKey(0)
    # date_output = pytesseract.image_to_string(mon_date)
    # print(date_output)

    cropped_image = cv2.resize(cropped_image, (600, 700))
    cropped_height = cropped_image.shape[0]

    data = {}

    dates = []
    times = []
    prev = 0
    for i in range(7):
        # Divide into 7 days
        day_crop = cropped_image[prev+5:int(cropped_height / 7) * (i + 1) - 5, 0:150]
        date_ocr = pytesseract.image_to_string(day_crop)
        date_split = date_ocr.split('\n')
        dates.append(date_split[1])


        # Divide into 7 days
        time_crop = cropped_image[prev + 5:int(cropped_height / 7) * (i + 1) - 5, 170:400]
        time_ocr = pytesseract.image_to_string(time_crop)
        time_trim = time_ocr[0:len(time_ocr)-1]
        times.append(time_trim)

        data[date_split[1]] = time_trim

        prev = int(cropped_height / 7) * (i + 1)

    print(data)


