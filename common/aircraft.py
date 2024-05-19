from common import *
class Aircraft:
    def __init__(self, app):
        self.app = app
        self.image = pygame.image.load('images/aircraft.png')
        self.image = pygame.transform.scale(self.image, (100, 40))
        self.x = 100
        self.y = 300
        self.angle = self.speed = 0
        self.min_speed = 0.7
        self.max_speed = 5
        self.acceleration = self.deceleration = 0.02
        self.turn_speed = 0.5
        self.accelerate = self.brake = self.turn_left = self.turn_right = False

    def handle_events(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.accelerate = True
            elif event.key == pygame.K_DOWN:
                self.brake = True
            elif event.key == pygame.K_LEFT:
                self.turn_left = True
            elif event.key == pygame.K_RIGHT:
                self.turn_right = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                self.accelerate = False
            elif event.key == pygame.K_DOWN:
                self.brake = False
            elif event.key == pygame.K_LEFT:
                self.turn_left = False
            elif event.key == pygame.K_RIGHT:
                self.turn_right = False

    def __update_position(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        if self.x > SCREEN_WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = SCREEN_WIDTH

        if self.y > SCREEN_HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = SCREEN_HEIGHT

    def __update_velocity(self):
        if self.accelerate:
            self.speed += self.acceleration
        if self.brake:
            self.speed -= self.deceleration
        if self.turn_right:
            if self.angle < 25:
                self.angle += self.turn_speed
        if self.turn_left:
            if self.angle > -25:
                self.angle -= self.turn_speed

        self.speed = max(self.min_speed, min(self.max_speed, self.speed))

    def draw(self, screen):
        if self.app.simulation_started:
            self.__update_position()
            self.__update_velocity()
            rotated_image = pygame.transform.rotate(self.image, -self.angle)
            new_rect = rotated_image.get_rect(
                center=self.image.get_rect(midright=(self.x, self.y)).midright)
            screen.blit(rotated_image, new_rect.topleft)
