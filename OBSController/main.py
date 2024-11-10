from controller import *

import time


source_name = (
    "Video Capture Device (V4L2)"  # Replace with your actual source name from OBS
)
try:
    ws = getWS()
    oldStatus = 0
    while True:
        startRecording(ws)
        status = is_black_screen_obs(source_name)
        if status != oldStatus:
            print("New:", status)
        oldStatus = status

        if status:
            toZOOM(ws)
        else:
            toHDMI(ws)

        time.sleep(1)

except:
    print("Exception")
finally:
    stopRecording(ws)
    time.sleep(0.5)
    closeWS(ws)
