import pygame
import random
import cv2
import time

class ArUcoSimulation:
    def __init__(self, marker_id=0, marker_size=350, speed_x=1, speed_y=1):
        # Initialize Pygame
        pygame.init()

        # Create ArUco marker image
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
        cv2.imwrite("aruco_marker.png", marker_image)

        # Set window dimensions
        self.width, self.height = 3440, 1440  # High resolution

        # Set up Pygame display with hardware acceleration and double buffering
        self.window = pygame.display.set_mode(
            (self.width, self.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SRCALPHA
        )
        pygame.display.set_caption("ArUco Marker Simulation")

        # Load marker image into Pygame and optimize
        self.marker_image = pygame.image.load("aruco_marker.png").convert_alpha()
        self.marker_rect = self.marker_image.get_rect()
        self.marker_rect.topleft = (
            random.randint(0, self.width - self.marker_rect.width),
            random.randint(0, self.height - self.marker_rect.height)
        )

        # Movement speed
        self.speed_x = speed_x
        self.speed_y = speed_y

        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()

        # Padding from edges
        self.padding = 30

    def move_marker(self):
        # Update marker position
        self.marker_rect.x += self.speed_x
        self.marker_rect.y += self.speed_y

        # Bounce off the edges considering padding
        if self.marker_rect.left <= self.padding or self.marker_rect.right >= self.width - self.padding:
            self.speed_x = -self.speed_x
        if self.marker_rect.top <= self.padding or self.marker_rect.bottom >= self.height - self.padding:
            self.speed_y = -self.speed_y

    def run(self):
        running = True

        while running:
            self.clock.tick(30)  # Adjusted FPS for smoother performance

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False

            self.move_marker()

            # Clear the screen
            self.window.fill((255, 255, 255))

            # Draw marker and center red dot
            self.window.blit(self.marker_image, self.marker_rect)
            center_position = self.marker_rect.center
            pygame.draw.circle(self.window, (255, 0, 0), center_position, 10)

            # Update the display
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    simulation = ArUcoSimulation(speed_x=2, speed_y=2)  # Adjust speed values
    simulation.run()
