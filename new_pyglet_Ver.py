import pyglet
import random
import cv2
from kivy.config import Config


class ArUcoVerticalSimulation(pyglet.window.Window):
    def __init__(self, marker_id=0, marker_size=200, speed_x=3, speed_y=3):
        super(ArUcoVerticalSimulation, self).__init__(width=1920, height=1080)

        self.speed_x = speed_x
        self.speed_y = speed_y
        self.marker_size = marker_size

        # Generate the ArUco marker image
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, self.marker_size)

        # Ensure the marker is upright by flipping it
        marker_image = cv2.cvtColor(marker_image, cv2.COLOR_GRAY2RGB)
        marker_image = cv2.flip(marker_image, 0)

        # Create a pyglet image from the marker
        marker_data = marker_image.tobytes()
        marker_texture = pyglet.image.ImageData(self.marker_size, self.marker_size, 'RGB', marker_data)
        self.marker_sprite = pyglet.sprite.Sprite(marker_texture)

        # Set the initial position of the marker
        self.marker_sprite.x = random.randint(0, self.width - self.marker_sprite.width)
        self.marker_sprite.y = random.randint(0, self.height - self.marker_sprite.height)

        self.padding_left = 30
        self.padding_right = 50
        self.padding_top = 50
        self.padding_bottom = 30

        self.current_x = self.padding_left
        self.current_y = self.padding_top

        self.direction_x = 0
        self.direction_y = 1

        self.grid_size = 100  # Grid cell size
        self.horizontal_movement = 0
        self.completed = False

        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def update(self, dt):
        if self.completed:
            pyglet.app.exit()

        padded_left = self.padding_left
        padded_right = self.width - self.padding_right - self.marker_sprite.width
        padded_top = self.padding_top
        padded_bottom = self.height - self.padding_bottom - self.marker_sprite.height

        # Vertical movement logic
        if self.direction_y:
            self.current_y += self.speed_y * self.direction_y
            if self.current_y >= padded_bottom:
                self.current_y = padded_bottom
                self.direction_y = 0
                self.direction_x = 1
                self.horizontal_movement = 0
            elif self.current_y <= padded_top:
                self.current_y = padded_top
                self.direction_y = 0
                self.direction_x = 1
                self.horizontal_movement = 0

        # Horizontal movement logic
        elif self.direction_x:
            self.current_x += self.speed_x * self.direction_x
            self.horizontal_movement += self.speed_x * self.direction_x
            if self.horizontal_movement >= self.grid_size:
                self.current_x = min(max(self.current_x, padded_left), padded_right)
                self.direction_x = 0
                if self.direction_y == 0:
                    if self.current_y == padded_bottom:
                        self.direction_y = -1  # Move up
                    elif self.current_y == padded_top:
                        self.direction_y = 1  # Move down
                self.horizontal_movement = 0

        self.current_x = max(padded_left, min(self.current_x, padded_right))
        self.current_y = max(padded_top, min(self.current_y, padded_bottom))

        if self.current_x >= padded_right and self.current_y >= padded_bottom:
            self.completed = True
        elif self.current_x <= padded_left and self.current_y <= padded_top:
            self.completed = True

        # Update the marker position
        self.marker_sprite.x = self.current_x
        self.marker_sprite.y = self.current_y

    def on_draw(self):
        # Clear the screen with a white background
        self.clear()
        pyglet.gl.glClearColor(1, 1, 1, 1)  # Set background to white
        self.marker_sprite.draw()
        # Draw the red dot at the center of the marker
        center_x = self.current_x + self.marker_size // 2
        center_y = self.current_y + self.marker_size // 2
        pyglet.shapes.Circle(center_x, center_y, 10, color=(255, 0, 0)).draw()


if __name__ == '__main__':
    sim = ArUcoVerticalSimulation()
    Config.set('graphics', 'width', '1920')
    Config.set('graphics', 'height', '1080')
    Config.set('graphics', 'fullscreen', '0')  # Set to '1' for fullscreen
    Config.set('graphics', 'multisamples', '4')  # Anti-aliasing for smoother graphics
    Config.set('graphics', 'vsync', '1')  # Enable V-Sync for smoother animation
    pyglet.app.run()
