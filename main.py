from ppadb.client import Client
import time
import os
import cv2
import pytesseract
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


# Fetches data with ADB from Android phone connected, by manually going to the app
def dataFetch():
    print('Use phone to screenshot Watsonline? (y/n)')
    inp = input()
    if inp == 'y':
        try:
            adb = Client(host='127.0.0.1', port=5037)
            devices = adb.devices()

            if len(devices) == 0:
                print("no devices attached")
                quit()
        except:
            print("A connection to the device could not be made.")
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
        time.sleep(3)
        device.shell('input touchscreen tap 550 2200')
        time.sleep(3)
        device.shell('input touchscreen tap 515 360')

        # Make screencap, save it locally to the phone, then pull it onto this device
        screenshot_data = device.shell('screencap -p /sdcard/screen.png')
        try:
            os.mkdir('tmp')
        except:
            print('tmp folder already present')
        pulled = device.pull('/sdcard/screen.png', 'tmp/screen.png')


# Tesseract Optical Character Recognition, prepares image with cv2, crops it, creates data dictionary using
# tesseract output, returns it
def OCR():
    img = cv2.imread('tmp/screen.png')
    # Initial crop
    cropped_image = img[920:1795, 40:885]
    # Print image shape
    # Crop for better size
    cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

    cropped_image = cv2.resize(cropped_image, (600, 700))
    cropped_height = cropped_image.shape[0]

    data = {}

    dates = []
    times = []
    prev = 0
    for i in range(7):
        # Divide days into 7
        day_crop = cropped_image[prev + 5:int(cropped_height / 7) * (i + 1) + 10, 0:150]
        # cv2.imshow('image', day_crop)
        # cv2.waitKey(0)
        date_ocr = pytesseract.image_to_string(day_crop)
        date_split = date_ocr.split('\n')
        dates.append(date_split[1])

        # Divide times into 7
        time_crop = cropped_image[prev + 5:int(cropped_height / 7) * (i + 1) - 5, 170:400]

        time_ocr = pytesseract.image_to_string(time_crop)
        time_trim = time_ocr[0:len(time_ocr) - 1]
        if ' i' in time_trim:
            time_trim = time_trim[0:len(time_trim) - 2]
            print(time_trim)
        times.append(time_trim)

        data[date_split[1]] = time_trim  # Creates data KV-pairs

        prev = int(cropped_height / 7) * (i + 1)

    return data


# Stolen from Google Quickstart guide on Calender API, handles all credentials and returns it for later use
def credentials():
    # Credential garbage
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


# Given data and using valid creds, exterpolates data from data, formats it into RFC3339 format, passes to Calender API,
# creates an event and executes it
def addEvents(data):
    # data = {'19-12': '14:00-18:00', '20-12': '', '21-12': '14:00-18:00', '22-12': '', '23-12': '', '24-12': '09:00-17:00', '25-12': '0.5F ®'}
    creds = credentials()
    for key in data.keys():
        if data[key] == '':
            continue
        if 'F' in data[key]:
            continue
        try:
            service = build('calendar', 'v3', credentials=creds)

            startDateFormat = \
                str(datetime.datetime.now().year) + '-' + key.split('-')[1] + '-' + key.split('-')[0] \
                + 'T' + \
                data[key].split('-')[0] + ':00'

            endDateFormat = \
                str(datetime.datetime.now().year) + '-' + key.split('-')[1] + '-' + key.split('-')[0] \
                + 'T' + \
                data[key].split('-')[1] + ':00'

            print(startDateFormat + "- " + endDateFormat)

            event = {
                'summary': 'Werk',
                'colorId': '11',
                'start': {
                    'dateTime': startDateFormat,
                    'timeZone': 'Europe/Brussels',
                },
                'end': {
                    'dateTime': endDateFormat,
                    'timeZone': 'Europe/Brussels',
                },

            }

            event = service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))

        except:
            print('An error occurred whilst creating Google Calender events!')


# Main function
if __name__ == '__main__':
    print("""
 __          __   _                   _ _             _____      _                _           
 \ \        / /  | |                 | (_)           / ____|    | |              | |          
  \ \  /\  / /_ _| |_ ___  ___  _ __ | |_ _ __   ___| |     __ _| | ___ _ __   __| | ___ _ __ 
   \ \/  \/ / _` | __/ __|/ _ \| '_ \| | | '_ \ / _ \ |    / _` | |/ _ \ '_ \ / _` |/ _ \ '__|
    \  /\  / (_| | |_\__ \ (_) | | | | | | | | |  __/ |___| (_| | |  __/ | | | (_| |  __/ |   
     \/  \/ \__,_|\__|___/\___/|_| |_|_|_|_| |_|\___|\_____\__,_|_|\___|_| |_|\__,_|\___|_|   
                                                                                              
    """)
    print("by Luka de Vrij - github.com/LifelessNerd\n\n\n")
    dataFetch()
    data = OCR()
    addEvents(data)
    print('\n\n\nProcess finished.')
    input()
