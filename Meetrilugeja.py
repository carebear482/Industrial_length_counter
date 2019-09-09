import pygame
#import os
#import time
from time import sleep
import RPi.GPIO as GPIO

# Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
GPIO.setmode(GPIO.BCM)
physical_connection = {'meter_pulse':21,'reset_pulse':20,'alarm':16, 'exit_counter': 26 }
color =  {'white' : (255, 255, 255),'black' : (0, 0, 0), 'red' : (255, 0, 0)}

#Define input pull ups
for i in physical_connection.values():
    GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print ('Defining inputs', i)
#Initial values
pygame.init()
pygame.mouse.set_visible(False)
font_small = pygame.font.Font(None, 150)
font_big = pygame.font.Font(None, 800)
lcd = pygame.display.set_mode((1500, 1024))

current_drum = 0
meter_debounce_bit = 0
reset_debounce_bit = 0
last_drum = 0


#Working loop
while True:
    #Paint background color to red in case of alarm
    if not GPIO.input(physical_connection['alarm']):
        lcd.fill(color['red'])
        print ('alarm')
    else:
        lcd.fill(color['black'])
        
    #set text sizes    
    if GPIO.input(physical_connection['meter_pulse']):
        #Current drum
        text_big = font_big.render('%d'%current_drum, True, color['white'])
        text_box_big = text_big.get_rect(center=(750, 400))
        lcd.blit(text_big, text_box_big)
        #Last drum
        text_small = font_small.render('Viimane trummel  ''%d'' m'%last_drum, True, color['white'])
        text_box_small = text_small.get_rect(center=(700, 900))
        lcd.blit(text_small, text_box_small)
        pygame.display.update()
        
    #Meter counter   
    if not GPIO.input(physical_connection['meter_pulse']) and meter_debounce_bit == 0:            
        current_drum += 1
        meter_debounce_bit = 1
        
    #Meter pulse debounce    
    if GPIO.input(physical_connection['meter_pulse']) and meter_debounce_bit == 1:
        meter_debounce_bit = 0
            
    #Reset drum length
    if not GPIO.input(physical_connection['reset_pulse']) and reset_debounce_bit == 0:
        last_drum = current_drum
        current_drum = 0
        reset_debounce_bit = 1
        
    #Reset debounce
    if GPIO.input(physical_connection['reset_pulse']):
        reset_debounce_bit = 0