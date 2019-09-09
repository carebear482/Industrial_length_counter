import pygame
import os
import time
from time import sleep
import RPi.GPIO as GPIO
 
# Note #21 changed to #27 for rev2 Pi
button_map = {21:(0, 0, 0)}
# Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
GPIO.setmode(GPIO.BCM)
for meter_pulse in button_map.keys():
    GPIO.setup(meter_pulse, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# Colours
WHITE = (255, 255, 255)
 
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((1500, 1024),pygame.FULLSCREEN)
pygame.display.update()
startup = 0
count = 0
if startup == 0:
    marker = 0
    marker1 = 0
    startup = 1
    reset = 0
    lastdrum = 0


font_small = pygame.font.Font(None, 150)
font_big = pygame.font.Font(None, 800)
while True:
    # Scan the buttons
    pygame.display.update()
    for (meter_pulse, v) in button_map.items():

        if GPIO.input(meter_pulse) == 0 or marker == 0:
            if not GPIO.input(19):
                lcd.fill((255,0,0))
            if GPIO.input(19):
                lcd.fill(v)
            # Meter mark
            time.sleep(.01)
            text_surface = font_big.render('%d'%count, True, WHITE)
            rect = text_surface.get_rect(center=(1500/2, 400))
            lcd.blit(text_surface, rect)
            # last drum
            text_surface2 = font_small.render('Viimane trummel  ''%d'' m'%lastdrum, True, WHITE)
            rect2 = text_surface2.get_rect(center=(700, 900))
            lcd.blit(text_surface2, rect2)
            pygame.display.update()
        if GPIO.input(meter_pulse) == 0 and marker == 0:            
            count += 1
            marker = 1
            print('marker', marker)
            print('Nupp', GPIO.input(meter_pulse))
        if GPIO.input(meter_pulse) == 1 and marker == 1:
            marker = 0
        if GPIO.input(20) == False and marker1 == 0:
            lastdrum = count
            count = 0
            marker1 = 1
            sleep(0.1)
        if GPIO.input(20):
            marker1 = 0
        if not GPIO.input(26):
            pygame.display.quit()
            pygame.quit()
            quit()
            
sleep(0.1)
