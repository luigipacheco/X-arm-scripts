__author__ = "Luis Pacheco"
__copyright__ = "Copyright 2023, Luis Pacheco"
__contributors__ = ""
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Luis Pacheco"
__email__ = "luigi@luigipacheco.com"
__status__ = "Alpha"
"""
This code sends an OSC message to draw on a neopixel matrix from adafruit
"""
import argparse
import random
import time

from pythonosc import udp_client

def get_square_coordinates(t):
    # Make the square bounce back and forth every 0.5 second
    base = int((t // 0.5) % 6)
    return [8 + base, 9 + base, 16 + base, 17 + base]

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="192.168.1.10",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=55555,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  start_time = time.time()

"""   while True:
    # initialize all pixels to off (black)
    pixel_data = []
    for x in range(32):
      pixel_data.extend([x, 0, 0, 0, 0])  # [LED number, R, G, B, W]

    # get current square coordinates
    square_coordinates = get_square_coordinates(time.time() - start_time)

    # set square pixels to white (or any color you want)
    for i in square_coordinates:
      pixel_data[5*i:5*i+5] = [i, 255, 255, 255, 0]  # [LED number, R, G, B, W]

    client.send_message("/draw", pixel_data)
    #pixel_data_fill = [255, 255, 0, 0]  # replace this with your actual pixel data
    #client.send_message("/fill", pixel_data_fill)
    #client.send_message("/clear", "clear")

    # wait before updating position
    time.sleep(0.1) """
pixel_data_fill = [0, 0, 0, 0]  # replace this with your actual pixel data
client.send_message("/fill", pixel_data_fill)