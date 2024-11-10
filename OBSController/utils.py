import cv2


def list_capture_devices():
    """
    Lists all available video capture devices with detailed information.
    Tests indices 0-20 by default.
    """
    print("\nSearching for capture devices (this may take a moment)...")
    print("------------------------------------------------")

    for i in range(20):  # Check first 20 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Try to get device information
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = cap.getBackendName()

            print(f"\nDevice Index {i}:")
            print(f"Resolution: {width}x{height}")
            print(f"FPS: {fps}")
            print(f"Backend: {backend}")

            # Try to read a frame to make sure it's working
            ret, frame = cap.read()
            if ret:
                print("Status: Working (successfully read frame)")
                print(f"Frame size: {frame.shape}")
            else:
                print("Status: Device found but cannot read frame")

        cap.release()

    print("\nSearch complete.")
    print("------------------------------------------------")


if __name__ == "__main__":
    list_capture_devices()
