import serial
import time

# Define the coordinates
target_coordinates = [
    [25, 20],
    [25, 40],
    [25, 70],
    [50, 70],
    [50, 40],
    [50, 20],
    [50, 0]
]

# Set up the serial connection
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Thay '/dev/ttyUSB0' bằng cổng phù hợp trên máy tính của bạn
time.sleep(2)  # Wait for the connection to establish

def send_coordinates(coordinates):
    for coordinate in coordinates:
        x, y = coordinate
        command = f"{x},{y}\n"
        ser.write(command.encode())
        print(f"Sent: {command.strip()}")
        wait_for_capture()  # Wait for the capture command
        time.sleep(5)  # Wait for the Arduino to process the command

def wait_for_capture():
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response == "CAPTURE":
                print("Capture command received")
                break

try:
    send_coordinates(target_coordinates)
finally:
    # Send stop command to Arduino
    ser.write("STOP\n".encode())
    ser.close()
    print("Serial connection closed and STOP command sent.")
