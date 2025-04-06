import cv2

def open_camera():
    # Open the default camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera at index 0")
        return

    camera_start_time = cv2.getTickCount()
    # Create a resizable window
    cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
    
    print("Displaying camera feed. Close the window to exit.")
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame.")
            break
        
        # Get frame dimensions and crop to the top half
        height = frame.shape[0]
        top_half = frame[:height // 2, :]
        print(f" Top half shape: {top_half.shape}")
        cv2.imshow("Camera", top_half)
        cv2.waitKey(1)

        frame_count += 1
        if frame_count % 100 == 0:
            elapsed_time = (cv2.getTickCount() - camera_start_time) / cv2.getTickFrequency()
            print(f"Elapsed time: {elapsed_time:.2f} seconds")
            print(f"FPS: {frame_count / elapsed_time:.2f} frames per second")


        
    cap.release()
    cv2.destroyAllWindows()
    print("Camera closed.")

if __name__ == "__main__":
    open_camera()