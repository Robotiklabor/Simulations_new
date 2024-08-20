from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
import cv2
import random
from kivy.config import Config

class ArUcoSimulation(Widget):
    def __init__(self, **kwargs):
        super(ArUcoSimulation, self).__init__(**kwargs)
        self.width, self.height = 1920, 1080
        self.marker_size = 200
        self.speed_x = 1
        self.speed_y = 1
        self.padding = 40
        self.x = random.randint(0, self.width - self.marker_size)
        self.y = random.randint(0, self.height - self.marker_size)

        # Generate ArUco marker and convert it to a texture
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, 0, self.marker_size)

        # Ensure the marker is upright (no rotation or flipping)
        marker_image = cv2.cvtColor(marker_image, cv2.COLOR_GRAY2RGB)
        marker_image = cv2.flip(marker_image, 0)  # Flip vertically to correct orientation
        buf = marker_image.tobytes()
        texture = Texture.create(size=(self.marker_size, self.marker_size), colorfmt='rgb')
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

        with self.canvas:
            Color(1, 1, 1)  # Set background color to white
            self.rect_background = Rectangle(pos=(0, 0), size=(self.width, self.height))

            self.marker = Rectangle(texture=texture, pos=(self.x, self.y), size=(self.marker_size, self.marker_size))
            Color(1, 0, 0)  # Set dot color to red
            self.dot_size = 20
            self.dot = Ellipse(pos=self.calculate_dot_position(), size=(self.dot_size, self.dot_size))

        Clock.schedule_interval(self.update, 1.0 / 60)

    def calculate_dot_position(self):
        """ Calculate the position of the dot to ensure it is centered on the marker """
        return (self.x + self.marker_size // 2 - self.dot_size // 2,
                self.y + self.marker_size // 2 - self.dot_size // 2)
    def update(self, dt):
        # Update position
        self.x += self.speed_x
        self.y += self.speed_y

        # Check for bouncing off edges
        if self.x <= self.padding or self.x + self.marker_size >= self.width - self.padding:
            self.speed_x = -self.speed_x
        if self.y <= self.padding or self.y + self.marker_size >= self.height - self.padding:
            self.speed_y = -self.speed_y

        # Update marker and dot position
        self.marker.pos = (self.x, self.y)
        self.dot.pos = self.calculate_dot_position()

class ArUcoApp(App):
    def build(self):
        return ArUcoSimulation()

if __name__ == '__main__':
    Config.set('graphics', 'width', '1920')
    Config.set('graphics', 'height', '1080')
    Config.set('graphics', 'fullscreen', '0')  # Set to '1' for fullscreen
    Config.set('graphics', 'multisamples', '4')  # Anti-aliasing for smoother graphics
    Config.set('graphics', 'vsync', '1')  # Enable V-Sync for smoother animation
    # Config.set('graphics', 'borderless', '1')  # Remove window borders if in fullscreen
    ArUcoApp().run()
