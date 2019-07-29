"""
Helper file that defines certain interactions/commands with a DJI Tello drone.
Also displays a video feed from Tello, all credit for this functionality goes
to Damia Fuentes
Damia's GitHub - https://github.com/damiafuentes/DJITelloPy
"""

import socket
import time
import threading
import cv2
from threading import Thread


class Tello(object):

    UDP_IP = "192.168.10.1"
    UDP_PORT = 8889
    print("Tello UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)

    # Video stream, server socket
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111

    # VideoCapture object
    cap = None
    background_frame_read = None
    stream_on = False

    # time between individual real-time commands
    TIME_BTW_RTCMNDS = .5
    CMND_TIMEOUT = 5

    def __init__(self, interface=2, timeout=CMND_TIMEOUT):
        self.address = (self.UDP_IP, self.UDP_PORT)
        self.clientSock = socket.socket(socket.AF_INET,  # Interwebs
                                        socket.SOCK_DGRAM)  # UDP
        self.clientSock.bind(('', self.UDP_PORT))  # For UDP response
        self.response = None
        self.stream_on = False

        # set timeout in seconds
        self.clientSock.settimeout(timeout)

        # Run tello udp receiver on background
        thread = threading.Thread(target=self.run_udp_receiver, args=())
        thread.daemon = True
        thread.start()

    def run_udp_receiver(self):
        # FROM DAMIA FUENTES -
        # Setup drone UDP receiver & listens for Tello response.
        # Must be run from a background thread in order to not
        #  block the main thread.
        while True:
            try:
                # buffer size is 1024 bytes
                self.response, _ = self.clientSock.recvfrom(1024)
            except Exception as e:
                print(e)
                break

    def get_udp_video_address(self):
        # printout video communication lane
        return 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT)

    def get_video_capture(self):
        # FROM DAMIA FUENTES -
        # Get the VideoCapture object from the camera drone
        # Returns: VideoCapture

        if self.cap is None:
            self.cap = cv2.VideoCapture(self.get_udp_video_address())

        if not self.cap.isOpened():
            self.cap.open(self.get_udp_video_address())

        return self.cap

    def get_frame_read(self):
        # FROM DAMIA FUENTES -
        # Get the BackgroundFrameRead object from the camera drone.
        # Then, you just need to callbackgroundFrameRead.frame
        # to get the actual frame received by the drone.
        # Returns: BackgroundFrameRead

        if self.background_frame_read is None:
            self.background_frame_read = BackgroundFrameRead(
                self, self.get_udp_video_address()).start()
        return self.background_frame_read

    def stop_video_capture(self):
        return self.streamoff()

    def send_command_response(self, message, counter=5, verbose=True):
        # command to be sent to Tello
        # True if received, False otherwise
        self.clientSock.sendto(bytes(message, 'utf-8'), (self.UDP_IP,
                                                         self.UDP_PORT))

        # To execute if recursive call hasn't hit base case
        if counter != 0:
            if verbose:
                print('sent', '"'+message+'"')
                print('waiting for response...')

            # Get return data:
            try:
                data, server = self.clientSock.recvfrom(self.UDP_PORT)
                if verbose:
                    print('recieved', data, server)
                time.sleep(1)
                return True

            # Tello did not respond to command, trying again recursively with
            # verbose enabled
            except socket.timeout:
                if verbose:
                    print('timeout, recieved no data.')
                return self.send_command_response(message, counter=counter-1,
                                                  verbose=True)

        # base case stops connection attempts and returns str
        else:
            print("Aborting last command: '" + message + "'")
            return False

    def send_command_no_response(self, message):
        # send command to Tello without awaiting response
        self.clientSock.sendto(bytes(message, 'utf-8'), (self.UDP_IP,
                                                         self.UDP_PORT))
        print("Sent command " + message + "; no response expected.")

    """
    remaining defs in class Tello are commands that utilize both
    the send_command_response and the send_command_no_response
    to communicate w/Tello and send instructions or gather data
    """

    def connect(self, response=True):
        # enables SDK mode for commands
        # returns T/F

        if response:
            return self.send_command_response("command")
        else:
            return self.send_command_no_response("command")

    def takeoff(self, response=True):
        # takeoff Tello
        # returns T/F

        if response:
            return self.send_command_response("takeoff")
        else:
            return self.send_command_no_response("takeoff")

    def land(self, response=True):
        # land Tello
        # returns T/F

        if response:
            return self.send_command_response("land")
        else:
            return self.send_command_no_response("land")

    def streamon(self, response=True):
        # enables data stream from Tello camera
        # returns T/F

        result = None
        if response:
            result = self.send_command_response("streamon")
        else:
            self.send_command_no_response("streamon")

        if result is True:
            self.stream_on = True
        return result

    def streamoff(self, response=True):
        # disables data stream from Tello camera
        # returns T/F

        result = None
        if response:
            result = self.send_command_response("streamoff")
        else:
            self.send_command_no_response("streamoff")

        if result is True:
            self.stream_on = False
        return result

    def emergency(self, response=True):
        # emergency halt all motors
        # return T/F

        if response:
            return self.send_command_response("emergency")
        else:
            return self.send_command_no_response("emergency")

    def move(self, direction, x, response=True):
        # move Tello while in air
        # Args: direction - up, down, left, right, forward, back
        #       x - 20-500 (cm)
        # return T/F

        if response:
            return self.send_command_response(direction + " " + str(x))
        else:
            return self.send_command_response(direction + " " + str(x))

    def rotate_cw(self, x, response=True):
        # yaw Tello x degrees clockwise
        # return T/F

        if response:
            return self.send_command_response("cw " + str(x))
        else:
            return self.send_command_no_response("cw " + str(x))

    def rotate_ccw(self, x, response=True):
        # yaw Tello x degrees counter clockwise
        # return T/F

        if response:
            return self.send_command_response("ccw " + str(x))
        else:
            return self.send_command_no_response("ccw " + str(x))

    def flip(self, direction, response=True):
        # flip Tello in specified direction
        # directions: l (left), r (right), f (forward), b (backward)
        # return T/F

        if response:
            return self.send_command_response("flip " + direction)
        else:
            return self.send_command_no_response("flip " + direction)

    def go_xyz_speed(self, x, y, z, speed, response=True):
        # fly Tello to xyz coordinate with at speed cm/s
        # 20 < xyz < 500
        # 10 < speed < 100
        # return T/F

        if response:
            return self.send_command_response('go %s %s %s %s' % (x, y, z, speed))
        else:
            return self.send_command_no_response('go %s %s %s %s' % (x, y, z, speed))

    #TODO: implement curve

    def set_speed(self, x, response=True):
        # set speed to x cm/s
        # return T/F

        if response:
            self.send_command_response("speed " + str(x))
        else:
            self.send_command_no_response("speed " + str(x))

    last_rtcmnd_sent = 0

    def send_rc_control(self, left_right_velocity, forward_backward_velocity,
                        up_down_velocity, yaw_velocity, verbose=False):
        # Credit to Damia Fuentes for RealTime commands function
        # Send RC control via four channels. Command is sent every
        # self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        # Arguments:
        #    left_right_velocity: -100~100 (left/right)
        #    forward_backward_velocity: -100~100 (forward/backward)
        #    up_down_velocity: -100~100 (up/down)
        #    yaw_velocity: -100~100 (yaw)
        # Returns: T/F

        if int(time.time() * 1000) - self.last_rtcmnd_sent < self.TIME_BTW_RTCMNDS:
            pass
        else:
            if verbose:
                self.last_rc_control_sent = int(time.time() * 1000)
                return self.send_command_no_response('rc %s %s %s %s' % (left_right_velocity, forward_backward_velocity,
                                                                            up_down_velocity, yaw_velocity))
            else: 
                return self.send_command_no_response('rc ' + left_right_velocity + " " + forward_backward_velocity + 
                                                     " " + up_down_velocity + " " + yaw_velocity)
    
    def get_battery(self):
        # prints battery % to console
        # returns T/F
        return self.send_command_response("battery?")

    def get_speed(self):
        # print current speed in cm/s
        # returns T/F
        return self.send_command_response("speed?")

    def get_flight_time(self):
        # prints flight time (s)
        # returns T/F
        return self.send_command_response("time?")

    def get_height(self):
        # prints height (cm)
        # returns T/F
        return self.send_command_response("height?")

    def get_temp(self):
        # prints temp (C)
        # returns T/F
        return self.send_command_response("temperature?")

    def get_attitude(self):
        # prints IMU data (pitch roll yaw)
        # returns T/F
        return self.send_command_response("attitude?")

    def get_wifi(self):
        # prints wifi SNR
        # returns T/F
        return self.send_command_response("wifi?")

    def end(self):
        # Call this method when you want to end the tello object
        if self.stream_on:
            self.streamoff()
        if self.background_frame_read is not None:
            self.background_frame_read.stop()
        if self.cap is not None:
            self.cap.release()


class BackgroundFrameRead:
    """
    All credit for this class goes to Damia Fuentes
    @ https://github.com/damiafuentes/DJITelloPy
    This class read frames from a VideoCapture in background.
    Then, just call backgroundFrameRead.frame to get the actual one.
    """

    def __init__(self, tello, address):
        tello.cap = cv2.VideoCapture(address)
        self.cap = tello.cap

        if not self.cap.isOpened():
            self.cap.open(address)

        self.grabbed, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update_frame, args=()).start()
        return self

    def update_frame(self):
        while not self.stopped:
            if not self.grabbed or not self.cap.isOpened():
                self.stop()
            else:
                (self.grabbed, self.frame) = self.cap.read()

    def stop(self):
        self.stopped = True
