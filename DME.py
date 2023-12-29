import pygame
import math
from pygame import mixer
import pygame_gui
import os
from data import *


class DMEStation:
    DIV = 2
    x = SCREEN_WIDTH//DIV
    y = SCREEN_HEIGHT//DIV
    selected_beacon = 1

    def __init__(self):

        self.radius = 100
        self.track_mode = False
        self.search_mode = True
        self.color_track = (0, 0, 255)
        self.color_search = (0, 255, 0)
        self.color = self.color_search

        self.font = pygame.font.Font('fonts/dme_font.ttf', 40)

        self.beacon_calls = [mixer.Sound(
            f'mp3s/позывные/{i + 1}.mp3') for i in range(len(BEACONS))]

    def draw(self, screen, aircraft):

        if self.track_mode:
            color_DME = self.color_track

        else:
            color_DME = self.color_search

        left_point = (self.x - self.radius, self.y)
        right_point = (self.x + self.radius, self.y)
        top_point = (self.x, self.y*self.DIV)
        points = [left_point, right_point, top_point]

        diagram_surface = pygame.Surface(
            (self.x*self.DIV, self.y*self.DIV), pygame.SRCALPHA)
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
                if self.selected_beacon is not None:
                    self.beacon_calls[self.selected_beacon].play()
        else:
            # Aircraft is outside diagram
            if self.track_mode:
                self.track_mode = False
                self.search_mode = True
                self.color = self.color_search

        screen.blit(diagram_surface, (0, 0))

    @classmethod
    def calculate_distance(cls, aircraft):
        distance = math.sqrt((aircraft.x - SCREEN_WIDTH//cls.DIV) **
                             2 + (aircraft.y - 600) ** 2)
        return distance


class DDRMIIndicator:
    def __init__(self, x, y, dme_station):
        self.dme_station = dme_station
        self.x = x
        self.y = y
        self.state = 0  # Добавляем состояние тумблера

        self.ddrmi_image = self.load_image(
            'images/DDRMI/DDRMI_indicator.png', 200, 200)
        self.ddrmi_tumbler_L = self.load_image(
            'images/DDRMI/DDRMI_tumbler_L.png', 30, 35)
        self.ddrmi_tumbler_R = self.load_image(
            'images/DDRMI/DDRMI_tumbler_R.png', 30, 35)

        # Создаем прямоугольники для обработки кликов мыши
        self.rect_L = self.ddrmi_tumbler_L.get_rect(
            topleft=(self.x + 20, self.y + 150))
        self.rect_R = self.ddrmi_tumbler_R.get_rect(
            topleft=(self.x + 160, self.y + 150))

        self.ddrmi_font = pygame.font.Font('fonts/dme_font.ttf', 22)

    def load_image(self, path, width, height):
        image = pygame.image.load(path)
        return pygame.transform.scale(image, (width, height))

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect_L.collidepoint(event.pos):
                if self.state == 0:
                    self.ddrmi_tumbler_L = pygame.transform.rotate(
                        self.ddrmi_tumbler_L, -90)
                    self.state = 1
                else:
                    self.ddrmi_tumbler_L = pygame.transform.rotate(
                        self.ddrmi_tumbler_L, 90)
                    self.state = 0
            elif self.rect_R.collidepoint(event.pos):
                if self.state == 0:
                    self.ddrmi_tumbler_R = pygame.transform.rotate(
                        self.ddrmi_tumbler_R, 90)
                    self.state = 1
                else:
                    self.ddrmi_tumbler_R = pygame.transform.rotate(
                        self.ddrmi_tumbler_R, -90)
                    self.state = 0

    def draw(self, screen, aircraft):
        screen.blit(self.ddrmi_image, (self.x, self.y))
        screen.blit(self.ddrmi_tumbler_R, (self.x + 157, self.y + 150))
        screen.blit(self.ddrmi_tumbler_L, (self.x + 20, self.y + 150))

        distance = int(DMEStation.calculate_distance(aircraft) // 10)
        ddrmi_text = self.ddrmi_font.render(
            f'{distance:.1f}'.zfill(2), True, (255, 255, 255))
        ddrmi_rect = ddrmi_text.get_rect(center=(370, 643))
        screen.blit(ddrmi_text, ddrmi_rect)


class PFDIndicator:
    def __init__(self):

        self.x = 0
        self.y = SCREEN_WIDTH/2.4
        self.horizon_image = pygame.image.load('images/PFDth/horizon.png')
        self.horizon_image = pygame.transform.scale(
            self.horizon_image, (300, 300))
        self.vertical_speed = 0
        self.font = pygame.font.Font(None, 15)  
        self.height_font=pygame.font.Font(None, 18)  
        self.numbers = [self.font.render(str(abs(i)), True, (255, 255, 255)) for i in range(
            100, 400, 10)]  # Список изображений чисел от 1 до 100
        self.position = 0

    def speed_indication(self, screen, aircraft):
        speed = aircraft.speed
        start = int(self.position)
        for i in range(start, start+100):  # Отображаем 10 чисел
            number_image = self.numbers[-((i-10) % len(self.numbers))]
            y = (i - self.position) * number_image.get_height() + 10
            if i % 2 == 0:  # Отображаем только каждое второе число
                screen.blit(number_image, (25, y+550))
            pygame.draw.line(screen, (255, 255, 255), (45, y + 550 + number_image.get_height() // 2),
                             (49, y + 550 + number_image.get_height() // 2))  # Рисуем риску справа от числа
        diff = speed*3 + self.position
        self.position -= diff * 0.2

    def vs_speed_indication(self, screen, aircraft):
        self.vertical_speed = aircraft.speed * \
            math.sin(math.radians(aircraft.angle))

        vs_indicator_x = 273  # координата x центра индикатора вертикальной скорости
        vs_indicator_y = 655  # координата y центра индикатора вертикальной скорости

        vs_max_value = 6  # максимальное значение вертикальной скорости
        vs_angle = -(self.vertical_speed / vs_max_value) * \
            180-180  # угол поворота стрелки
        vs_arrow_length = 13  # длина стрелки
        vs_arrow_start_y = vs_indicator_y + \
            math.sin(math.radians(vs_angle)) * \
            50  # координата y начала стрелки
        vs_arrow_end_y = vs_indicator_y + \
            math.sin(math.radians(vs_angle)) * 6 * \
            vs_arrow_length  # координата y конца стрелки

        # текст с нормированным значением вертикальной скорости# нормированное значение вертикальной скорости
        vs_text = f"{int(abs(self.vertical_speed) / vs_max_value * 280)}".zfill(2)
        vs_font = pygame.font.Font(None, 16)  # шрифт для текста
        color_of_vs_indication = (0, 255, 0) if abs(
            self.vertical_speed*47) <= 71 else (255, 155, 0)
        vs_text_render = vs_font.render(
            vs_text, True, color_of_vs_indication)  # рендер текста
        rect_pos = vs_arrow_end_y - 10 if self.vertical_speed <= 0 else vs_arrow_end_y
        vs_text_rect = vs_text_render.get_rect(
            center=(vs_indicator_x-4, rect_pos+5))  # прямоугольник с текстом
        if int(abs(self.vertical_speed) / vs_max_value * 100) != 0:
            # рисуем чёрный квадратик
            pygame.draw.rect(screen, (0, 0, 0),
                             (vs_indicator_x-14, rect_pos, 15, 10))
            # выводим текст с нормированным значением вертикальной скорости внутри квадратика
            screen.blit(vs_text_render, vs_text_rect)
        pygame.draw.line(screen, color_of_vs_indication, (vs_indicator_x,
                         vs_arrow_start_y), (vs_indicator_x-14, vs_arrow_end_y), 2)

    def dme_indication(self, screen, aircraft):
        self.pfd_font = pygame.font.Font(None, 16)
        pfd_text = self.pfd_font.render(
            f'{int(DMEStation.calculate_distance(aircraft)//10)}'.zfill(2), True, (203, 0, 125))
        pfd_rect = pfd_text.get_rect(center=(22, 773))
        screen.blit(pfd_text, pfd_rect)
        if DMEStation.selected_beacon is not None:
            frequency = FREQUENCIES_BANDS[DMEStation.selected_beacon]
            text_frequency = self.pfd_font.render(
                f"{frequency} ", True, (203, 0, 125))
            text_rect_frequency = text_frequency.get_rect(center=(32, 762))
            screen.blit(text_frequency, text_rect_frequency)
            
    def height_indication(self,screen,aircraft):
        
        
        numbers = [self.height_font.render(str(abs(i)).zfill(2), True, (0, 255, 0)) for i in range(
            00, 100, 10)]
        
        self.button_rect = pygame.draw.rect(
                    screen, (123, 142, 146), ((215, 585), (21, 135)))
        self.button_rect = pygame.draw.rect(
                    screen, (0, 0, 0), ((215, 645), (20, 15)))
        self.button_rect = pygame.draw.rect(
                    screen, (0, 0, 0), ((235, 642), (16, 22)))
        for i in range(5):
            
            height=int(4000-aircraft.y)
            str_height=f"{4000-aircraft.y:.0f}"
            
            first_pfd_text=self.height_font.render(str_height[0:2],True,(0,255,0))
            height_2=int(str_height[2::])+i
            pfd_text=self.height_font.render(str(height_2).zfill(2),True,(0,255,0))
            first_pfd_rect = first_pfd_text.get_rect(center=(225, 655))
            
            #wrapper_text=self.font.render(str(int(str_height[0:2])+i), True, (255, 255, 255))
            
            
            screen.blit(pfd_text, (236, 613+i*10+(height%98)%10))
            #screen.blit(wrapper_text,(216, 613+i*50+(height//98)%10))
            screen.blit(first_pfd_text, first_pfd_rect)

    def draw(self, screen, aircraft):

        angle = aircraft.angle
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
        # self.speed_indicator_image = pygame.image.load('images/PFDth/speed_pfd_panel.png')
        # self.speed_indicator_image = pygame.transform.scale(self.speed_indicator_image, (300, 300))
        screen.blit(self.horizon_image, (self.x, self.y-angle-12))
        pygame.draw.rect(screen, (123, 142, 146), (24, 570, 30, 600))
        self.speed_indication(screen, aircraft)
        # screen.blit(self.speed_indicator_image, (indicator_x,indicator_y-140), area=(0, -50, 1200, 800))
        self.height_indication(screen,aircraft)
        screen.blit(pfd_panel_image, (self.x, self.y))

        self.vs_speed_indication(screen, aircraft)
        self.dme_indication(screen, aircraft)
        

class Menu:
    def __init__(self, screen, app):

        self.current_element = 0

        self.screen = screen
        self.app = app
        self.app.simulation_started = False
        self.app.menu_visible = True
        self.app.show_dme_scheme = False
        self.app.map_active = False

        self.manager = pygame_gui.UIManager(
            (self.screen.get_width(), self.screen.get_height()), 'configuration/menu.json')
        self.__circuit_button_gen()
        self.font = pygame.font.Font('fonts/menu_font.ttf', 32)
        self.button_font = pygame.font.Font(None, 18)
        self.dme_scheme_image = pygame.image.load('images/scheme_dme.png')
        self.map_image = pygame.image.load('images/map.png')
        self.beacon_image = pygame.image.load('images/DME.png')
        self.menu_image = pygame.image.load('images/menu.jpg')
        self.dme_font = pygame.font.Font('fonts/dme_font.ttf', 24)
        self.menu_image = pygame.transform.scale(
            self.menu_image, (self.screen.get_width(), self.screen.get_height()))
        self.options = ('Simulation', 'Map', 'Circuit',
                        'Circuit description', 'Exit')

    def __circuit_button_gen(self):
        self.app.button_on = False

        self.buttons = []
        for i, option in enumerate(SCHEME_OPTIONS):
            button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(
                option), text='', manager=self.manager)
            self.buttons.append(button)
        self.app.menu_visible = True

    def select_option(self):
        if self.current_element == 0:
            self.app.simulation_started = True
            self.app.menu_visible = False

        elif self.current_element == 1:
            self.app.map_active = True
            self.app.menu_visible = False

        elif self.current_element == 2:
            self.app.show_dme_scheme = True
            self.app.menu_visible = False

        elif self.current_element == 3:
            os.startfile('dme.pdf')

        elif self.current_element == 4:
            pygame.quit()
            quit()

    def handle_events(self, event):
        # кнопки
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if self.app.show_dme_scheme:
                    for i, option in enumerate(SCHEME_OPTIONS):
                        if event.ui_element == self.buttons[i]:
                            self.app.button_on = True
                            self.current_button = i

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if self.app.button_on:
                    self.app.button_on = False
                else:
                    self.app.menu_visible = True
                    self.app.simulation_started = False
                    self.app.show_dme_scheme = False
                    self.app.map_active = False

            if self.app.menu_visible:
                if event.key == pygame.K_UP:
                    if self.current_element > 0:
                        self.current_element -= 1
                    else:
                        self.current_element=len(self.options)-1
                elif event.key == pygame.K_DOWN:
                    if self.current_element < len(self.options)-1:
                        self.current_element += 1
                    else:
                        self.current_element=0
                elif event.key == pygame.K_RETURN:
                    self.select_option()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.app.map_active:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, beacon in enumerate(BEACONS):
                    beacon_x, beacon_y = beacon
                    beacon_width, beacon_height = self.beacon_image.get_size()
                    if beacon_x <= mouse_x <= beacon_x + beacon_width and beacon_y <= mouse_y <= beacon_y + beacon_height:
                        DMEStation.selected_beacon = i
                        break
            if self.app.menu_visible:
                for i, option in enumerate(self.options):
                    text = self.font.render(option, True, (0, 0, 0))
                    text_rect = text.get_rect(center=(300, 225 + i * 55))
                    if text_rect.collidepoint(event.pos):

                        self.current_element = i
                        self.select_option()
                        break
            if self.app.button_on:
                if not self.button_rect.collidepoint(event.pos):
                    self.app.button_on = False

        elif event.type == pygame.MOUSEMOTION and self.app.menu_visible:
            for i, option in enumerate(self.options):
                text = self.font.render(option, True, (0, 0, 0))
                text_rect = text.get_rect(center=(300, 225 + i * 55))
                if text_rect.collidepoint(event.pos):
                    self.current_element = i
                    break

        elif event.type == pygame.QUIT:
            pygame.quit()
            quit()

        self.manager.process_events(event)

    def draw(self):

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

            for i, option in enumerate(self.options):
                color = (255, 255, 255) if i == self.current_element else (
                    100, 100, 100)
                self.text = self.font.render(option, True, color)
                self.text_rect = self.text.get_rect(center=(300, 225 + i * 55))
                self.screen.blit(self.text, self.text_rect)

        if self.app.show_dme_scheme:

            self.screen.blit(self.dme_scheme_image, (0, 0))
            self.manager.draw_ui(self.screen)
            time_delta = self.app.clock.tick(60) / 100.0
            self.manager.update(time_delta)
            if self.app.button_on:
                self.text = self.button_font.render(
                    CIRCUIT_DESCRIPTIONS[self.current_button], True, (0, 0, 0), (247, 240, 255))
                self.button_rect = pygame.draw.rect(
                    self.screen, (247, 240, 255), (100, 100, 1000, 600))
                pygame.draw.rect(self.screen, (0, 0, 0),
                                 (100, 100, 1000, 600), 4)
                self.screen.blit(self.text, ((110, 110), (980, 580)),)

        if self.app.map_active:
            self.screen.blit(self.map_image, (0, 0))
            for i, beacon in enumerate(BEACONS):
                self.screen.blit(self.beacon_image, beacon)
                self.beacon_image = pygame.transform.scale(
                    self.beacon_image, (50, 50))
                frequency_color = (
                    255, 0, 0) if i == DMEStation.selected_beacon else (255, 255, 255)
                frequency_text = f"{FREQUENCIES_BANDS[i]} MHz"
                frequency_text_render = self.dme_font.render(
                    frequency_text, True, frequency_color)
                frequency_text_rect = frequency_text_render.get_rect(
                    center=(beacon[0] + self.beacon_image.get_width() / 2, beacon[1] - 20))
                self.screen.blit(frequency_text_render, frequency_text_rect)
   

class Aircraft:
    def __init__(self,app):
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


class DMEApp:
    def __init__(self):
        self.a=0,0;self.flag=False#dogshit+boolshit parameters
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
        self.pfd_indicator = PFDIndicator()
        self.ddrmi_indicator = DDRMIIndicator(
            300, self.screen_width/2.4+100, self.dme_station)
        self.menu = Menu(self.screen, self)

    def boolshit(self,a):
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
            pygame.draw.rect(self.screen, (0, 0, 0,225), a)

    def dogshit(self, event):
        
        self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN :

            self.a = (self.mouse_x, self.mouse_y)
            self.flag=True
            
        if event.type == pygame.MOUSEMOTION and self.flag:
            
            return self.a, (abs(self.a[0]-self.mouse_x),abs(self.a[1]-self.mouse_y))
                
            
        elif event.type == pygame.MOUSEBUTTONUP:
            print((self.a, (abs(self.a[0]-self.mouse_x),abs(self.a[1]-self.mouse_y))), end=',\n')
            self.flag=False
            return self.a, (abs(self.a[0]-self.mouse_x),abs(self.a[1]-self.mouse_y))

    def handle_events(self):
        for event in pygame.event.get():
            self.aircraft.handle_events(event)
            self.menu.handle_events(event)
            self.ddrmi_indicator.handle_events(event)
            self.coords=(0,0,0,0)
            self.coords=self.dogshit(event)

    def draw(self):
        
        self.background_image = pygame.image.load('images/airport.png')
        self.background_image = pygame.transform.scale(
            self.background_image, (self.screen_width, self.screen_height))
        self.screen.blit(self.background_image, (0, 0))
        self.dme_station.draw(self.screen, self.aircraft)
        self.pfd_indicator.draw(self.screen, self.aircraft)
        # self.ddrmi_indicator.draw(self.screen, self.aircraft)
        self.aircraft.draw(self.screen)
        self.menu.draw()
        self.boolshit(self.coords)  # угол, координаты
        
        
        pygame.display.update()

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)


app = DMEApp()
app.run()
