
import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Start streaming with default recommended settings
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start the pipeline
pipeline.start(config)

try:
    while True:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Filter depth_image for non-zero values (greater than 0)
        valid_depth = depth_image[depth_image > 0]

        if valid_depth.size == 0:
            print("No valid depth data found")
            continue

        # Find the closest point in the depth image
        min_depth_value = np.min(valid_depth)

        # Get the coordinates of the closest point
        min_depth_coords = np.unravel_index(np.argmin(depth_image), depth_image.shape)

        # Draw a circle on the closest point
        cv2.circle(color_image, (min_depth_coords[1], min_depth_coords[0]), 10, (0, 255, 0), 2)

        # Display the images
        cv2.imshow('Color Image', color_image)
        cv2.imshow('Depth Image', depth_image)

        print(f'Closest point is at {min_depth_coords} with depth {min_depth_value}')

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Stop streaming
    pipeline.stop()
    cv2.destroyAllWindows()
