import pygame
####import RPi.GPIO as GPIO

# Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
####GPIO.setmode(GPIO.BCM)
physical_connection = {'meter_pulse': 21, 'reset_pulse': 20, 'alarm': 16, 'exit_counter': 26}
#color = {'white': (255, 255, 255), 'black': (0, 0, 0), 'red': (255, 0, 0)}

# Define input pull ups
for i in physical_connection.values():
    ####GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print('Defining inputs', i)

# Initial pygame values
width = 1920
height = 1080
pygame.init()
pygame.mouse.set_visible(False)
font_small = pygame.font.Font(None, 150)
font_big = pygame.font.Font(None, 100)
lcd = pygame.display.set_mode([width, height], pygame.FULLSCREEN)
clock = pygame.time.Clock()


# Initial counter values
current_drum = 0
last_drum = 0
meter_debounce_bit = 0
reset_debounce_bit = 0
done = False
meter_pulse = 0
alarm = 0
reset = 0
start_time = None
timer_second = 0
timer_minute = 0
timer_hour = 0
timer_total_minutes = 0
timer_setpoint_minutes = 60
timer_completion_percent = 0
timer_color_bar = 0
using_as_counter = 0
using_as_timer = 1
start = False

# Working loop
while not done:
    #Loop variables:
    #meter_pulse = GPIO.input(physical_connection['meter_pulse'])
    #alarm = GPIO.input(physical_connection['alarm'])
    #reset = GPIO.input(physical_connection['reset_pulse'])
    meter_pulse = 0
    #alarm = 0
    reset = 0
    color = {'white': (255, 255, 255), 'black': (0, 0, 0), 'red': (255, 0, 0), 'green': (0, int(timer_color_bar), 0)}

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.unicode == 'j':
                print(event.unicode)
                done = True
            if event.unicode == 'a':
                print(event.unicode)
                alarm = True
            else:
                alarm = False
            if event.unicode == 'm':
                print(event.unicode)
                meter_pulse = True
            if event.unicode == 'r':
                print(event.unicode)
                reset = True
            if event.unicode == 's':
                print(event.unicode)
                start = True
                start_time = pygame.time.get_ticks()
                timer_second = 0
                timer_minute = 0
                timer_hour = 0
    if not start:
        start_time = None
    if timer_setpoint_minutes == timer_total_minutes:
        start_time = pygame.time.get_ticks()
        timer_second = 0
        timer_minute = 0
        timer_hour = 0
        timer_setpoint_minutes = 0
    if start_time:
        timer_second = (pygame.time.get_ticks() - start_time)/10
    if int(timer_second) == 60:
        start_time = pygame.time.get_ticks()
        timer_second = 0
        timer_minute += 1
    if timer_minute == 60:
        timer_minute = 0
        timer_hour += 1
    timer_total_minutes += timer_minute
    try:timer_completion_percent = timer_minute / timer_setpoint_minutes
    except: print("oops")
    timer_color_bar = timer_completion_percent * 255


    # Paint background color to red in case of alarm
    if alarm:
        lcd.fill(color['red'])
    elif start:
        lcd.fill(color['green'])
        print (color['green'], timer_total_minutes)
    else:
        lcd.fill(color['black'])
    #clock.tick(1)
    # Set text sizes
    # Current drum
    time = str(timer_hour) + ':' + str(timer_minute) +':'+ str(int(timer_second))
    text_big = font_big.render(time, True, color['white'])
    #text_big = font_big.render('%d' % time_since_enter, True, color['white'])
    text_box_big = text_big.get_rect(center=(width/2, (height + height)/5))
    lcd.blit(text_big, text_box_big)
    # Last drum
    text_small = font_small.render('Viimane trummel  ''%d'' m'%last_drum, True, color['white'])
    text_box_small = text_small.get_rect(center=(width/2, (height - height/10)))
    lcd.blit(text_small, text_box_small)
    pygame.display.update()
    #clock.tick(1)
    # Meter counter
    if not meter_pulse and meter_debounce_bit == 0:
        current_drum += 1
        meter_debounce_bit = 1
        
    # Meter pulse debounce
    if meter_pulse and meter_debounce_bit == 1:
        meter_debounce_bit = 0
            
    # Reset drum length
    if not meter_pulse and reset_debounce_bit == 0:
        last_drum = current_drum
        current_drum = 0
        reset_debounce_bit = 1
        
    # Reset debounce
    if reset:
        reset_debounce_bit = 0
