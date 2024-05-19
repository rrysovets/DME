from common import *

class DMEStation:
    
    x = SCREEN_WIDTH//DIV
    y = SCREEN_HEIGHT//DIV
    

    def __init__(self):

        self.radius = 100
        self.track_mode = False
        self.search_mode = True
        self.color_track = (0, 0, 255)
        self.color_search = (0, 255, 0)
        self.color = self.color_search

        self.font = pygame.font.Font('fonts/dme_font.ttf', 40)

        self.beacon_calls = [pygame.mixer.Sound(
            f'mp3s/позывные/{i + 1}.mp3') for i in range(len(BEACONS))]

    def draw(self, screen, aircraft):

        if self.track_mode:
            color_DME = self.color_track

        else:
            color_DME = self.color_search

        left_point = (self.x - self.radius, self.y)
        right_point = (self.x + self.radius, self.y)
        top_point = (self.x, self.y*DIV)
        points = [left_point, right_point, top_point]

        diagram_surface = pygame.Surface(
            (self.x*DIV, self.y*DIV), pygame.SRCALPHA)
        diagram_surface.set_alpha(64)

        pygame.draw.polygon(diagram_surface, color_DME, points)
        pygame.draw.circle(diagram_surface, color_DME,
                           (self.x, self.y), self.radius, 1000)
        pixel_color = diagram_surface.get_at(
            (int(aircraft.x), int(aircraft.y)))
        if pixel_color == self.color:
            # Aircraft is inside diagram
            if self.search_mode:
                self.track_mode = True
                self.search_mode = False
                self.color = self.color_track
                
                if data.selected_beacon is not None:
                    self.beacon_calls[data.selected_beacon].play()
        else:
            # Aircraft is outside diagram
            if self.track_mode:
                self.track_mode = False
                self.search_mode = True
                self.color = self.color_search

        screen.blit(diagram_surface, (0, 0))

