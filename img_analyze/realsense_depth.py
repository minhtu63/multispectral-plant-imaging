

import pyrealsense2 as rs
import numpy as np
import cv2

class DepthCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Enable depth and color streams
        self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        self.pipeline.start(self.config)

    def get_frame(self):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            return False, None, None

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Crop to a square (from center)
        crop_size = 480  # Square size
        depth_image = self.crop_center(depth_image, crop_size, crop_size)
        color_image = self.crop_center(color_image, crop_size, crop_size)

        return True, depth_image, color_image

    def get_closest_point(self, depth_image):
        # Filter depth_image for non-zero values (greater than 0)
        valid_depth = depth_image[depth_image > 0]
        if valid_depth.size == 0:
            return None, None

        # Find the closest point in the depth image within the square region
        min_depth_value = np.min(valid_depth)

        # Get the coordinates of the closest point
        min_depth_coords = np.unravel_index(np.argmin(depth_image), depth_image.shape)

        return min_depth_value, min_depth_coords

    def crop_center(self, img, cropx, cropy):
        """Crop the center of the image to the given size"""
        y, x = img.shape[:2]
        startx = x // 2 - (cropx // 2)
        starty = y // 2 - (cropy // 2)
        return img[starty:starty + cropy, startx:startx + cropx]

    def release(self):
        self.pipeline.stop()



