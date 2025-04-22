import cv2
import time
import numpy as np
import threading
import queue
import hashlib

# Global variables for thread communication
frame_queue0 = queue.Queue(maxsize=2)
frame_queue1 = queue.Queue(maxsize=2)
stop_threads = False

def process_thermal_frame(frame):
    """Convert a raw thermal frame to 16-bit data and colormap visualization"""
    height = frame.shape[0]
    width = frame.shape[1]
    
    # Split frame into upper and lower halves
    upper_half = frame[:height//2, :]
    lower_half = frame[height//2:, :]
    
    # Convert to grayscale if needed
    if len(upper_half.shape) == 3:
        upper_half_gray = cv2.cvtColor(upper_half, cv2.COLOR_BGR2GRAY)
        lower_half_gray = cv2.cvtColor(lower_half, cv2.COLOR_BGR2GRAY)
    else:
        upper_half_gray = upper_half
        lower_half_gray = lower_half
    
    # Combine as 16-bit
    upper_half_16bit = upper_half_gray.astype(np.uint16) << 8
    lower_half_16bit = lower_half_gray.astype(np.uint16)
    combined_16bit = upper_half_16bit | lower_half_16bit
    
    # Normalize and colormap for display
    normalized = cv2.normalize(combined_16bit, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    colormap = cv2.applyColorMap(normalized, cv2.COLORMAP_INFERNO)
    
    return colormap, combined_16bit

def is_duplicate_frame(frame, prev_frame):
    """Check if a frame is identical to the previous one"""
    if prev_frame is None:
        return False
    
    # Simple hash-based comparison
    hash1 = hashlib.md5(frame.tobytes()).hexdigest()
    hash2 = hashlib.md5(prev_frame.tobytes()).hexdigest()
    
    return hash1 == hash2

def camera_thread(camera_index, output_queue, start_delay=0):
    """Thread function for capturing frames from a camera"""
    # Apply start delay if specified
    if start_delay > 0:
        print(f"Camera {camera_index} waiting {start_delay}s before starting...")
        time.sleep(start_delay)
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print(f"Error opening camera {camera_index}")
        return
    
    prev_frame = None
    frame_count = 0
    start_time = time.time()
    
    while not stop_threads:
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read from camera {camera_index}")
            time.sleep(0.1)
            continue
        
        # If the queue is full, get rid of the oldest frame
        if output_queue.full():
            try:
                output_queue.get_nowait()
            except queue.Empty:
                pass
        
        # Check if this frame is a duplicate
        is_duplicate = is_duplicate_frame(frame, prev_frame)
        
        # Add to queue with duplicate flag
        output_queue.put((frame, is_duplicate, time.time()))
        prev_frame = frame.copy()
        
        # Calculate and log FPS for this camera thread
        frame_count += 1
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            camera_fps = frame_count / elapsed
    
    cap.release()
    print(f"Camera {camera_index} thread stopped")

def open_cameras():
    global stop_threads
    
    # Create window first for better display performance
    cv2.namedWindow("Dual Thermal Cameras", cv2.WINDOW_NORMAL)
    
    # Start camera capture threads - camera 1 starts 2 seconds later
    print("Starting camera threads...")
    thread0 = threading.Thread(target=camera_thread, args=(0, frame_queue0, 0))
    thread1 = threading.Thread(target=camera_thread, args=(1, frame_queue1, 2))  # 2 second delay
    
    thread0.daemon = True
    thread1.daemon = True
    
    thread0.start()
    thread1.start()
    
    # Wait for initial frames from first camera
    print("Waiting for initial frames...")
    while frame_queue0.empty():
        time.sleep(0.1)
    
    print("Starting main processing loop...")
    
    # Variables for the main loop
    frame_count = 0
    fps_start_time = time.time()
    
    # Store processed frames and their status
    last_display0 = None
    last_display1 = None
    
    # FPS calculation
    fps_frames = 0
    fps_update_interval = 1  # Update FPS every half second
    
    try:
        while True:
            updated = False
            current_time = time.time()
            
            # Process camera 0 (first camera)
            if not frame_queue0.empty():
                frame0, is_dup0, timestamp0 = frame_queue0.get_nowait()
                if not is_dup0:
                    # Process new frame
                    colormap0, _ = process_thermal_frame(frame0)
                    # Add camera identifier
                    cv2.putText(colormap0, "Camera 0", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    last_display0 = colormap0
                    updated = True
                    fps_frames += 1
                else:
                    # Create black image for duplicate frame
                    if last_display0 is not None:
                        black_frame = np.zeros_like(last_display0)
                        last_display0 = black_frame
                        updated = True
            
            # Process camera 1 (second camera)
            if not frame_queue1.empty():
                frame1, is_dup1, timestamp1 = frame_queue1.get_nowait()
                if not is_dup1:
                    # Process new frame
                    colormap1, _ = process_thermal_frame(frame1)
                    # Add camera identifier
                    cv2.putText(colormap1, "Camera 1", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    last_display1 = colormap1
                    updated = True
                    fps_frames += 1
                else:
                    # Create black image for duplicate frame
                    if last_display1 is not None:
                        black_frame = np.zeros_like(last_display1)
                        last_display1 = black_frame
                        updated = True
            
            # Update the FPS calculation and display every interval
            elapsed_since_fps_update = current_time - fps_start_time
            if elapsed_since_fps_update >= fps_update_interval:
                # Calculate FPS based on recent frames
                if fps_frames > 0:
                    current_fps = fps_frames / elapsed_since_fps_update
                    print(f"Current FPS: {current_fps:.1f}")
                    
                    # Reset counters for next interval
                    fps_frames = 0
                    fps_start_time = current_time
            
            # Display side by side if both frames are available
            if updated and last_display0 is not None and last_display1 is not None:
                # Ensure both images are the same size for side-by-side display
                h0, w0 = last_display0.shape[:2]
                h1, w1 = last_display1.shape[:2]
                
                # Resize if heights don't match
                if h0 != h1:
                    if h0 > h1:
                        resized_display1 = cv2.resize(last_display1, (int(w1 * h0 / h1), h0))
                        resized_display0 = last_display0
                    else:
                        resized_display0 = cv2.resize(last_display0, (int(w0 * h1 / h0), h1))
                        resized_display1 = last_display1
                else:
                    resized_display0 = last_display0
                    resized_display1 = last_display1
                
                # Combine side by side
                side_by_side = np.hstack((resized_display0, resized_display1))
                
                # Add FPS counter to the combined display
                elapsed_since_fps_update = current_time - fps_start_time
                if elapsed_since_fps_update > 0:
                    instantaneous_fps = fps_frames / elapsed_since_fps_update
                    cv2.putText(side_by_side, f"FPS: {instantaneous_fps:.1f}", 
                                (10, side_by_side.shape[0] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show the combined display
                cv2.imshow("Dual Thermal Cameras", side_by_side)
            
            # Check for user input (with minimal delay)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
            # Count frames for performance metrics
            frame_count += 1
            if frame_count % 100 == 0:
                print(f"Processed {frame_count} frames")
                print(f"Queue sizes: Camera 0: {frame_queue0.qsize()}, Camera 1: {frame_queue1.qsize()}")

    except KeyboardInterrupt:
        print("KeyboardInterrupt caught. Exiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Stop the camera threads
        stop_threads = True
        thread0.join(timeout=1.0)
        thread1.join(timeout=1.0)
        
        cv2.destroyAllWindows()
        print("Cameras closed.")

if __name__ == "__main__":
    open_cameras()