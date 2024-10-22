
import sys
import cv2
import os
import time
import numpy as np
import serial
import ptpy
import pyrealsense2 as rs
from realsense_depth import DepthCamera

# Initialize Camera Intel Realsense
dc = DepthCamera()

# Align the depth frame to the color frame
align_to = rs.stream.color
align = rs.align(align_to)

min_distance = None
min_point = None

def send_coordinates(coordinates, camera):
    for coordinate in coordinates:
        x, y = coordinate
        command = f"{x},{y}\n"
        ser.write(command.encode())
        print(f"Sent: {command.strip()}")
        wait_for_capture(camera)  # Wait for the capture command
        time.sleep(5)  # Wait for the Arduino to process the command

    # After completing all coordinates, return to origin
    return_to_origin()

def wait_for_capture(camera):
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response == "CAPTURE":
                capture_image(camera)
                break

def capture_image(camera):
    try:
        with camera.session():
            capture = camera.initiate_capture()
        print("Multispectral Image captured")
        capture_depth_image()
        print("Depth captured")
    except Exception as e:
        print(f"Failed to capture image: {e}")

def capture_depth_image():
    # Retrieve frames and align them
    frames = dc.pipeline.wait_for_frames()
    aligned_frames = align.process(frames)

    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()

    if not depth_frame or not color_frame:
        print("Failed to get frames from camera.")
        return

    # Convert frames to numpy arrays
    depth_image = np.asanyarray(depth_frame.get_data())
    color_image = np.asanyarray(color_frame.get_data())

    # Get the closest point using the method from depth_utils
    ret, depth_image, color_image = dc.get_frame()  # Now getting the cropped square frame

    min_distance, _ = dc.get_closest_point(depth_image)

    if min_distance is not None:
        # Calculate the result as per your requirement
        result = 610 - min_distance
        cv2.putText(color_image, "Plant Result: {}mm".format(result), (30, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        print("Minimum distance greater than 0: {}mm".format(min_distance))
        print("Result: {}mm".format(result))

    # Normalize the depth frame for color mapping
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

    # Save images with the result
    save_image(color_image, depth_colormap)

def save_image(color_frame, depth_colormap):
    folder_path = "/home/tu/Documents/Thesis/src/Data/plant_data/plant_height_data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Generate unique filenames based on the current time
    timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
    color_filename = os.path.join(folder_path, f"color_{timestamp}.png")
    depth_filename = os.path.join(folder_path, f"depth_{timestamp}.png")

    # Save images
    cv2.imwrite(color_filename, color_frame)
    cv2.imwrite(depth_filename, depth_colormap)
    print(f"Saved color image to {color_filename}")
    print(f"Saved depth image to {depth_filename}")

def return_to_origin():
    command = "0,0\n"
    ser.write(command.encode())
    print("Returning to origin")
    wait_for_capture(None)  # No need to capture image when returning to origin
    time.sleep(5)  # Wait for the Arduino to process the command

# Set up the serial connection
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust the port as needed
time.sleep(2)  # Wait for the connection to establish

# Define the coordinates
target_coordinates = [
     [9, 13],
     [9, 43],
     [38, 43],
     [38, 13] 
]

try:
    camera = ptpy.PTPy()
    send_coordinates(target_coordinates, camera)
finally:
    # Send stop command to Arduino
    ser.write("STOP\n".encode())
    ser.close()
    print("Serial connection closed and STOP command sent.")

# Release the RealSense camera
dc.release()
cv2.destroyAllWindows()
