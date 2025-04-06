import cv2
import P2Pro.P2Pro_cmd as P2Pro_CMD
import time

def open_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera at index 0")
        return
    
    cam_cmd = P2Pro_CMD.P2Pro()
    cam_cmd.pseudo_color_set(0, P2Pro_CMD.PseudoColorTypes.PSEUDO_BLACK_HOT)

    try:
        while True:
            ret, frame = cap.read()
            height = frame.shape[0]
            top_half = frame[:height // 2, :]

            cv2.imshow("Camera", top_half)
            cv2.waitKey(1)

    except KeyboardInterrupt:
        print("KeyboardInterrupt caught. Exiting...")
    
    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed.")

if __name__ == "__main__":
    open_camera()