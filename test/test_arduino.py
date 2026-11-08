import serial
import time

from src.hardware.led import LEDController

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


# Test program
if __name__ == "__main__":

    led = None

    try:
        led = LEDController(
            port="/dev/cu.usbmodem1401",
            baudrate=9600
        )

        # Test each LED
        led.set_category(0)  # Compost
        time.sleep(2)

        led.set_category(1)  # Recycling
        time.sleep(2)

        led.set_category(2)  # Paper
        time.sleep(2)

        led.set_category(3)  # Garbage
        time.sleep(2)

    except serial.SerialException as error:
        print(f"Arduino connection error: {error}")

    finally:
        if led is not None:
            led.close()