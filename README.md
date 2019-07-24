# TelloRC

Hello all, this is a fun little program that I call TelloRC! 
With it, you can control a Tello drone from your desktop/laptop using Python.

## Functionality:
- Interact with Tello using keyboard
- See Tello video stream on desktop
- Use this module for any realtime command applications (like tracking!)
    
## Controls:
- W,A,S,D: Forward, Backward, Left, Right
- Up,Down,Left,Right Arrows: Up, Down, Rotate Left/Right
- T: Takeoff
- L/Q: Land and Exit
- ESC: Emergency Motor Shutoff
- 1,2,3: Set Speed Low, Normal, High
    
## Requirements (see requirements.txt):
- Python 3.6+ (let me know if it works on lower versions!)
- NumPy 1.16.4
- OpenCV-Python 4.1.0.25
    
## Install and Run:
- Install dependencies:

    $ pip install -r requirements.txt
    
- Run: Open a Terminal in /path/to/TelloRC and type:
    
    $ python TelloRC.py
    
- Note: You may have to add a '3' after pip and python commands if you have multiple python versions installed on your system.