# Multispectral Imaging and Plant Height Measurement System

## Overview
This project focuses on a multispectral imaging and plant height measurement system using the Jetson Nano platform, integrated with a Parrot Sequoia Multispectral Camera and an Intel Realsense Depth Camera D435. The system is designed to capture and analyze multispectral data for agricultural applications, including measuring plant height and health.

## System Requirements
- **Platform**: Jetson Nano
- **Operating System**: Ubuntu 20.04 for Jetson Nano

To install Ubuntu 20.04 on your Jetson Nano, follow the tutorial provided [here](https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image).

## Installation Guide
### 1. Clone the Repository
To download all the necessary code, run the following command in your terminal:

```
git clone https://github.com/minhtu63/multispectral-plant-phenotyping.git
```
### 2. Install Libraries for Parrot Sequoia Multispectral Camera
The Parrot Sequoia requires some specific libraries to function correctly. You will need to install the ```PTPy``` library and ```gphoto2```. Follow these steps:

- Clone the ```PTPy``` library for Parrot Sequoia from [this link](https://github.com/Parrot-Developers/sequoia-ptpy/tree/master).
```
git clone https://github.com/Parrot-Developers/sequoia-ptpy.git
cd sequoia-ptpy
python3 setup.py install
```
- Install ```gphoto2``` by running the following command:
```
sudo apt-get install gphoto2
```