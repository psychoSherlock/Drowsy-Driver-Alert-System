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
import tkinter as tk


def get_driver_name():
    global driver
    driver = driver_entry.get()
    driver_label.config(text="Driver's name: " + driver)
    root.destroy()


# Create a GUI window
root = tk.Tk()
root.title("Driver's name")
root.geometry("400x400")

# Add a label for instructions
instruction_label = tk.Label(root, text="Please Enter the Driver's Name:")
instruction_label.pack(pady=10)

# Add an entry box for the driver's name
driver_entry = tk.Entry(root)
driver_entry.pack(pady=10)

# Add a button to submit the driver's name
submit_button = tk.Button(root, text="Submit", command=get_driver_name)
submit_button.pack(pady=10)

# Add a label to display the driver's name
driver_label = tk.Label(root, text="")
driver_label.pack(pady=10)

root.mainloop()


contact_list = ["8139833169",]  # Change this


mixer.init()
mixer.music.load("music.wav")
foo = pyglet.media.load("alarm3.mp3")


def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear


def detect_sunglasses(shape):
    # Define the indexes of the facial landmarks for the sunglasses detection
    sunglasses_start = 17
    sunglasses_end = 26

    # Extract the relevant landmarks for the sunglasses region
    sunglasses_region = shape[sunglasses_start:sunglasses_end]

    # Calculate the distance between the upper and lower points of the sunglasses region
    sunglasses_distance = distance.euclidean(
        sunglasses_region[0], sunglasses_region[4])

    # Define a threshold for sunglasses detection
    sunglasses_threshold = 0.25

    # Check if the distance is above the threshold
    if sunglasses_distance > sunglasses_threshold:
        return True
    else:
        return False


def get_current_location():
    class LocationThread(threading.Thread):
        def run(self):
            async def getCoords():
                locator = wdg.Geolocator()
                pos = await locator.get_geoposition_async()
                return [pos.coordinate.latitude, pos.coordinate.longitude]

            def getLoc():
                return asyncio.run(getCoords())

            location = getLoc()
            self.result = f"http://maps.google.com/?q={location[0]},{location[1]}"


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
    account_sid = "ACb8596146689ef8a86cc220edd0dbc18d"
    auth_token = "7d8a20b0d44389724095f260362f00df"
    sender = "+16073576749"  # Fetch Phone number and put it here
    message = f"{driver} doesn't seem okay! Last known location: {current_location}"

    client = Client(account_sid, auth_token)
    for num in contact_list:
        client.messages.create(
            to="+91"+str(num),
            from_=sender,
            body=message
        )


alerted = 0


def onDriverDrowsy(frame):
    global alerted
    if alerted >= 3:  # Modify this if required. Change to following line to add more alert, like final sure death alert.
        sys.exit()
    foo.play()

    print('Drowsyyyy!')  # For debugging
    # current_location = get_current_location()
    print('Location feched!!')
    # send_alert_message(driver, contact_list, current_location)
    print('Message sent!')
    alerted += 1


def onSunglassesDetected(frame):
    mixer.music.load("sunglasses.mp3")
    mixer.music.play()
    cv2.putText(frame, "*****SUNGLASSES DETECTED!*****", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, "*****SUNGLASSES DETECTED!*****", (10, 325),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


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

        # Check for sunglasses
        sunglasses_detected = detect_sunglasses(shape)
        if sunglasses_detected:
            onSunglassesDetected(frame)

        if ear < thresh:
            flag += 1
            print(flag)
            if flag >= fatal:
                cv2.putText(frame, "*****WAKE UP! Message sent!*****", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "*****WAKE UP!!! Message sent*****", (10, 325),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                onDriverDrowsy(frame)

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
