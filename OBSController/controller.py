#!/usr/bin/env python3

import sys
import time
import cv2
import numpy as np
import logging

# logging.basicConfig(level=logging.DEBUG)

sys.path.append("../")
from obswebsocket import obsws, requests  # noqa: E402

host = "localhost"
# host = "172.31.130.1"
port = 4455
password = "p23iIVMuuEZzx1CG"

HDMISCENE = "HDMIInputView"
ZOOMSCENE = "ZoomView"


def getWS():

    ws = obsws(host, port, password, legacy=False)
    ws.connect()
    return ws


def toHDMI(ws):
    ws.call(requests.SetCurrentProgramScene(**{"sceneName": HDMISCENE}))


def toZOOM(ws):
    ws.call(requests.SetCurrentProgramScene(**{"sceneName": ZOOMSCENE}))
    # scenes = ws.call(requests.GetSceneList())
    # print(scenes.getScenes())
    # for s in scenes.getScenes():
    #     name = s.get('sceneName')
    #     print("Switching to {}".format(name))
    #     ws.call(requests.SetCurrentProgramScene(**{'sceneName': name}))
    #     time.sleep(2)
    # print("End of list")


def closeWS(ws):
    ws.disconnect()


def startRecording(ws):
    ws.call(requests.StartRecord())


def stopRecording(ws):
    ws.call(requests.StopRecord())


def is_black_screen(device_id=0, intensity_threshold=10, std_threshold=5):
    """
    Check if webcam input appears to be a black screen using both mean intensity
    and standard deviation of pixel values.

    Parameters:
    device_id (int): Camera device ID
    intensity_threshold (int): Maximum average pixel intensity to consider as black (0-255)
    std_threshold (int): Maximum standard deviation to consider as black

    Returns:
    bool: True if screen is black, False otherwise
    """
    try:
        cap = cv2.VideoCapture(device_id)
        if not cap.isOpened():
            return False

        # Read a few frames to let the camera adjust
        for _ in range(3):
            cap.read()

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return False

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate both mean and standard deviation
        mean_intensity = np.mean(gray)
        std_intensity = np.std(gray)
        print(mean_intensity, std_intensity)
        # A true black screen should have both low mean and low standard deviation
        return mean_intensity < intensity_threshold and std_intensity < std_threshold

    except:
        return False


import sys
import numpy as np
from obswebsocket import obsws, requests
import base64
from io import BytesIO
from PIL import Image


def is_black_screen_obs(source_name, intensity_threshold=10, std_threshold=5):
    """
    Check if an OBS source is outputting a black screen by analyzing its content

    Parameters:
    source_name (str): Name of the source in OBS
    intensity_threshold (int): Maximum average pixel intensity to consider as black
    std_threshold (int): Maximum standard deviation to consider as black

    Returns:
    bool: True if screen appears to be black, False otherwise
    """
    try:
        ws = obsws("localhost", 4455, "p23iIVMuuEZzx1CG", legacy=False)
        ws.connect()

        # Get source screenshot
        response = ws.call(
            requests.GetSourceScreenshot(sourceName=source_name, imageFormat="png")
        )

        ws.disconnect()

        # Decode the base64 image
        image_data = base64.b64decode(response.getImageData().split(",")[1])
        image = Image.open(BytesIO(image_data))

        # Convert to grayscale numpy array
        gray_array = np.array(image.convert("L"))

        # Calculate metrics
        mean_intensity = np.mean(gray_array)
        std_intensity = np.std(gray_array)

        # print(f"Debug - Mean intensity: {mean_intensity:.2f}, Std: {std_intensity:.2f}")

        # A true black screen should have both low mean and low standard deviation
        return mean_intensity < intensity_threshold and std_intensity < std_threshold

    except Exception as e:
        print(f"Error checking source: {str(e)}")
        return False


def test_source_values(source_name):
    """
    Test function to print the intensity values for a given source
    """
    try:
        ws = obsws("localhost", 4455, "p23iIVMuuEZzx1CG", legacy=False)
        ws.connect()

        response = ws.call(
            requests.GetSourceScreenshot(sourceName=source_name, imageFormat="png")
        )

        ws.disconnect()

        # Decode and analyze the image
        image_data = base64.b64decode(response.getImageData().split(",")[1])
        image = Image.open(BytesIO(image_data))
        gray_array = np.array(image.convert("L"))

        mean_intensity = np.mean(gray_array)
        std_intensity = np.std(gray_array)
        min_intensity = np.min(gray_array)
        max_intensity = np.max(gray_array)

        print("\nSource Analysis:")
        print(f"Mean intensity: {mean_intensity:.2f}")
        print(f"Standard deviation: {std_intensity:.2f}")
        print(f"Min intensity: {min_intensity}")
        print(f"Max intensity: {max_intensity}")

    except Exception as e:
        print(f"Error analyzing source: {str(e)}")


def list_obs_sources():
    """
    Lists all available sources in OBS across all scenes.
    Returns a dict of scenes and their sources.
    """
    try:
        ws = obsws("localhost", 4455, "p23iIVMuuEZzx1CG", legacy=False)
        ws.connect()

        print("\nAvailable OBS Sources:")
        print("---------------------")

        # Get list of all scenes
        scene_list = ws.call(requests.GetSceneList())

        for scene in scene_list.getScenes():
            scene_name = scene["sceneName"]
            print(f"\nScene: {scene_name}")

            # Get sources in this scene
            scene_items = ws.call(requests.GetSceneItemList(sceneName=scene_name))

            if scene_items.getSceneItems():
                for item in scene_items.getSceneItems():
                    source_name = item["sourceName"]
                    source_type = (
                        item["inputKind"] if "inputKind" in item else "Unknown"
                    )
                    print(f"  - {source_name} (Type: {source_type})")
            else:
                print("  No sources in this scene")

        ws.disconnect()

    except Exception as e:
        print(f"Error listing sources: {str(e)}")

    # Example of how to use with is_black_screen_obs:
    # source_name = "Your Source Name Here"  # Use name from the list above
    # is_black = is_black_screen_obs(source_name)
    # print(f"Is {source_name} black? {is_black}")


source_name = (
    "Video Capture Device (V4L2)"  # Replace with your actual source name from OBS
)
if __name__ == "__main__":
    # source_name = "USB3 Video"  # Replace with your source name
    list_obs_sources()
    # First test the values
    # print("Testing source values...")
    # test_source_values(source_name)

    # Then check if it's black
    is_black = is_black_screen_obs(source_name)
    print(f"\nSource appears to be {'black' if is_black else 'not black'}")
