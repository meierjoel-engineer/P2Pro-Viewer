import cv2
import P2Pro.P2Pro_cmd as P2Pro_CMD
import time

def open_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera at index 0")
        return
    
    cam_cmd = P2Pro_CMD.P2Pro()
    time.sleep(1)  # Allow time for camera to initialize
    cam_cmd.pseudo_color_set(0, P2Pro_CMD.PseudoColorTypes.PSEUDO_BLACK_HOT)

    prev_toggle = None
    start_time = time.time()
    try:
        while True:
            ret, frame = cap.read()
            height = frame.shape[0]
            # top_half = frame[:height // 2, :]
            _, disabled = cam_cmd.get_shutter_state()

            diff = time.time() - start_time
            toggle_state = (diff % 20) < 10
            
            # Only if the state has changed, update the shutter.
            if prev_toggle is None or toggle_state != prev_toggle:
                if toggle_state:
                    cam_cmd.auto_shutter_disable()
                else:
                    cam_cmd.auto_shutter_enable()
                prev_toggle = toggle_state

            # _,en = cam_cmd.shutter_sta_get()
            # print(f"Shutter state: {en}")
            cv2.imshow("Camera", frame)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        print("KeyboardInterrupt caught. Exiting...")
    
    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed.")

if __name__ == "__main__":
    open_camera()