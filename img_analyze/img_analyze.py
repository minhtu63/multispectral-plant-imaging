import cv2 as cv
from glob import glob
import numpy as np
import pickle


class ImgAnalyze():
    def __init__(self, folder_path, homography_path_f, width=1280, height=960):
        images_name = glob(folder_path + '*.TIFrd') + glob(folder_path + '*.JPGrd')
        calibs_name = glob(homography_path_f + '*.pickle')
        if len(calibs_name) == 0:
            raise TypeError("Empty calibration folder")
        self.folder_path = folder_path
        self.RGB_f = False
        self.NIR_f = False
        self.REG_f = False
        self.GRE_f = False
        self.RED_f = False
        self.RGB_calib = False
        self.NIR_calib = False
        self.REG_calib = False
        self.GRE_calib = False
        self.RED_calib = False
        self.width = width
        self.height = height
        for calib in calibs_name:
            if 'RGB' in calib:
                self.RGB_calib = self.read_calib_homography(calib)
            elif 'NIR' in calib:
                self.NIR_calib = self.read_calib_homography(calib)
            elif 'REG' in calib:
                self.REG_calib = self.read_calib_homography(calib)
            elif 'GRE' in calib:
                self.GRE_calib = self.read_calib_homography(calib)
            elif 'RED' in calib:
                self.RED_calib = self.read_calib_homography(calib)

        for img in images_name:
            if 'RGB' in img:
                self.RGB = cv.imread(img, 1)
                self.RGB = cv.resize(
                    self.RGB, (self.width, self.height), interpolation=cv.INTER_AREA)
                if self.RGB_calib is not False:
                    self.RGB = cv.warpPerspective(
                        self.RGB, self.RGB_calib, (self.width, self.height))
                self.RGB = cv.rotate(self.RGB,
                                     cv.ROTATE_90_CLOCKWISE)
                self.RGB_f = True
            elif 'NIR' in img:
                self.NIR = cv.imread(img, 1)
                if self.NIR_calib is not False:
                    self.NIR = cv.warpPerspective(
                        self.NIR, self.NIR_calib, (self.width, self.height))
                self.NIR = cv.rotate(self.NIR,
                                     cv.ROTATE_90_CLOCKWISE)
                self.NIR_f = True
            elif 'REG' in img:
                self.REG = cv.imread(img, 1)
                if self.REG_calib is not False:
                    self.REG = cv.warpPerspective(
                        self.REG, self.REG_calib, (self.width, self.height))
                self.REG = cv.rotate(self.REG,
                                     cv.ROTATE_90_CLOCKWISE)
                self.REG_f = True
            elif 'GRE' in img:
                self.GRE = cv.imread(img, 1)
                if self.GRE_calib is not False:
                    self.GRE = cv.warpPerspective(
                        self.GRE, self.GRE_calib, (self.width, self.height))
                self.GRE = cv.rotate(self.GRE,
                                     cv.ROTATE_90_CLOCKWISE)
                self.GRE_f = True
            elif 'RED' in img:
                self.RED = cv.imread(img, 1)
                if self.RED_calib is not False:
                    self.RED = cv.warpPerspective(
                        self.RED, self.RED_calib, (self.width, self.height))
                self.RED = cv.rotate(self.RED,
                                     cv.ROTATE_90_CLOCKWISE)
                self.RED_f = True

    def read_calib_homography(self, homography_path):
        with (open(homography_path, "rb")) as openfile:
            while True:
                try:
                    homography = pickle.load(openfile)
                except EOFError:
                    break
        return homography

    def get_rgb(self, cmap=cv.COLORMAP_JET, savef=False):
        if savef:
            cv.imwrite(self.folder_path + 'RGB.jpg', self.RGB)
        return self.RGB

    def get_ndvi(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            index_image = (self.NIR.astype(float) - self.RED.astype(float)) / \
                          (self.NIR.astype(float) + self.RED.astype(float))
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            with open(self.folder_path + 'NDVI.pickle', 'wb') as f:
                pickle.dump(index_image, f)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'NDVI.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError('There is not RED or NIR images loaded'))

    def get_ndre(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            index_image = (self.NIR.astype(float) - self.REG.astype(float)) / \
                          (self.NIR.astype(float) + self.REG.astype(float))
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'NDRE.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError(
                'There is not RED or NIR images loaded'))

    def get_sr(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            index_image = self.NIR.astype(float) / (self.RED.astype(float))
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'SR.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError(
                'There is not RED or NIR images loaded'))

    def get_dvi(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            index_image = self.NIR.astype(float) - self.RED.astype(float)
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'DVI.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError(
                'There is not RED or NIR images loaded'))

    def get_gndvi(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            index_image = (self.NIR.astype(float) - self.GRE.astype(float)) / \
                          (self.NIR.astype(float) + self.GRE.astype(float))
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'GNDVI.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError(
                'There is not RED or NIR images loaded'))

    def get_savi(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            L = 0.5
            index_image = ((1 + L) * (self.NIR.astype(float) - self.RED.astype(float))) / \
                          (self.NIR.astype(float) + self.RED.astype(float) + 0.5)
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'SAVI.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError(
                'There is not RED or NIR images loaded'))

    def get_msavi(self, cmap=cv.COLORMAP_JET, savef=False):
        if self.NIR_f and self.RED_f:
            d_NIR = 2 * self.NIR.astype(float)
            index_image = (0.5) * (d_NIR + 1 - (d_NIR ** 2) ** 0.5 -
                                   (8 * (self.NIR.astype(float) - self.RED.astype(float))))
            index_image = index_image - index_image.min()  # Now between 0 and 8674
            index_image = index_image / index_image.max() * 255
            index_image = np.uint8(index_image)
            index_image = cv.applyColorMap(index_image, cmap)
            if savef:
                cv.imwrite(self.folder_path + 'MSAVI.jpg', index_image)
            return index_image
        else:
            raise Exception(ValueError(
                'There is not RED or NIR images loaded'))

    def get_nir(self):
        return cv.cvtColor(self.NIR, cv.COLOR_BGR2GRAY)

    def get_red(self):
        return cv.cvtColor(self.RED, cv.COLOR_BGR2GRAY)

    def get_gre(self):
        return cv.cvtColor(self.GRE, cv.COLOR_BGR2GRAY)

    def get_reg(self):
        return cv.cvtColor(self.REG, cv.COLOR_BGR2GRAY)

    @staticmethod
    def generate_VI_images(calib_path, imgs_folder_path):
        files = glob(f'{imgs_folder_path}/*/')
        print("calib", calib_path)
        if len(files) == 0:
            raise TypeError("Empty images directory")
        for fname in files:
            my_img_analyze = ImgAnalyze(fname, f"{calib_path}/")
            my_img_analyze.get_rgb(savef=True)
            my_img_analyze.get_sr(savef=True) # this idex some times has divisoin by zero
            my_img_analyze.get_dvi(savef=True)
            my_img_analyze.get_ndvi(savef=True)
            my_img_analyze.get_gndvi(savef=True)
            my_img_analyze.get_ndre(savef=True)
            my_img_analyze.get_savi(savef=True)
            my_img_analyze.get_msavi(savef=True)
            my_img_analyze.get_ndre(savef=True)

    @staticmethod
    def generate_RGB_image(calib_path, imgs_folder_path):
        print(imgs_folder_path)
        files = glob(f'{imgs_folder_path}/*/')
        print("calib", calib_path)
        if len(files) == 0:
            raise TypeError("Empty images directory")
        for fname in files:
            my_img_analyze = ImgAnalyze(fname, f"{calib_path}/")
            my_img_analyze.get_rgb(savef=True)

