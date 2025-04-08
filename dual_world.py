import cv2
import P2Pro.P2Pro_cmd as P2Pro_CMD
import time
import numpy as np
import matplotlib.pyplot as plt

def open_cameras():
    # Open the first and second camera using DirectShow
    cap0 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)

    if not cap0.isOpened() or not cap1.isOpened():
        print("One or both cameras did not open properly")
        return
    
    # # Initialize both cameras
    # cam_cmd = P2Pro_CMD.P2Pro()
    # # cam_cmd.pseudo_color_set(0, P2Pro_CMD.PseudoColorTypes.PSEUDO_BLACK_HOT)

    prev_toggle = None
    start_time = time.time()
    
    try:
        frame_count = 1
        while True:
            # Read frames from both cameras
            ret0, frame0 = cap0.read()
            ret1, frame1 = cap1.read()
            
            if not ret0 or not ret1:
                print("Failed to grab a frame")
                continue
                
            # Process first camera frame
            height0 = frame0.shape[0]
            width0 = frame0.shape[1]
            
            # Split frame into upper and lower halves
            upper_half0 = frame0[:height0//2, :]
            lower_half0 = frame0[height0//2:, :]
            
            # Convert both halves to grayscale if they're not already
            if len(upper_half0.shape) == 3:
                upper_half0_gray = cv2.cvtColor(upper_half0, cv2.COLOR_BGR2GRAY)
                lower_half0_gray = cv2.cvtColor(lower_half0, cv2.COLOR_BGR2GRAY)
            else:
                upper_half0_gray = upper_half0
                lower_half0_gray = lower_half0
            
            # Combine upper half (MSB) and lower half (LSB) into a higher bit depth image
            upper_half0_16bit = upper_half0_gray.astype(np.uint16) << 8
            lower_half0_16bit = lower_half0_gray.astype(np.uint16)
            combined0_16bit = upper_half0_16bit | lower_half0_16bit
            
            # Normalize and colormap for display
            normalized0 = cv2.normalize(combined0_16bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            colormap0 = cv2.applyColorMap(normalized0, cv2.COLORMAP_INFERNO)
            
            # Process second camera frame
            height1 = frame1.shape[0]
            width1 = frame1.shape[1]
            
            # Split frame into upper and lower halves
            upper_half1 = frame1[:height1//2, :]
            lower_half1 = frame1[height1//2:, :]
            
            # Convert both halves to grayscale if they're not already
            if len(upper_half1.shape) == 3:
                upper_half1_gray = cv2.cvtColor(upper_half1, cv2.COLOR_BGR2GRAY)
                lower_half1_gray = cv2.cvtColor(lower_half1, cv2.COLOR_BGR2GRAY)
            else:
                upper_half1_gray = upper_half1
                lower_half1_gray = lower_half1
            
            # Combine upper half (MSB) and lower half (LSB) into a higher bit depth image
            upper_half1_16bit = upper_half1_gray.astype(np.uint16) << 8
            lower_half1_16bit = lower_half1_gray.astype(np.uint16)
            combined1_16bit = upper_half1_16bit | lower_half1_16bit
            
            # Normalize and colormap for display
            normalized1 = cv2.normalize(combined1_16bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            colormap1 = cv2.applyColorMap(normalized1, cv2.COLORMAP_INFERNO)
            
            # Display statistics
            if frame_count % 100 == 0:
                print(f"Camera 1 frame shape: {frame0.shape}")
                print(f"Camera 2 frame shape: {frame1.shape}")
                print(f"Camera 1 16-bit range: {np.min(combined0_16bit)} to {np.max(combined0_16bit)}")
                print(f"Camera 2 16-bit range: {np.min(combined1_16bit)} to {np.max(combined1_16bit)}")
                
            frame_count += 1
            
            # Shutter management with time-based toggling
            diff = time.time() - start_time
            toggle_state = (diff % 20) < 10
            
            # Only if the state has changed, update the shutter
            # if prev_toggle is None or toggle_state != prev_toggle:
            #     if toggle_state:
            #         cam_cmd.auto_shutter_disable()
            #     else:
            #         cam_cmd.auto_shutter_enable()
            #     prev_toggle = toggle_state
            
            # Create a side-by-side view
            # Ensure both images are the same height for concatenation
            h0, w0 = colormap0.shape[:2]
            h1, w1 = colormap1.shape[:2]
            
            # Resize if heights don't match
            if h0 != h1:
                if h0 > h1:
                    colormap1 = cv2.resize(colormap1, (int(w1 * h0 / h1), h0))
                else:
                    colormap0 = cv2.resize(colormap0, (int(w0 * h1 / h0), h1))
            
            # Concatenate images horizontally
            side_by_side = np.hstack((colormap0, colormap1))
            
            # Display the combined image
            cv2.imshow("Dual Thermal Cameras", side_by_side)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("KeyboardInterrupt caught. Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap0.release()
        cap1.release()
        cv2.destroyAllWindows()
        print("Cameras closed.")

if __name__ == "__main__":
    open_cameras()