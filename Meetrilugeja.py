import pygame

# If raspberry is not used simulation in other platforms is possible
using_raspberry = False
if using_raspberry:
    import RPi.GPIO as GPIO

    # Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    physical_connection = {'meter_pulse': 26, 'reset_pulse': 19, 'alarm': 13, 'close_ui': 6, 'timer_mode': 5}
    # Define input pull ups
    for i in physical_connection.values():
        GPIO.setup(i, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print('Defining inputs', i)
    meter_pulse = GPIO.input(physical_connection['meter_pulse'])
    alarm = GPIO.input(physical_connection['alarm'])
    reset = GPIO.input(physical_connection['reset_pulse'])
    close_ui = GPIO.input(physical_connection['close_ui'])

# Initial pygame variables
width = 1920
height = 1080
pygame.init()
pygame.mouse.set_visible(False)
font_small = pygame.font.Font(None, 150)
font_big = pygame.font.Font(None, 400)
lcd = pygame.display.set_mode([width, height], pygame.FULLSCREEN)
color = {'white': (255, 255, 255),
         'black': (0, 0, 0),
         'red': (255, 0, 0),
         'green': (0, 150, 0)}

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
timer_setpoint_minutes = ''
timer_completion_percent = 0
timer_color_bar = 0
using_as_counter = 0
using_as_timer = 1
start = False
word = ''
last_drum_time = 0
setpoint_seconds = 0
seconds_left = 0
# Working loop
while not done:

    # Loop variables:
    meter_pulse = 0
    reset = 0

    # Simulation loop for capturing keyboard inputs
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
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

            if event.unicode == 'r':
                reset = True

            if event.unicode == 's' and not timer_setpoint_minutes == '':
                start = True
                start_time = pygame.time.get_ticks()
                timer_second = 0
                timer_minute = 0
                timer_hour = 0
                timer_total_minutes = 0
                last_drum_time = timer_total_minutes
            # Capture and add together user input as strings.
            if event.unicode.isdigit():
                if word == 0:
                    word = ''
                word += event.unicode

            # Press enter to accept the setpoint as int and reset user input
            if event.key == pygame.K_RETURN and not start and word :
                if word.isdigit():
                    #Convert user input as future setpoint
                    timer_setpoint_minutes = int(word)
                    setpoint_seconds = timer_setpoint_minutes * 60
                    setpoint_hours = timer_setpoint_minutes / 60
                    setpoint_minutes = timer_setpoint_minutes - int(setpoint_hours) * 60
                    print('new setpoint set!', int(setpoint_hours),'hours', int(setpoint_minutes),'min', setpoint_seconds, 'sec')
                    word = ''

    # Avoid exception by setting empty string to 0
    if not word:
        word = 0

    # Stop counting when setpoint has reached
    if timer_setpoint_minutes == timer_total_minutes:
        start_time = None
        start = 0

    if start_time:
        timer_second = (pygame.time.get_ticks() - start_time) / 100
    if setpoint_seconds > 0:
        seconds_left = timer_second - setpoint_seconds
    if int(seconds_left) >= 60:
        start_time = pygame.time.get_ticks()
        timer_second = 0
        timer_minute += 1
        timer_total_minutes += 1
    if timer_minute >= 60:
        timer_minute = 0
        timer_hour += 1
    # Add zeros if digit is single
    if timer_hour < 10:
        hours_to_screen = '0' + str(timer_hour)
    else:
        hours_to_screen = str(timer_hour)
    if timer_minute < 10:
        minutes_to_screen = '0' + str(timer_minute)
    else:
        minutes_to_screen = str(timer_minute)
    if timer_second < 10:
        seconds_to_screen = '0' + str(int(timer_second))
    else:
        seconds_to_screen = str(int(timer_second))

    # Countdown

    time = hours_to_screen + ':' + minutes_to_screen + ':' + seconds_to_screen

    # Paint background color to red in case of alarm
    if alarm:
        lcd.fill(color['red'])
    elif timer_setpoint_minutes == timer_total_minutes:
        lcd.fill(color['green'])
    else:
        lcd.fill(color['black'])


    # Current drum
    if using_as_counter:
        text_big = font_big.render(current_drum, True, color['white'])
        text_small_bottom = font_small.render('Viimane trummel  ''%d'' m' % last_drum, True, color['white'])
        text_small_top = font_small.render('' '%d' % '', True, color['white'])
    else:
        text_small_top = font_small.render('Palun sisesta töö pikkus ' '%d' % int(word)  , True, color['white'])
        text_big = font_big.render(time, True, color['white'])
        text_small_bottom = font_small.render('Viimane trummel oli ahjus ''%d'' tundi' % timer_total_minutes, True, color['white'])
        if timer_setpoint_minutes and start:
            text_small_top = font_small.render('Etteantud aeg ''%d'' ' % int(timer_setpoint_minutes), True, color['white'])

    # Set text sizes
    # Main textbox
    text_box_big = text_big.get_rect(center=(width / 2, (height + height) / 5))
    lcd.blit(text_big, text_box_big)

    # Subbox
    text_box_small = text_small_bottom.get_rect(center=(width / 2, (height - height / 10)))
    lcd.blit(text_small_bottom, text_box_small)

    # Small box on top
    text_box_small = text_small_bottom.get_rect(center=(width / 2, (height / 10)))
    lcd.blit(text_small_top, text_box_small)

    pygame.display.update()
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
