import serial
import time


class LEDController:

    CATEGORIES = {
        0: "Compost",
        1: "Recycling",
        2: "Paper",
        3: "Garbage"
    }

    def __init__(self, port="/dev/cu.usbmodem1101", baudrate=9600):

        self.arduino = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=1
        )

        # Wait for Arduino to initialize
        time.sleep(2)

        print("Arduino connected!")

    def set_category(self, category):

        if category not in self.CATEGORIES:
            print("Invalid category")
            return

        # Send category number to Arduino
        message = f"{category}\n"
        self.arduino.write(message.encode("utf-8"))

        print(f"LED activated: {self.CATEGORIES[category]}")

    def close(self):
        if self.arduino.is_open:
            self.arduino.close()
            print("Arduino disconnected!")


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