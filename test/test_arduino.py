import serial
import time

arduino = serial.Serial(
    "/dev/cu.usbmodem11401",
    9600,
    timeout=1
)

time.sleep(2)

try:
    for category in range(4):
        print(f"Testing category {category}")

        arduino.write(f"{category}\n".encode())

        time.sleep(2)

    # Turn all LEDs off
    arduino.write(b"-1\n")
    time.sleep(1)

finally:
    arduino.close()