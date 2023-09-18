from scipy.spatial import distance
from imutils import face_utils
from pygame import mixer
import imutils
import dlib
import cv2
from twilio.rest import Client
import pyglet
import sys
import winsdk.windows.devices.geolocation as wdg
import asyncio
import threading


driver = input("Drivers name: ")  # Change this
contact_list = ["8921511945"]  # Change this


mixer.init()
mixer.music.load("music.wav")
foo = pyglet.media.load("alarm3.mp3")


def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


def get_current_location():
    async def getCoords():
        locator = wdg.Geolocator()
        pos = await locator.get_geoposition_async()
        return [pos.coordinate.latitude, pos.coordinate.longitude]

    def getLoc():
        return asyncio.run(getCoords())
    location = getLoc()
    lat = location[0]
    lon = location[1]

    current_location = f"http://maps.google.com/?q={lat},{lon}"
    return current_location


def send_alert_message(driver, contact_list, current_location):
    # twilio credentials
    account_sid = "********************"
    auth_token = "******************"
    sender = "+1**********"  # Fetch Phone number and put it here
    message = f"{driver} doesn't seem okay! Last known location: {current_location}"

    client = Client(account_sid, auth_token)
    for num in contact_list:
        client.messages.create(
            to="+91"+str(num),
            from_=sender,
            body=message
        )


alerted = 0


def onDriverDrowsy():
    global alerted
    if alerted >= 3:  # Modify this if required. Change to following line to add more alert, like final sure death alert.
        sys.exit()
    foo.play()

    print('Drowsyyyy!')  # For debugging
    current_location = get_current_location()
    print('Location feched!!')
    send_alert_message(driver, contact_list, current_location)
    print('Message sent!')
    alerted += 1


thresh = 0.25
drowsy = 20
fatal = 50  # Change
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
cap = cv2.VideoCapture(0)
flag = 0
while True:
    ret, frame = cap.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    subjects = detect(gray, 0)
    for subject in subjects:
        shape = predict(gray, subject)
        shape = face_utils.shape_to_np(shape)
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        if ear < thresh:
            flag += 1
            print(flag)
            if flag >= fatal:
                cv2.putText(frame, "*****WAKE UP! Message sent!*****", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "*****WAKE UP!!! Message sent*****", (10, 325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                onDriverDrowsy()

            elif flag >= drowsy:
                cv2.putText(frame, "*****ALERT!*****", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, "*****ALERT!*****", (10, 325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                # mixer.music.play()
                threading.Thread(target=mixer.music.play).start()

        else:
            flag = 0
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
cv2.destroyAllWindows()
cap.release()
