import pygame
import os
import time
from time import sleep
import RPi.GPIO as GPIO

physical_connection = {'meter_pulse':21,'reset_pulse':20,'alarm':16, 'exit_counter': 26 }
color =  {'white' : (255, 255, 255),'black' : (0, 0, 0), 'red' : (255, 0, 0)}
# Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
GPIO.setmode(GPIO.BCM)
for i in physical_connection.values():
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print ('Defining inputs', i)    

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((1500, 1024))
#lcd = pygame.display.set_mode((1500, 1024),pygame.WINDOW)
pygame.display.update()
current_count = 0
marker = 0
marker1 = 0
lastdrum = 0

font_small = pygame.font.Font(None, 150)
font_big = pygame.font.Font(None, 800)

while True:
    # Scan the buttons
    if GPIO.input(physical_connection['meter_pulse']) == 0 or marker == 0:
        if not GPIO.input(physical_connection['alarm']):
            lcd.fill(color['red'])
            print ('alarm')
        else:
            lcd.fill(color['black'])
            
        if GPIO.input(physical_connection['meter_pulse']):
            # Meter mark
            time.sleep(.01)
            text_surface = font_big.render('%d'%current_count, True, color['white'])
            rect = text_surface.get_rect(center=(1500/2, 400))
            lcd.blit(text_surface, rect)
            # last drum
            text_surface2 = font_small.render('Viimane trummel  ''%d'' m'%lastdrum, True, color['white'])
            rect2 = text_surface2.get_rect(center=(700, 900))
            lcd.blit(text_surface2, rect2)
            pygame.display.update()
            
        if GPIO.input(physical_connection['meter_pulse']) == 0 and marker == 0:            
            current_count += 1
            marker = 1
            print('marker', marker)
            print('Nupp', GPIO.input(physical_connection['meter_pulse']))
        if GPIO.input(physical_connection['meter_pulse']) == 1 and marker == 1:
            marker = 0
        if GPIO.input(physical_connection['reset_pulse']) == False and marker1 == 0:
            lastdrum = current_count
            current_count = 0
            marker1 = 1
            sleep(0.1)
        if GPIO.input(physical_connection['reset_pulse']):
            marker1 = 0
            
        if not GPIO.input(26):
            pygame.display.quit()
            pygame.quit()
            quit()
            
sleep(0.1)
