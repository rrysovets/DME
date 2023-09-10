import pygame
import math
from pygame import mixer
import pygame_gui



class DMEStation:

    def __init__(self, x, y):
        self.div=2
        self.x = x//self.div
        self.y = y//self.div
        self.radius = 100
        self.track_mode = False
        self.search_mode = True
        self.color_track = (0, 0, 255)
        self.color_search = (0, 255, 0)
        self.color = self.color_search
        self.dme_image = pygame.image.load('images/dme_panel.png')
        self.font = pygame.font.Font('fonts/dme_font.ttf', 40)
        self.beacons = [
            (500, 380),
            (700, 400),
            (300, 480),
            (750, 620),
        ]
        self.frequencies_bands = [
            108.1,
            108.8,
            108.3,
            108.4
        ]
        
        self.selected_beacon = 1 
        self.beacon_calls = [mixer.Sound(f'mp3s/позывные/{i + 1}.mp3') for i in range(len(self.beacons))]

    def draw(self, screen, aircraft):
        # Draw DME panel
        dme_panel_pos = (0, 0)
        screen.blit(self.dme_image, dme_panel_pos)

        # Draw frequency
        if self.selected_beacon is not None:
            frequency = self.frequencies_bands[self.selected_beacon]
            text_frequency = self.font.render(f"{frequency} MHz", True, (255, 0, 0))
            text_rect_frequency = text_frequency.get_rect(center=(240, 40))
            screen.blit(text_frequency, text_rect_frequency)

        # Draw distance
        if self.track_mode:
            color_DME=self.color_track
            dist=f"{self.calculate_distance(aircraft):.2f}"
        else:
            color_DME=self.color_search
            dist="00.00"
        text = self.font.render(dist, True, (255, 0, 0))
        text_rect = text.get_rect(center=(65, 40))
        screen.blit(text, text_rect)

        left_point = (self.x - self.radius, self.y);right_point = (self.x + self.radius, self.y);top_point = (self.x,self.y*self.div)
        points = [left_point, right_point, top_point]

        diagram_surface = pygame.Surface((self.x*self.div, self.y*self.div), pygame.SRCALPHA)
        diagram_surface.set_alpha(64)

        pygame.draw.polygon(diagram_surface, color_DME, points)
        pygame.draw.circle(diagram_surface, color_DME, (self.x, self.y), self.radius, 1000)
        pixel_color = diagram_surface.get_at((int(aircraft.x), int(aircraft.y)))
        if pixel_color == self.color:
            # Aircraft is inside diagram
            if self.search_mode:
                self.track_mode = True
                self.search_mode = False
                self.color = self.color_track
                if self.selected_beacon is not None:
                    self.beacon_calls[self.selected_beacon].play()
        else:
            # Aircraft is outside diagram
            if self.track_mode:
                self.track_mode = False
                self.search_mode = True
                self.color = self.color_search

        screen.blit(diagram_surface, (0, 0))

    def calculate_distance(self, aircraft):
        distance = math.sqrt((aircraft.x - self.x) ** 2 + (aircraft.y - 600) ** 2)
        return distance


class DDRMIIndicator:
    def __init__(self, x, y, dme_station):
        self.dme_station = dme_station
        self.x = x
        self.y = y
        self.state = 0  # Добавляем состояние тумблера

        self.ddrmi_image = self.load_image('images/DDRMI/DDRMI_indicator.png', 200, 200)
        self.ddrmi_tumbler_L = self.load_image('images/DDRMI/DDRMI_tumbler_L.png', 30, 35)
        self.ddrmi_tumbler_R = self.load_image('images/DDRMI/DDRMI_tumbler_R.png', 30, 35)

        # Создаем прямоугольники для обработки кликов мыши
        self.rect_L = self.ddrmi_tumbler_L.get_rect(topleft=(self.x + 20, self.y + 150))
        self.rect_R = self.ddrmi_tumbler_R.get_rect(topleft=(self.x + 160, self.y + 150))

        self.ddrmi_font = pygame.font.Font('fonts/dme_font.ttf', 22)

    def load_image(self, path, width, height):
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect_L.collidepoint(event.pos):
                if self.state == 0:
                    self.ddrmi_tumbler_L = pygame.transform.rotate(self.ddrmi_tumbler_L, -90)
                    self.state = 1
                else:
                    self.ddrmi_tumbler_L = pygame.transform.rotate(self.ddrmi_tumbler_L, 90)
                    self.state = 0
            elif self.rect_R.collidepoint(event.pos):
                if self.state == 0:
                    self.ddrmi_tumbler_R = pygame.transform.rotate(self.ddrmi_tumbler_R, 90)
                    self.state = 1
                else:
                    self.ddrmi_tumbler_R = pygame.transform.rotate(self.ddrmi_tumbler_R, -90)
                    self.state = 0

    def draw(self, screen, aircraft):
        screen.blit(self.ddrmi_image, (self.x, self.y))
        screen.blit(self.ddrmi_tumbler_R, (self.x + 157, self.y + 150))
        screen.blit(self.ddrmi_tumbler_L, (self.x + 20, self.y + 150))

        distance = int(self.dme_station.calculate_distance(aircraft) // 10)
        ddrmi_text = self.ddrmi_font.render(f'{distance:.1f}'.zfill(2), True, (255, 255, 255))
        ddrmi_rect = ddrmi_text.get_rect(center=(370, 643))
        screen.blit(ddrmi_text, ddrmi_rect)
        
        
class PFDIndicator:
    def __init__(self, x, y,dme_station):
        self.dme_station = dme_station
        self.x = x
        self.y = y
        self.horizon_image = pygame.image.load('images/PFDth/horizon.png')
        self.horizon_image = pygame.transform.scale(self.horizon_image, (300, 300))
        self.vertical_speed = 0
        self.font = pygame.font.Font(None, 24)  # Выберите нужный шрифт
        self.numbers = [self.font.render(str(i), True, (255, 255, 255)) for i in range(100, 999,10)]  # Список изображений чисел от 1 до 100
        self.position = 100.0 


    def speed_indication(self, screen, aircraft):
        speed = aircraft.speed
        start = int(self.position)
        for i in range(start, start + 10):  # Отображаем 10 чисел
            number_image = self.numbers[i % len(self.numbers)]
            y = (i - self.position) * number_image.get_height() + 10
            if i % 2 == 0: # Отображаем только каждое второе число
                screen.blit(number_image, (100, y)) 
            pygame.draw.line(screen, (255, 255, 255), (140, y + number_image.get_height() // 2), (150, y + number_image.get_height() // 2)) # Рисуем риску справа от числа
        diff = speed*1 - self.position
        self.position += diff * 0.1 


    def vs_speed_indication(self, screen, aircraft):
        self.vertical_speed = aircraft.speed * math.sin(math.radians(aircraft.angle))
        
        vs_indicator_x = 273 # координата x центра индикатора вертикальной скорости
        vs_indicator_y = 655 # координата y центра индикатора вертикальной скорости
        
        vs_max_value = 6 # максимальное значение вертикальной скорости
        vs_angle = -(self.vertical_speed / vs_max_value) * 180-180  # угол поворота стрелки
        vs_arrow_length = 13 # длина стрелки
        vs_arrow_start_y = vs_indicator_y + math.sin(math.radians(vs_angle)) * 50 # координата y начала стрелки
        vs_arrow_end_y = vs_indicator_y + math.sin(math.radians(vs_angle)) *6*vs_arrow_length # координата y конца стрелки

        
        vs_text = f"{int(abs(self.vertical_speed) / vs_max_value * 280)}".zfill(2) # текст с нормированным значением вертикальной скорости# нормированное значение вертикальной скорости
        vs_font = pygame.font.Font(None, 16) # шрифт для текста
        color_of_vs_indication= (0, 255, 0) if abs(self.vertical_speed*47)<=51 else (255, 255, 0) if abs(self.vertical_speed*47)<=81 else (255, 155, 0)
        vs_text_render = vs_font.render(vs_text, True, color_of_vs_indication) # рендер текста
        rect_pos=vs_arrow_end_y - 10 if self.vertical_speed <= 0 else vs_arrow_end_y
        vs_text_rect = vs_text_render.get_rect(center=(vs_indicator_x-4, rect_pos+5)) # прямоугольник с текстом
        if int(abs(self.vertical_speed) / vs_max_value * 100) != 0:
            pygame.draw.rect(screen, (0, 0, 0), (vs_indicator_x-14, rect_pos, 15, 10)) # рисуем чёрный квадратик
            screen.blit(vs_text_render, vs_text_rect) # выводим текст с нормированным значением вертикальной скорости внутри квадратика
        pygame.draw.line(screen, color_of_vs_indication, (vs_indicator_x, vs_arrow_start_y), (vs_indicator_x-14, vs_arrow_end_y), 2)


    def dme_indication(self, screen, aircraft):
        self.pfd_font = pygame.font.Font(None, 16)
        pfd_text = self.pfd_font.render(f'{int(self.dme_station.calculate_distance(aircraft)//10)}'.zfill(2), True, (203, 0, 125))
        pfd_rect=pfd_text.get_rect(center=(22, 773))
        screen.blit(pfd_text, pfd_rect)
        if self.dme_station.selected_beacon is not None:
            frequency = self.dme_station.frequencies_bands[self.dme_station.selected_beacon]
            text_frequency = self.pfd_font.render(f"{frequency} ", True, (203, 0, 125))
            text_rect_frequency = text_frequency.get_rect(center=(32, 762))
            screen.blit(text_frequency, text_rect_frequency)


    def draw(self, screen, aircraft):
        
        angle =  aircraft.angle 
        speed = aircraft.speed
        
        speed = aircraft.speed
        max_speed = aircraft.max_speed
        min_speed = aircraft.min_speed
        speed_range = max_speed - min_speed
        normalized_speed = (speed - min_speed) / speed_range
        indicator_x = self.x
        indicator_y = self.y + (1 + normalized_speed/2) * 100
        
        pfd_panel_image = pygame.image.load('images/PFDth/pfd_panel1.png')
        pfd_panel_image = pygame.transform.scale(pfd_panel_image, (300, 300))
        self.speed_indicator_image = pygame.image.load('images/PFDth/speed_pfd_panel.png')
        self.speed_indicator_image = pygame.transform.scale(self.speed_indicator_image, (300, 300))
        screen.blit(self.horizon_image, (self.x, self.y-angle-12))

        screen.blit(self.speed_indicator_image, (indicator_x, indicator_y-140), area=(0,-50,1200,800))

        screen.blit(pfd_panel_image, (self.x, self.y))

        #self.dme_indication(screen, aircraft)
        self.speed_indication(screen, aircraft)
        self.vs_speed_indication(screen, aircraft)

        
class Menu:
    def __init__(self, screen, app, dme_station):
        
        self.screen = screen
        self.app = app
        self.app.simulation_started = False
        self.app.menu_visible = True
        self.app.show_dme_scheme = False
        self.app.map_active = False
        self.beacons=dme_station.beacons
        self.frequencies_bands=dme_station.frequencies_bands
        self.manager = pygame_gui.UIManager((self.screen.get_width(), self.screen.get_height()),'configuration/menu.json')
        self.show()
        self.dme_scheme_image = pygame.image.load('images/scheme_dme.jpg')
        self.map_image = pygame.image.load('images/map.png')
        self.beacon_image = pygame.image.load('images/DME.png')
        self.menu_image = pygame.image.load('images/menu.jpg')
        self.dme_font = pygame.font.Font('fonts/dme_font.ttf', 24)
        self.menu_image = pygame.transform.scale(self.menu_image, (self.screen.get_width(), self.screen.get_height()))


    def show(self):
        self.options = ['Simulation', 'Map', 'Scheme', 'Settings', 'Exit']
        self.buttons = []
        for i, option in enumerate(self.options):
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((220, 200 + i * 55), (200, 50)),text=option, manager=self.manager)
            self.buttons.append(button)
        self.app.menu_visible=True


    def handle_events(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if self.app.menu_visible:
                    if event.ui_element == self.buttons[0]:
                        self.app.simulation_started = True
                        self.app.menu_visible = False
                        
                    elif event.ui_element == self.buttons[1]:
                        self.app.map_active = True
                        self.app.menu_visible = False
                        
                    elif event.ui_element == self.buttons[2]:
                        self.app.show_dme_scheme = True
                        self.app.menu_visible = False
                        
                    elif event.ui_element == self.buttons[4]:
                        pygame.quit()
                        quit()
                        
        elif event.type == pygame.KEYDOWN:
            if self.app.menu_visible == False:
                if event.key == pygame.K_ESCAPE:
                    self.app.simulation_started = False
                    self.app.menu_visible = True
                    self.app.show_dme_scheme = False
                    self.app.map_active = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.app.map_active:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for i, beacon in enumerate(self.beacons):
                        beacon_x, beacon_y = beacon
                        beacon_width, beacon_height = self.beacon_image.get_size()
                        if beacon_x <= mouse_x <= beacon_x + beacon_width and beacon_y <= mouse_y <= beacon_y + beacon_height:
                            self.dme_station.selected_beacon = i
                            break
        elif event.type == pygame.QUIT:
            pygame.quit()
            quit()
                    
        self.manager.process_events(event)


    def draw(self,dme_station):
        self.dme_station=dme_station
        if self.app.menu_visible:
            self.screen.blit(self.menu_image, (0, 0))
            font = pygame.font.Font('fonts/menu_font.ttf', 32)
            info_text = font.render("DME Simulator", True, (225, 235, 255))
            info_text_rect = info_text.get_rect(center=(300, 70))
            self.screen.blit(info_text, info_text_rect)
            font1 = pygame.font.Font('fonts/menu_font.ttf', 16)
            text4 = font1.render("by RRysovets", True, (225, 235, 255))
            text_rect4 = text4.get_rect(center=(1115, 790))
            self.screen.blit(text4, text_rect4)
            self.manager.draw_ui(self.screen)

        if self.app.show_dme_scheme:
            self.screen.blit(self.dme_scheme_image, (0, 0))

        if self.app.map_active:
            self.screen.blit(self.map_image, (0, 0))
            for i, beacon in enumerate(self.beacons):
                self.screen.blit(self.beacon_image, beacon)
                self.beacon_image = pygame.transform.scale(self.beacon_image, (50, 50))
                frequency_color = (255, 0, 0) if i == self.dme_station.selected_beacon else (255, 255, 255)
                frequency_text = f"{self.frequencies_bands[i]} MHz"
                frequency_text_render = self.dme_font.render(frequency_text, True, frequency_color)
                frequency_text_rect = frequency_text_render.get_rect(center=(beacon[0] + self.beacon_image.get_width() / 2, beacon[1] - 20))
                self.screen.blit(frequency_text_render, frequency_text_rect)
        

    def update(self, time_delta):
        self.manager.update(time_delta)


class Aircraft:
    def __init__(self, x, y,width,height):
        self.image = pygame.image.load('images/aircraft.png')
        self.image = pygame.transform.scale(self.image, (100, 40))
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.min_speed = 0.7
        self.max_speed = 5
        self.acceleration = 0.02
        self.deceleration = 0.02
        self.turn_speed = 0.5
        self.accelerate = False
        self.brake = False
        self.turn_left = False
        self.turn_right = False
        self.height=height
        self.width=width
        
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

    def update_position(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        if self.x > self.width:
            self.x = 0
        elif self.x < 0:
            self.x = self.width

        if self.y > self.height:
            self.y = 0
        elif self.y < 0:
            self.y = self.height


    def update_velocity(self, accelerate, brake, turn_left, turn_right):
        if accelerate:
            self.speed += self.acceleration
        if brake:
            self.speed -= self.deceleration
        if turn_left:
            if self.angle < 25:
                self.angle += self.turn_speed
        if turn_right:
            if self.angle > -25:
                self.angle -= self.turn_speed

        self.speed = max(self.min_speed, min(self.max_speed, self.speed))

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(midright=(self.x, self.y)).midright)
        screen.blit(rotated_image, new_rect.topleft)


class DMEApp:
    def __init__(self):

        pygame.init()
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("DME Simulator")
        self.dme_image = pygame.image.load('images/dme_panel.png')
        icon = pygame.image.load('images/icon.png')
        self.clock = pygame.time.Clock()
        pygame.display.set_icon(icon)
        self.dme_station = DMEStation(self.screen_width , self.screen_height)        
        self.aircraft = Aircraft(100, 300,self.screen_width, self.screen_height)
        self.pfd_indicator = PFDIndicator(0, self.screen_width/2.4,self.dme_station)
        self.ddrmi_indicator = DDRMIIndicator(300, self.screen_width/2.4+100,self.dme_station)
        self.menu = Menu(self.screen, self,self.dme_station)
        self.simulation_started = False
        
        
    def boolshit(self):
        """вспомогательные штуки"""
        self.font = pygame.font.Font(None, 24)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_text = f"({mouse_x}, {mouse_y})"
        mouse_text_render = self.font.render(mouse_text, True, (255, 255, 255))
        self.screen.blit(mouse_text_render, (mouse_x + 10, mouse_y))
        angle_text = f"Angle: {self.aircraft.angle:.2f}"
        angle_text_render = self.font.render(angle_text, True, (255, 255, 255))
        self.screen.blit(angle_text_render, (10, 10))


    def handle_events(self):
        for event in pygame.event.get():
            self.aircraft.handle_events(event)
            self.menu.handle_events(event)
            self.ddrmi_indicator.handle_events(event)


    def update(self):
        if self.simulation_started:
            self.aircraft.update_velocity(self.aircraft.accelerate, self.aircraft.brake, self.aircraft.turn_right, self.aircraft.turn_left)
            self.aircraft.update_position()
        time_delta = self.clock.tick(60) / 100.0
        self.menu.update(time_delta)


    def draw(self):
        self.background_image = pygame.image.load('images/airport1.png')
        self.background_image = pygame.transform.scale(self.background_image, (self.screen_width, self.screen_height))
        self.screen.blit(self.background_image, (0, 0))
        self.dme_station.draw(self.screen, self.aircraft)
        self.pfd_indicator.draw(self.screen, self.aircraft)
        self.ddrmi_indicator.draw(self.screen, self.aircraft)
        self.aircraft.draw(self.screen)
        self.menu.draw(self.dme_station)
        self.boolshit()#угол, координаты
        pygame.display.update()
    

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)


app = DMEApp()
app.run()
