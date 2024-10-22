import time
import os
from img_analyze import ImgAnalyze
from gphoto_utils import GPhotoUtils
from drive_utils import DriveUtils
import sys
sys.path.append('/home/tu/.local/lib/python3.6/site-packages')
sys.path.append('/usr/local/lib/python3.6/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/lib/python3.6/dist-packages')
def main():
    
    #time.sleep(90)
    image_folder_path = "/home/tu/Documents/Thesis/src/Data/plant_data/plant_mult_data"
    upload_folder_path = "/home/tu/Documents/Thesis/src/Data/plant_data/"
    base_save_folder_path = "/home/tu/Documents/Thesis/src/Data/calib_result/"
    homography_folder_path = "/home/tu/Documents/Thesis/src/Data/calib_result/multispectral_image_registration/"

    # Step 1: Download images from camera (Code 1)
    gphoto = GPhotoUtils()
    gphoto.download_images(image_folder_path)

    # Step 2: Process images (Code 2)
    os.makedirs(base_save_folder_path, exist_ok=True)
    ImgAnalyze.generate_VI_images(homography_folder_path, image_folder_path)
    ImgAnalyze.generate_RGB_image(homography_folder_path, image_folder_path)

    # Step 3: Upload processed images to Google Drive (Code 3)
    drive = DriveUtils()
    drive.upload_folder(upload_folder_path)

if __name__ == "__main__":
    main()
'''
import cv2
import pyrealsense2
from realsense_depth import *
import numpy as np
import serial
import time
import ptpy
import os
import requests
import shutil
from img_analyze import ImgAnalyze
from gphoto_utils import GPhotoUtils
from drive_utils import DriveUtils

# Initialize Camera Intel Realsense
dc = DepthCamera()

# Create mouse event
cv2.namedWindow("Color frame")

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
    ret, depth_frame, color_frame = dc.get_frame()

    # Normalize the depth frame for color mapping
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_frame, alpha=0.03), cv2.COLORMAP_JET)

    # Calculate the nearest point and the result
    non_zero_depth = depth_frame[depth_frame > 0]
    if non_zero_depth.size > 0:
        min_distance = np.min(non_zero_depth)
        result = 660 - min_distance
        min_point = np.unravel_index(np.argmin(np.where(depth_frame == min_distance, min_distance, np.inf)), depth_frame.shape)
        cv2.putText(color_frame, "Result: {}mm".format(result), (30, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        if min_point:
            cv2.circle(color_frame, (min_point[1], min_point[0]), 10, (255, 0, 0), 2)
            cv2.putText(color_frame, "{}mm".format(min_distance), (min_point[1], min_point[0] - 20), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        print("Minimum distance greater than 0: {}mm at {}".format(min_distance, min_point))
        print("Result: {}mm".format(result))

    # Save images with the result
    save_image(color_frame, depth_colormap)

def save_image(color_frame, depth_colormap):
    folder_path = "/home/tu/Documents/Thesis/src/Data/plant_data/plant_height_data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Generate unique filenames based on the current time
    timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
    color_filename = os.path.join(folder_path, f"color_{timestamp}.png")

    # Save images
    cv2.imwrite(color_filename, color_frame)
    print(f"Saved color image to {color_filename}")

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
     [13, 20],
     [13, 50],
     [50, 50],
     [50, 20] 
]

def run_camera_operations():
    try:
        camera = ptpy.PTPy()
        send_coordinates(target_coordinates, camera)
    finally:
        # Send stop command to Arduino
        ser.write("STOP\n".encode())
        ser.close()
        print("Serial connection closed and STOP command sent.")
    # Release camera resources
    dc.release()
    cv2.destroyAllWindows()

def process_images():
    image_folder_path = "/home/tu/Documents/Thesis/src/Data/plant_data/plant_mult_data"
    upload_folder_path = "/home/tu/Documents/Thesis/src/Data/plant_data/"
    base_save_folder_path = "/home/tu/Documents/Thesis/src/Data/calib_result/"
    homography_folder_path = "/home/tu/Documents/Thesis/src/Data/calib_result/multispectral_image_registration/"

    # Step 1: Download images from camera (Code 1)
    gphoto = GPhotoUtils()
    gphoto.download_images(image_folder_path)

    # Step 2: Process images (Code 2)
    os.makedirs(base_save_folder_path, exist_ok=True)
    ImgAnalyze.generate_VI_images(homography_folder_path, image_folder_path)
    ImgAnalyze.generate_RGB_image(homography_folder_path, image_folder_path)

    # Step 3: Upload processed images to Google Drive (Code 3)
    drive = DriveUtils()
    drive.upload_folder(upload_folder_path)

if __name__ == "__main__":
    run_camera_operations()  # Run the first code to handle camera operations
    process_images()  # Run the second code to process and upload images
'''
