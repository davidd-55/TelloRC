from tello import Tello
import time
import sys
import cv2
import numpy as np


def intro():
    print("Welcome to the Tello RC app!")
    print("Before running this program, please ensure that you have python 3.6+, "
          "NumPy,\nand OpenCV-Python installed on your system.\n")
    print("Once you have looked over the controls, press any key + 'Enter' to continue or 'Q' to quit.\n")
    print("Here are the available controls:")
    print("\tESC - Emergency Motor Shutoff.\n\tT - Takeoff.\n\tQ - Land/Exit.\n\tW - Forward.\n\tS - Backward"
          "\n\tA - Left.\n\tD - Right.\n\tI - Up.\n\tK - Down.\n\t"
          "J - Rotate Left.\n\tL - Rotate Right.\n\t1 - Set Low Speed."
          "\n\t2 - Set Normal Speed.\n\t3 - Set High Speed.")

    usr_in = input("")
    if usr_in == "q":
        return False
    else:
        return True


def initialize():

    # establish connection, exit if fails
    conn = t.connect()
    if not conn:
        print("Could not establish Tello connection. Reboot Tello, reconnect, and try again.")
        sys.exit()
    time.sleep(1)

    t.get_battery()
    time.sleep(1)

    # in case stream was already on
    t.streamoff(response=False)
    time.sleep(1)

    # get stream data, exit if fails
    strm = t.streamon(response=False)


if __name__ == "__main__":

    # initial speed setting
    S = 30

    # enables controls and sets drone takeoff status
    control_on = True
    taken_off = False

    # set intial velocities
    for_back_v = 0
    left_right_v = 0
    up_down_v = 0
    yaw_v = 0

    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner = (10, 710)


    # give inputs
    if not intro():
        print("Exiting TelloRC...")
        sys.exit()

    # initialize Tello and video stream
    t = Tello()
    time.sleep(1)
    initialize()

    while control_on:

        if S == 30:
            text = "Speed: Low"
        elif S == 65:
            text = "Speed: Normal"
        elif S == 100:
            text = "Speed: Fast"

        frame_read = t.get_frame_read()
        frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
        frameRet = frame_read.frame
        cv2.putText(frameRet, text, bottom_left_corner, font, 1, (0, 0, 255), 2)

        cv2.imshow("Tello Feed", frameRet)

        k = cv2.waitKey(40) & 0xFF

        if k == ord('t'):
            t.takeoff(response=False)
            taken_off = True

        if k == 27:
            print("Shutting down motors...")
            t.emergency()
            break

        if k == 49:          
            if S != 30:
                print("Setting speed to 'low'")
                S = 30
            else:
                print("Speed already set to low")

        if k == 50:
            if S != 65:
                print("Setting speed to 'normal'")
                S = 65
            else:
                print("Speed already set to normal")

        if k == 51:
            if S != 100:
                print("Setting speed to 'high'")
                S = 100
            else:
                print("Speed already set to high")

        if k == ord('q'):
            control_on = False
            t.land()
        
        if taken_off:

            if k == ord('a'):
                left_right_v = -S
            elif k == ord('d'):
                left_right_v = S
            else:
                left_right_v = 0
        
            if k == ord('w'):
                for_back_v = S
            elif k == ord('s'):
                for_back_v = -S
            else:
                for_back_v = 0

            if k == ord('i'):
                up_down_v = S
            elif k == ord('k'):
                up_down_v = -S
            else:
                up_down_v = 0

            if k == ord('j'):
                yaw_v = -S
            elif k == ord('l'):
                yaw_v = S
            else:
                yaw_v = 0

            if k == ord('q'):
                control_on = False
                t.land()

            t.send_rc_control(left_right_v, for_back_v, up_down_v, yaw_v, verbose=True)

    cv2.destroyAllWindows
    t.end()
