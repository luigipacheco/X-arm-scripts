from pythonosc.udp_client import SimpleUDPClient
import time

# Set the IP address and port number for the OSC server (your Arduino device)
ip = "192.168.1.10"  # use your Arduino's IP here
port = 55555  # use your OSC server's port number

client = SimpleUDPClient(ip, port)  # create a client

# Define the size of your matrix
matrix_width = 8
matrix_height = 4

# Define the color of your pixel
pixel_color = [255, 0, 0, 0]  # Red

# Variables to track the pixel's position
x, y = 0, 0
# Variables to track the pixel's velocity
dx, dy = 1, 1

# Loop that causes a pixel to bounce around
while True:
    # Clear the matrix
    client.send_message("/clear", "clear")
    time.sleep(0.1)
    # Calculate the position of the pixel
    x += dx
    y += dy

    # Check for collisions with the edge of the matrix
    if x <= 0 or x >= matrix_width - 1:
        dx *= -1  # Reverse the x direction
    if y <= 0 or y >= matrix_height - 1:
        dy *= -1  # Reverse the y direction

    # Draw the pixel
    pixel_position = y * matrix_width + x  # Convert from 2D to 1D position
    pixel_data = [pixel_position] + pixel_color  # Combine pixel position and color into a single list
    client.send_message("/draw", pixel_data)

    # Wait
    time.sleep(0.1)