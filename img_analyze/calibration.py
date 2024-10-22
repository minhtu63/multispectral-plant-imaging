import os
import cv2 as cv
import numpy as np
import pickle
import matplotlib.pyplot as plt
from glob import glob

width = 1280
height = 960


def image_registration(image_folder_path, base_save_folder_path):
    dim = (width, height)
    plot_flag = False
    save_folder_path = os.path.join(base_save_folder_path, "multispectral_image_registration")
    base_images_folder_path = image_folder_path + "/"
    base_save_folder_images = os.path.join(save_folder_path, "result_images")
    os.makedirs(base_save_folder_images, exist_ok=True)

    folders = glob(base_images_folder_path + '*/')

    k_points = {}
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    for folder in folders:
        print(f"Processing folder: {folder}")
        images_name = glob(folder + '*.TIF') + glob(folder + '*.JPG')
        if not images_name:
            print(f"No images found in {folder}")
            continue

        kp_prev = {}
        c_bnd = True

        plt_images = {}
        for fname in images_name:
            print(f"Processing file: {fname}")
            img = cv.imread(fname)
            if fname.split('.')[-1].upper() == 'JPG':
                img = cv.resize(img, dim, interpolation=cv.INTER_AREA)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, (7, 4), None)

            if ret:
                corners2 = cv.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1), criteria)
                # Draw and display the corners
                cv.drawChessboardCorners(img, (7, 4), corners2, ret)
                file_name_s = os.path.basename(fname)
                save_path = os.path.join(base_save_folder_images, file_name_s)
                cv.imwrite(save_path, img)
                print(f"Saved: {save_path}")
                corners = corners.reshape(corners.shape[0], 2)
                band = fname.split('_')[-1].split('.')[0]
                plt_images[band] = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
                if band in kp_prev:
                    kp_prev[band] = np.concatenate(
                        (corners, kp_prev[band]), axis=0)
                else:
                    kp_prev[band] = corners
            else:
                c_bnd = False
                print(f"No corners found in {fname}")
                break
        if plot_flag and plt_images:
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4)
            fig.suptitle("Multispectral camera registration", fontsize=16)
            if 'RED' in plt_images: ax1.imshow(plt_images['RED'])
            ax1.set_title('RED Band')
            ax1.set_yticklabels([])
            ax1.set_xticklabels([])
            if 'GRE' in plt_images: ax2.imshow(plt_images['GRE'])
            ax2.set_title('Green Band')
            ax2.set_yticklabels([])
            ax2.set_xticklabels([])
            if 'NIR' in plt_images: ax3.imshow(plt_images['NIR'])
            ax3.set_title('NIR Band')
            ax3.set_yticklabels([])
            ax3.set_xticklabels([])
            if 'REG' in plt_images: ax4.imshow(plt_images['REG'])
            ax4.set_title('RED EDGE Band')
            ax4.set_yticklabels([])
            ax4.set_xticklabels([])
            plt.show()

        for band, points in kp_prev.items():
            if band in k_points:
                k_points[band] = np.concatenate(
                    (points, k_points[band]), axis=0)
            else:
                k_points[band] = points

    if not k_points:
        print("No keypoints found in any images.")
        return

    m_band = 'NIR'
    points2match = k_points[m_band]
    for band, points in k_points.items():
        homography, mask = cv.findHomography(points, points2match, cv.RANSAC)
        pickle_out_path = os.path.join(save_folder_path, f"{band}_CALIB.pickle")
        with open(pickle_out_path, "wb") as pickle_out:
            pickle.dump(homography, pickle_out)
        print(f"Saved homography for {band} band at {pickle_out_path}")


# Main script to call the function
if __name__ == "__main__":
    image_folder_path = "/home/tu/Documents/Thesis/src/Data/calib_data/multispectral_image_registration"
    base_save_folder_path = "+"

    image_registration(image_folder_path, base_save_folder_path)

