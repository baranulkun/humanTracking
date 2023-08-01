import cv2
from djitellopy import tello

# Image sizes
FRAME_WIDTH = 640
FRAME_HEIGHT = 380

speed = 50 #drone speed

#establishing a connection with the drone
me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()
me.takeoff()


face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml") #reading the face file

while True:
    #face detection
    frame = me.get_frame_read().frame
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    face_rects = face_cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=5)

    if len(face_rects) > 0:
        (face_x, face_y, w, h) = face_rects[0]
        track_window = (face_x, face_y, w, h)

        roi = frame[face_y:face_y + h, face_x: face_x + w]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        roi_hist = cv2.calcHist([hsv_roi], [0], None, [180], [0, 180])
        cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

        term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 5, 1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0, 180], 1)

        ret, track_window = cv2.meanShift(dst, track_window, term_crit)
        x, y, w, h = track_window

        # Calculate the center coordinates of the face
        xPos = face_x + w / 2
        yPos = face_y + h / 2

        # Controls
        contF = 50
        contB = 70
        contY = 150
        contY2 = 250
        contX = 280
        contX2 = 370

        #drone movements according to face position
        if xPos < contX:
            contX = 295
            if xPos > 290:
                contX = 280
            leftRight = -speed
            cv2.putText(frame, "Left", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            print("Sola git")
        elif xPos > contX2:
            contX2 = 360
            if xPos < 365:
                contX2 = 370
            leftRight = speed
            cv2.putText(frame, "Right", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            print("Saga git")
        else:
            leftRight = 0
            cv2.putText(frame, "Hrz Stabil", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if yPos < contY:
            contY = 160
            if yPos > 155:
                contY = 150
            upDown = speed
            cv2.putText(frame, "Up", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        elif yPos > contY2:
            contY2 = 240
            if yPos < 245:
                contY2 = 250
            upDown = -speed
            cv2.putText(frame, "Down", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        else:
            upDown = 0
            cv2.putText(frame, "Ver Stabil", (400, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        if w < contF:
            contF = 55
            if w > 52:
                contF = 50
            forwardBack = speed
            cv2.putText(frame, "Forward", (220, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        elif w > contB:
            contB = 65
            if w < 67:
                contB = 70
            forwardBack = -speed
            cv2.putText(frame, "Back", (220, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        else:
            forwardBack = 0
            cv2.putText(frame, "Stabil", (220, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.putText(frame, f"w: {w}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, f"h: {h}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        me.send_rc_control(0, forwardBack, upDown, leftRight) #drone movement
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2) #face frame
    else:
        me.send_rc_control(0, 0, 0, 0)
        print("Stabil")
    cv2.imshow("Follow", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"): #exit
        break

me.streamoff()
me.land()
cv2.destroyAllWindows()
