
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

adb = Client(host='127.0.0.1', port=5037)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
devices = adb.devices()
SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def dataFetch():
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


def OCR():
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
        day_crop = cropped_image[prev + 5:int(cropped_height / 7) * (i + 1) - 5, 0:150]
        date_ocr = pytesseract.image_to_string(day_crop)
        date_split = date_ocr.split('\n')
        dates.append(date_split[1])

        # Divide into 7 days
        time_crop = cropped_image[prev + 5:int(cropped_height / 7) * (i + 1) - 5, 170:400]
        time_ocr = pytesseract.image_to_string(time_crop)
        time_trim = time_ocr[0:len(time_ocr) - 1]
        times.append(time_trim)

        data[date_split[1]] = time_trim

        prev = int(cropped_height / 7) * (i + 1)

    return data


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


def addEvents():

    creds = credentials()
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)



if __name__ == '__main__':
    #dataFetch()
    #data = OCR()
    addEvents()
