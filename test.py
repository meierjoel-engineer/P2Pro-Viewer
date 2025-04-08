import wmi
import cv2
import numpy as np
import re

def find_thermal_cameras():
    """Find thermal cameras using WMI and match them to specific device paths"""
    c = wmi.WMI()
    
    # Query for USB devices
    usb_devices = c.Win32_USBControllerDevice()
    
    # Look for devices that match our cameras
    thermal_cameras = []
    
    for device in usb_devices:
        dependent = device.Dependent
        if dependent:
            device_id = dependent.DeviceID
            
            # Check if device is our thermal camera (VID_0BDA and PID_5840)
            if "VID_0BDA" in device_id and "PID_5840" in device_id:
                # This is our thermal camera - now determine which one
                camera_info = {"id": device_id}
                
                # Extract serial or port identifier to distinguish cameras
                if "200901010001" in device_id:
                    camera_info["identifier"] = "camera1"
                    camera_info["description"] = "First Camera (Serial: 200901010001)"
                elif "5&13A74B18&0&11" in device_id:
                    camera_info["identifier"] = "camera2"
                    camera_info["description"] = "Second Camera (Port: 11/0B)"
                else:
                    # If we find another camera with the same VID/PID but different identifiers
                    camera_info["identifier"] = "unknown"
                    camera_info["description"] = "Unknown Camera"
                
                # Only add devices that represent the main USB interface, not child interfaces
                if not "MI_" in device_id:
                    thermal_cameras.append(camera_info)
    
    return thermal_cameras

def main():
    # Find thermal cameras
    print("Searching for thermal cameras...")
    cameras = find_thermal_cameras()
    
    print(f"\nFound {len(cameras)} thermal cameras:")
    for i, cam in enumerate(cameras):
        print(f"Camera {i+1}: {cam['description']}")
        print(f"  Device ID: {cam['id']}")
    
    # Create camera-to-index mapping
    # This maps our camera identifiers to OpenCV camera indices
    camera_to_index = {}
    
    if len(cameras) >= 2:
        # We need to figure out which camera corresponds to which index
        # This mapping might need to be adjusted based on testing
        camera_to_index = {
            "camera1": 0,  # Assuming the first camera is index 0
            "camera2": 1   # And the second camera is index 1
        }
        
        print(f"\nCamera mapping:")
        print(f"  {cameras[0]['description']} -> OpenCV index {camera_to_index[cameras[0]['identifier']]}")
        print(f"  {cameras[1]['description']} -> OpenCV index {camera_to_index[cameras[1]['identifier']]}")
    
    # Now try to open the cameras using OpenCV
    print("\nOpening camera feeds...")
    cap0 = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap1 = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    
    if not cap0.isOpened() or not cap1.isOpened():
        print("Failed to open one or both cameras")
        return
    
    # Display some frames to verify
    try:
        for i in range(10):
            ret0, frame0 = cap0.read()
            ret1, frame1 = cap1.read()
            
            if not ret0 or not ret1:
                print("Failed to read frames")
                break
            
            # Add camera identifiers to the frames
            height0, width0 = frame0.shape[:2]
            height1, width1 = frame1.shape[:2]
            
            # Add labels
            cv2.putText(frame0, "Camera 0", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame1, "Camera 1", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the top half of each frame (more meaningful for thermal)
            top_half0 = frame0[:height0//2, :]
            top_half1 = frame1[:height1//2, :]
            
            cv2.imshow("Camera 0", top_half0)
            cv2.imshow("Camera 1", top_half1)
            
            key = cv2.waitKey(100)
            if key & 0xFF == ord('q'):
                break
    
    finally:
        cap0.release()
        cap1.release()
        cv2.destroyAllWindows()
        print("Camera test completed")

if __name__ == "__main__":
    main()