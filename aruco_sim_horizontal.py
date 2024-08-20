import pygame
import random
import cv2
import socket
import time


class ArUcoSimulation:
    def __init__(self, marker_id=0, marker_size=300, speed_x=30, speed_y=30):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.marker_image = cv2.aruco.generateImageMarker(self.aruco_dict, marker_id, marker_size)
        cv2.imwrite("ArucoMarker/aruco_marker.png", self.marker_image)

        self.speed_x = speed_x
        self.speed_y = speed_y
        self.paused = False
        self.display = pygame.display
        self.draw = pygame.draw
        self.pygame = pygame
        self.pygame.init()
        display_info = self.pygame.display.Info()
        self.width, self.height = 3440, 1400
        self.window = self.pygame.display.set_mode((self.width, self.height))
        self.pygame.display.set_caption("ArUco Marker Simulation")

        self.marker_image = self.pygame.image.load("ArucoMarker/aruco_marker.png")
        self.marker_rect = self.marker_image.get_rect()
        self.marker_rect.topleft = (random.randint(0, self.width - self.marker_rect.width),
                                    random.randint(0, self.height - self.marker_rect.height))

        self.clock = self.pygame.time.Clock()

        # Ripple effect variables (now used for color change)
        self.ripple_active = False
        self.ripple_start_time = 0
        self.ripple_duration = 1  # seconds
        self.ripple_interval = 3  # seconds between ripples
        self.next_ripple_time = time.time() + self.ripple_interval

        self.ripple_count = 0
        self.user_looking_at_screen = False

        # Countdown variables
        self.countdown_start_time = time.time()
        self.countdown_duration = 3  # seconds
        self.countdown_active = True
        self.delay_after_countdown = 3  # seconds
        self.delay_start_time = None

        # Define padding constants
        self.padding_top = 50
        self.padding_bottom = 30
        self.padding_left = 30
        self.padding_right = 30

        # Flag to control main loop
        self.running = True
        self.client_socket = None

        # Initialize the grid parameters
        self.grid_size = 100  # Size of each grid cell (adjust as needed)
        self.current_x = self.padding_left
        self.current_y = self.padding_top
        self.direction_x = 1  # Start moving right
        self.direction_y = 0  # No vertical movement initially

        # Flag to indicate if the marker has completed its path
        self.completed = False
        self.vertical_movement = 0  # Counter to track vertical movement

    def connect_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', 65432))

    def send_message(self, message):
        try:
            if not self.client_socket:
                self.connect_socket()
            self.client_socket.sendall(message.encode())
        except Exception as e:
            print(f"Failed to send message: {e}")

    def close_socket(self):
        try:
            if self.client_socket:
                self.client_socket.close()
        except Exception as e:
            print(f"Failed to close socket: {e}")

    def move_marker(self):
        # Calculate padded boundaries
        padded_left = self.padding_left
        padded_right = self.width - self.padding_right - self.marker_rect.width
        padded_top = self.padding_top
        padded_bottom = self.height - self.padding_bottom - self.marker_rect.height

        # Move marker horizontally
        if self.direction_x:
            self.current_x += self.speed_x * self.direction_x
            self.vertical_movement += self.speed_y * self.direction_y
            if self.current_x >= padded_right:
                self.current_x = padded_right
                self.direction_x = 0  # Stop horizontal movement
                self.direction_y = 1  # Start vertical movement down
                self.vertical_movement = 0  # Reset vertical movement counter
            elif self.current_x <= padded_left:
                self.current_x = padded_left
                self.direction_x = 0  # Stop horizontal movement
                self.direction_y = 1  # Start vertical movement down
                self.vertical_movement = 0  # Reset vertical movement counter

        # Move marker vertically
        elif self.direction_y:
            self.current_y += self.speed_y * self.direction_y
            self.vertical_movement += self.speed_y * self.direction_y
            if self.vertical_movement >= self.grid_size:  # Move only a little bit vertically
                self.current_y = min(max(self.current_y, padded_top), padded_bottom)
                self.direction_y = 0  # Stop vertical movement
                # Determine next horizontal direction based on current position
                if self.direction_x == 0:
                    if self.current_x == padded_right:
                        self.direction_x = -1  # Move left
                    elif self.current_x == padded_left:
                        self.direction_x = 1  # Move right
                self.vertical_movement = 0  # Reset vertical movement counter

        # Ensure the marker remains within bounds
        self.current_x = max(padded_left, min(self.current_x, padded_right))
        self.current_y = max(padded_top, min(self.current_y, padded_bottom))

        # Check completion of the path
        if self.current_x >= padded_right and self.current_y >= padded_bottom:
            self.completed = True
        elif self.current_x <= padded_left and self.current_y <= padded_top:
            self.completed = True

        # Update marker position
        self.marker_rect.topleft = (self.current_x, self.current_y)

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def draw_color_change(self):
        elapsed_time = time.time() - self.ripple_start_time
        if elapsed_time > self.ripple_duration:
            self.ripple_active = False
            self.log_ripple_event()
            return
        alpha = max(0, 255 - int((elapsed_time / self.ripple_duration) * 255))
        # Choose the ripple color (e.g., green)
        ripple_color = (0, 255, 0)  # Change color to green
        center_x = self.marker_rect.centerx
        center_y = self.marker_rect.centery
        self.draw.circle(self.window, ripple_color, (center_x, center_y), 10)  # Draw the colored dot

    def log_ripple_event(self):
        self.ripple_count += 1
        status = "LOOKING" if self.user_looking_at_screen else "NOT LOOKING"
        print(f"Ripple {self.ripple_count}: User is {status}")
        # self.send_message(f"User is {status}")
        self.user_looking_at_screen = False

    def handle_key_press(self, key):
        if key == self.pygame.K_q:
            print("Q key pressed")
            # Handle Q key action

        elif key == self.pygame.K_w:
            print("W key pressed")
            # Handle W key action

        elif key == self.pygame.K_e:
            print("E key pressed")
            # Handle E key action

    def handle_mouse_button_down(self, button):
        if button == self.pygame.BUTTON_LEFT:
            if self.ripple_active:
                self.user_looking_at_screen = True

        elif button == self.pygame.BUTTON_RIGHT:
            self.running = False  # Stop the main loop
            pygame.quit()  # Quit pygame

    def run(self):
        running = True
        recording_active = True

        while running:
            current_time = time.time()

            # Check if countdown is active
            if self.countdown_active:
                elapsed_time = current_time - self.countdown_start_time
                countdown_time_left = self.countdown_duration - int(elapsed_time)
                if countdown_time_left <= 0:
                    self.countdown_active = False
                    self.delay_start_time = current_time
                    print("Recording has started")

            # Handle delay after countdown
            if not self.countdown_active and self.delay_start_time:
                if current_time - self.delay_start_time < self.delay_after_countdown:
                    delay_time_left = self.delay_after_countdown - (current_time - self.delay_start_time)
                    font = self.pygame.font.SysFont(None, 50)
                    text = font.render(f"Starting in {int(delay_time_left)} seconds...", True, (0, 0, 0))
                    text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
                    self.window.blit(text, text_rect)
                else:
                    self.delay_start_time = None  # Clear delay start time to indicate delay is over

            if not self.countdown_active and not self.delay_start_time:
                if current_time > self.next_ripple_time:
                    self.ripple_active = True
                    self.ripple_start_time = current_time
                    self.next_ripple_time = current_time + self.ripple_interval

            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    running = False
                elif event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_ESCAPE:
                        running = False

                    elif event.key in [self.pygame.K_q, self.pygame.K_w, self.pygame.K_e]:
                        self.handle_key_press(event.key)
                    elif event.key == self.pygame.K_SPACE:
                        if self.paused:
                            self.resume()
                        else:
                            self.pause()

                elif event.type == self.pygame.MOUSEBUTTONDOWN:
                    if recording_active:
                        self.handle_mouse_button_down(event.button)

                    elif event.button == self.pygame.BUTTON_MIDDLE:
                        print("Middle mouse button pressed")
                    elif event.button == self.pygame.BUTTON_RIGHT:
                        self.pygame.quit()  # Quit pygame
                        exit()  # Exit the program

            if recording_active and not self.paused:
                self.move_marker()
                if self.completed:
                    print("Marker has completed its path. Exiting...")
                    time.sleep(5)  # Pause for 5 seconds
                    running = False  # Exit the main loop

            self.window.fill((255, 255, 255))
            self.window.blit(self.marker_image, self.marker_rect.topleft)
            center_x = self.marker_rect.centerx
            center_y = self.marker_rect.centery
            self.draw.circle(self.window, (255, 0, 0), (center_x, center_y), 10)

            if self.ripple_active:
                self.draw_color_change()

            if self.paused:
                font = self.pygame.font.SysFont(None, 50)
                text = font.render("Paused - Press 'Space' to Resume", True, (255, 0, 0))
                text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 500))
                self.window.blit(text, text_rect)

            if self.countdown_active:
                font = self.pygame.font.SysFont(None, 100)
                text = font.render(f"Recording starts in {countdown_time_left}", True, (0, 0, 0))
                text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
                self.window.blit(text, text_rect)

            self.display.flip()
            self.clock.tick(30)

        self.pygame.quit()


sim = ArUcoSimulation()
sim.run()
