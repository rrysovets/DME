from common import *


class PFDIndicator:
    def __init__(self,app):
        self.app=app
        self.x = 0
        self.y = SCREEN_WIDTH/2.4
        self.horizon_image = pygame.image.load('images/PFDth/horizon.png')
        self.horizon_image = pygame.transform.scale(
            self.horizon_image, (300, 300))
        self.vertical_speed = 0
        self.font = pygame.font.Font(None, 15)  
        self.height_font=pygame.font.Font(None, 20)  
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
            f'{int(calculate_distance(aircraft)//10)}'.zfill(2), True, (203, 0, 125))
        pfd_rect = pfd_text.get_rect(center=(22, 773))
        screen.blit(pfd_text, pfd_rect)
        
        if data.selected_beacon is not None:
            frequency = FREQUENCIES_BANDS[data.selected_beacon]
            text_frequency = self.pfd_font.render(
                f"{frequency} ", True, (203, 0, 125))
            text_rect_frequency = text_frequency.get_rect(center=(32, 762))
            screen.blit(text_frequency, text_rect_frequency)
            
    def height_indication(self,screen,aircraft):
        
        

        # self.button_rect = pygame.draw.rect(
        #             screen, (123, 142, 146), ((215, 585), (21, 135)))

        self.button_rect = pygame.draw.rect(
                    screen, (0, 0, 0), ((235, 642), (16, 22)))
        for i in range(3):
            
            
            height=int(aircraft.y%100)
            
            incr=int(aircraft.y%10)/10

            img_height=str(height//10%10+i+3 if height//10%10+i+3<=9 else height//10%10+i-7).ljust(2,'0')
            
            pfd_text=self.height_font.render(img_height,True,(0,255,0))
            screen.blit(pfd_text, (236, 640+10*(i-incr)))
            

            #повторно используем переменные
            incr=int(aircraft.y%100)/100
            pos_y=613+100*(i-incr)
            pos_x=218
            wrapper_text=self.font.render('2'+str(int(aircraft.y//100+i)), True, (255, 255, 255))
            line_pos_y=pos_y+30;line_pos_x=pos_x+13
            pygame.draw.line(screen, (255, 255, 255),(line_pos_x, line_pos_y),(line_pos_x+4, line_pos_y))
            self.button_rect = pygame.draw.rect(
                    screen, (0, 0, 0), ((215, 645), (20, 15)))
            
            pfd_text=self.height_font.render('2'+str(int(aircraft.y//100)),True,(0,255,0))
            screen.blit(pfd_text, (pos_x, 647))
            
            screen.blit(wrapper_text,(pos_x, pos_y+26))
            
            
            
            #screen.blit(first_pfd_text, first_pfd_rect)

    def draw(self, screen, aircraft):

        angle = aircraft.angle

        
        pfd_panel_image = pygame.image.load('images/PFDth/pfd_panel1.png')
        pfd_panel_image = pygame.transform.scale(pfd_panel_image, (300, 300))
        
        #pygame.draw.rect(screen, (123, 142, 146), (24, 570, 30, 600))
        pygame.draw.rect(screen, (123, 142, 146), (0, 500, 300, 300))
        self.speed_indication(screen, aircraft)
        self.height_indication(screen,aircraft)
        
        screen.blit(self.horizon_image, (self.x, self.y-angle-12))
        screen.blit(pfd_panel_image, (self.x, self.y))
        self.vs_speed_indication(screen, aircraft)
        self.dme_indication(screen, aircraft)