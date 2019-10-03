import pygame

# If raspberry is not used simulation in other platforms is possible
using_raspberry = True
#Select corret mode either counter or timer
using_as_counter = 1

if using_raspberry:
    import RPi.GPIO as GPIO

    # Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    physical_connection = {'meter_pulse': 26,
                           'reset_pulse': 19,
                           'alarm': 13,
                           'close_ui': 6}
    # Define input pull ups
    for i in physical_connection.values():
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print('Defining inputs', i)

# Initial pygame variables
width = 1700
height = 900
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode([width, height], pygame.FULLSCREEN)
color = {'white': (255, 255, 255),
         'black': (0, 0, 0),
         'red': (255, 0, 0),
         'green': (0, 150, 0)}

small_text_box_message = ''

# Initial counter values
# Drum mode variables
current_drum = 0
last_drum = 0
meter_debounce_bit = 0
reset_debounce_bit = 0
done = False

#Timer mode variables
start_time = None
timer_total_second = 0
timer_setpoint = ''
start = False
word = ''
last_drum_time = 0
setpoint_second = 0
setpoint_minute = 0
setpoint_hour = 0
timer_setpoint_in_seconds = 0
time_left_hour = 0
time_left_minute = 0
time_left_seconds = 0

# Working loop
while not done:
    # Simulation loop for capturing keyboard inputs
    if using_raspberry:
        meter_pulse = GPIO.input(physical_connection['meter_pulse'])
        alarm = GPIO.input(physical_connection['alarm'])
        reset = GPIO.input(physical_connection['reset_pulse'])
        close_ui = GPIO.input(physical_connection['close_ui'])
    else:
        meter_pulse = 0
        reset = 0
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and not event.unicode == '':
            if event.unicode == 'j':
                print(event.unicode)
                done = True
            if not alarm and event.unicode == 'a':
                print(event.unicode)
                alarm = True
            elif alarm and event.unicode == 'a':
                alarm = False
            if event.unicode == 'm':
                meter_pulse = True
                print(event.unicode)
            if event.unicode == 'r':
                reset = True
                start_time = None
                start = 0
            if event.unicode == 's' and not timer_setpoint == '':
                start = True
                start_time = pygame.time.get_ticks()
                timer_total_second = 0
            # Capture and add together user input as strings.
            if event.unicode.isdigit():
                word += event.unicode
                timer_setpoint = int(word)
                if timer_setpoint:
                    setpoint_hour = timer_setpoint / 10000
                    setpoint_minute = (setpoint_hour - int(setpoint_hour)) * 100
                    setpoint_second = (setpoint_minute - int(setpoint_minute)) * 100
            # Press enter to accept the setpoint as int and reset user input
            if event.key == pygame.K_RETURN and word.isdigit():
                # Convert user input as future setpoint
                timer_setpoint_in_seconds = int(setpoint_hour) * 3600 + int(setpoint_minute) * 60 + int(
                    setpoint_second)
                word = ''
    if not meter_pulse:
        start = True
        start_time = pygame.time.get_ticks()
        timer_total_second = 0

    # Stop counting when setpoint has reached
    if timer_setpoint_in_seconds == int(timer_total_second) or not reset:
        start_time = None
        start = 0

    if start_time:
        timer_total_second = int((pygame.time.get_ticks() - start_time) / 1000)
    if start:
        # Finding the time left
        total_time_left_seconds = int(timer_setpoint_in_seconds - timer_total_second)
        time_left_hour = total_time_left_seconds / 3600
        time_left_minute = (time_left_hour - int(time_left_hour)) * 60
        time_left_seconds = (time_left_minute - int(time_left_minute)) * 60
    # Show setpoint in main screen
    else:
        time_left_hour = setpoint_hour
        time_left_minute = setpoint_minute
        time_left_seconds = setpoint_second

    # Add zeros if digit is single
    if time_left_hour < 10:
        hours_to_screen = '0' + str(int(time_left_hour))
    else:
        hours_to_screen = str(int(time_left_hour))
    if time_left_minute < 10:
        minutes_to_screen = '0' + str(int(time_left_minute))
    else:
        minutes_to_screen = str(int(time_left_minute))
    if time_left_seconds < 10:
        seconds_to_screen = '0' + str(int(time_left_seconds))
    else:
        seconds_to_screen = str(int(time_left_seconds))

    # Form classic clock look
    if not start:
        time = hours_to_screen + ':' + minutes_to_screen + ':' + seconds_to_screen
        last_drum_time = time
    else:
        time = hours_to_screen + ':' + minutes_to_screen + ':' + seconds_to_screen

    # Paint background color to red in case of alarm
    if not alarm:
        lcd.fill(color['red'])
    elif timer_setpoint_in_seconds == int(timer_total_second) and not timer_setpoint_in_seconds == 0:
        lcd.fill(color['green'])
    else:
        lcd.fill(color['black'])

    # Current drum
    if using_as_counter:
        font_small = pygame.font.Font(None, 150)
        font_big = pygame.font.Font(None, 800)

        text_big = font_big.render('%d' %current_drum, True, color['white'])
        text_small_bottom = font_small.render('Viimane trummel  ''%d'' m' % last_drum, True, color['white'])
        # Main textbox
        text_box_big = text_big.get_rect(center=(width / 2, (height + height) / 4))
        lcd.blit(text_big, text_box_big)

        # Subbox
        text_box_small = text_small_bottom.get_rect(center=(width / 2, (height - height / 10)))
        lcd.blit(text_small_bottom, text_box_small)
    else:
        font_small = pygame.font.Font(None, 100)
        font_big = pygame.font.Font(None, 600)
        text_big = font_big.render(time, True, color['white'])
        if not start:
            text_small_bottom = font_small.render('Palun sisesta töö pikkus ja vajuta enter', True, color['white'])
        else:
            text_small_bottom = font_small.render('Etteantud aeg %s' % last_drum_time, True, color['white'])
            # Main textbox
        text_box_big = text_big.get_rect(midleft=(width / 16, (height + height) / 4))
        lcd.blit(text_big, text_box_big)

        # Subbox
        text_box_small = text_small_bottom.get_rect(center=(width / 2, (height - height / 10)))
        lcd.blit(text_small_bottom, text_box_small)
    # Set text sizes

    #Keep updating every cycle
    pygame.display.update()
    print (meter_pulse, reset, alarm)
    # Meter counter
    if not meter_pulse and meter_debounce_bit == 0:
        current_drum += 1
        meter_debounce_bit = 1

    # Meter pulse debounce
    if meter_pulse and meter_debounce_bit == 1:
        meter_debounce_bit = 0

    # Reset drum length
    if not reset and reset_debounce_bit == 0:
        last_drum = current_drum
        current_drum = 0
        reset_debounce_bit = 1

    # Reset debounce
    if reset:
        reset_debounce_bit = 0
