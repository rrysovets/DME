from data import *
import data
import pygame
import math
import pygame_gui
import os
import data


def calculate_distance(aircraft):
    
    distance = ((aircraft.x - SCREEN_WIDTH//DIV) **2 + (aircraft.y - 600) ** 2)**0.5
    return distance
# class Img_render:
#     def __init__(self,path,params=None):
#         pfd_panel_image = pygame.image.load('images/PFDth/pfd_panel1.png')
#         pfd_panel_image = pygame.transform.scale(pfd_panel_image, (300, 300))
        
# class Txt_render:
#     def __init__(self,text,screen,font=None,size=24,color=(255,255,255)):
#         if font is None:
#             self.font =pygame.font.Font(None, size)
#         else:
#             self.font=font
#         self.text = text
#         self.color = color
#         self.size=size
#         self.screen = screen
    
#     def __call__(self, *args: os.Any, **kwds: os.Any) -> os.Any:
#         angle_text_render = self.font.render(self.text, True, self.color)
#         self.screen.blit(angle_text_render, (10, 10))
        