from common.dme import DMEStation
from common.pfd import PFDIndicator
from common.aircraft import Aircraft
from common.menu import Menu
from common import *


class App:
    def __init__(self):
        self.a = 0, 0
        self.flag = False  # dogshit+boolshit parameters
        pygame.init()
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height))
        pygame.display.set_caption("DME Simulator")
        self.dme_image = pygame.image.load('images/dme_panel.png')
        icon = pygame.image.load('images/icon.png')
        self.clock = pygame.time.Clock()
        pygame.display.set_icon(icon)
        self.dme_station = DMEStation()
        self.aircraft = Aircraft(self)
        self.pfd_indicator = PFDIndicator(self)
        self.menu = Menu(self.screen, self)

    def boolshit(self, a):
        """вспомогательные штуки"""
        self.font = pygame.font.Font(None, 24)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = f"({mouse_x}, {mouse_y})"
        mouse_text_render = self.font.render(mouse_text, True, (255, 255, 255))
        self.screen.blit(mouse_text_render, (mouse_x + 10, mouse_y))
        angle_text = f"Angle: {self.aircraft.angle:.2f}"
        angle_text_render = self.font.render(angle_text, True, (255, 255, 255))
        self.screen.blit(angle_text_render, (10, 10))
        if a:
            pygame.draw.rect(self.screen, (0, 0, 0, 225), a)

    def dogshit(self, event):

        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:

            self.a = (self.mouse_x, self.mouse_y)
            self.flag = True

        if event.type == pygame.MOUSEMOTION and self.flag:

            return self.a, (abs(self.a[0]-self.mouse_x), abs(self.a[1]-self.mouse_y))

        elif event.type == pygame.MOUSEBUTTONUP:
            print((self.a, (abs(self.a[0]-self.mouse_x),
                  abs(self.a[1]-self.mouse_y))), end=',\n')
            self.flag = False
            return self.a, (abs(self.a[0]-self.mouse_x), abs(self.a[1]-self.mouse_y))

    def handle_events(self):
        for event in pygame.event.get():
            self.aircraft.handle_events(event)
            self.menu.handle_events(event)
            # self.coords=(0,0,0,0)
            # self.coords=self.dogshit(event)

    def draw(self):
        
        self.background_image = pygame.image.load('images/airport.png')
        self.background_image = pygame.transform.scale(
            self.background_image, (self.screen_width, self.screen_height))
        self.screen.blit(self.background_image, (0, 0))
        self.dme_station.draw(self.screen, self.aircraft)
        self.pfd_indicator.draw(self.screen, self.aircraft)
        
        self.aircraft.draw(self.screen)
        self.menu.draw()
        # self.boolshit(self.coords)  # угол, координаты

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)


app = App()
app.run()
