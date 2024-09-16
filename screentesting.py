import time
from displayhatmini import DisplayHATMini

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("""This example requires PIL/Pillow, try:

sudo apt install python3-pil

""")
width = DisplayHATMini.WIDTH
height = DisplayHATMini.HEIGHT
buffer = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(buffer)
font = ImageFont.load_default()

displayhatmini = DisplayHATMini(buffer, backlight_pwm=True)
displayhatmini.set_led(0.05, 0.05, 0.05)

brightness = 1.0

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkred = (175,0,0)
darkgreen = (0,175,0)
darkblue = (0,0,175)

# Plumbing to convert Display HAT Mini button presses into pygame events
draw.rectangle((0, 0, width, height), black)
draw.text((10, 70), "Backlight Up", font=font, fill=white)
draw.text((10, 160), "Backlight Down", font=font, fill=white)


displayhatmini.display()
displayhatmini.set_backlight(brightness)
