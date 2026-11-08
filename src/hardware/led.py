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


