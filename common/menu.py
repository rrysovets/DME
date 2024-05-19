from common import *
import g4f
from g4f.client import Client
class Menu:
    def __init__(self, screen, app):
        self.chat_text = ''
        self.current_element = 0

        self.screen = screen
        self.app = app
        self.app.simulation_started = False
        self.app.menu_visible = True
        self.app.show_dme_scheme = False
        self.app.map_active = False
        self.app.show_gpt = False

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
                        'Circuit description', 'Copilot', 'Exit')

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
            # bot.send_message(chat_id=387352688,text='тут будет инструкция')################бот################
            os.startfile('dme.pdf')
        elif self.current_element == 4:
            self.app.show_gpt = True

    def res(self,text):
        return g4f.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role": "user", "content": f"{text}"}],stream=True,)
    # async def res1(self,text):
    #     await self.res1(text)

    # def insert_newlines(self, string, max_line_length):
    #     lines = string.split('\n')
    #     for i in range(len(lines)):
    #         line = lines[i]
    #         if len(line) > max_line_length:
    #             num_of_splits = len(line) // max_line_length
    #             split_lines = [
    #                 line[j*max_line_length:(j+1)*max_line_length] for j in range(num_of_splits)]
    #             if len(line) % max_line_length != 0:
    #                 split_lines.append(line[num_of_splits*max_line_length:])
    #             lines[i] = '\n'.join(split_lines)
    #     return '\n'.join(lines)

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
                    self.app.show_gpt=False
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
                        self.current_element = len(self.options)-1
                elif event.key == pygame.K_DOWN:
                    if self.current_element < len(self.options)-1:
                        self.current_element += 1
                    else:
                        self.current_element = 0
                elif event.key == pygame.K_RETURN:
                    self.select_option()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.app.map_active:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, beacon in enumerate(BEACONS):
                    beacon_x, beacon_y = beacon
                    beacon_width, beacon_height = self.beacon_image.get_size()
                    
                    if beacon_x <= mouse_x <= beacon_x + beacon_width and beacon_y <= mouse_y <= beacon_y + beacon_height:
                        
                        data.selected_beacon = i
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
            if self.app.show_gpt:
                if not self.button_rect.collidepoint(event.pos):
                    self.app.show_gpt = False

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

        if self.app.show_gpt:

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:

                    self.chat_text += '\n'

                    response = self.res(self.chat_text)
                    print('ответ пошёл')
                    print(response)
                    for message in response:
                        self.chat_text += message
                    self.chat_text += '\n'

                elif event.key == pygame.K_BACKSPACE:
                    self.chat_text = self.chat_text[:-1]
                    
                elif event.key == pygame.K_ESCAPE:
                    self.app.show_gpt = False
                else:

                    self.chat_text += event.unicode
                    

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
                    255, 0, 0) if i == data.selected_beacon else (255, 255, 255)
                frequency_text = f"{FREQUENCIES_BANDS[i]} MHz"
                frequency_text_render = self.dme_font.render(
                    frequency_text, True, frequency_color)
                frequency_text_rect = frequency_text_render.get_rect(
                    center=(beacon[0] + self.beacon_image.get_width() / 2, beacon[1] - 20))
                self.screen.blit(frequency_text_render, frequency_text_rect)
        if self.app.show_gpt:
            chat_text_height = 110

            self.button_rect = pygame.draw.rect(
                self.screen, (247, 240, 255), (100, 100, 1000, 600))
            pygame.draw.rect(self.screen, (0, 0, 0), (100, 100, 1000, 600), 4)
            for i in self.chat_text.split('\n'):
                self.text = self.button_font.render(
                    i, True, (0, 0, 0), (247, 240, 255),900)
                self.screen.blit(
                    self.text, ((110, chat_text_height), (980, 580)),)
                chat_text_height += 30