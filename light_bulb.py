class LightBulb:
    def __init__(self):
        self.is_on: bool = False
        self.brightness: float = 1.0

    def turn_on(self):
        self.is_on = True
        print("Light Bulb switched ON")

    def turn_off(self):
        self.is_on = False
        print("Light Bulb switched OFF")

    def set_brightness(self, value: float):
        self.brightness = value
        print(f"Light Bulb brightness set to {int(value * 100)}%")
