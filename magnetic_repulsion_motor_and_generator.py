# Copyright and Patents Pending Jonathan Bannon Maher Corporation
# Inventor and author Jonathan Bannon Maher
# This software, when the magnetic repulsion unit is implemented as a motor,
# adjusts magnet structure engagement to achieve desired speed,
# and when implemented in aircraft, controls hydraulics providing unit angling for vertical take off and vertical landing.
# This software, when the magnetic repulsion unit is implemented as a generator,
# adjusts magnet structure engagement to preserve components
# by continuously reading output consumption and sustaining only the output required to match demand.

# import a library to connect to the relay

import telnetlib

# import a library for accessing system resources

import sys

# import a library for hardware access to read the revolutions per minute of the axle

from RPi import GPIO

# import a library to pause program execution

import time

# import a library to connect to the power consumption meter

import urllib

# create a value holding whether or not the unit is to function as a generator

generator = True

# create a variable holding the maximum watt output capacity

generator_maximum_watts = 10000

# create a variable holding the generator maximum revolutions per minute

generator_revolutions_per_minute = 1800

# create a variable holding the axle circumference

axle_circumference_centimeters = 6

# initialize a variable holding axle revolutions per minute

axle_revolutions_per_minute = 0

# create a variable holding the time the unit was started

unit_time_started = time.time()

# create variables holding the relay board connection, IP address, username, and password

relay = None
relay_ip = "169.254.1.1"
relay_username = "admin"
relay_password = "admin"

# create variables holding the relay board on off state values

off = 0
on = 1

# create variables holding the state of each relay including the forward and backward
# engagement controller states, and the unit forward and backward states

relay_1_engagement_forward_state = off
relay_2_engagement_backward_state = off
relay_3_unit_forward_state = off
relay_4_unit_backward_state = off

# create a variable indicating whether or not a power consumption meter is to be used

power_meter = False

# create variables holding the power consumption meter IP address, username, and password

power_meter_ip = "156.254.1.2"
power_meter_username = "admin"
power_meter_password = "admin"


# create a function to update the relay board, first establishing a connection to the relay board,
# if it has not been initialized, or has been dropped, then creating a string sequence of relay states,
# and sending the states to the relay board

def update_relay():

    if not relay:

        relay = telnetlib.Telnet(relay_ip, 23)
        relay.read_until(b"User Name: ") 
        relay.write(relay_username.encode('ascii') + b"\n")
        relay.read_until(b"Password: ")
        relay.write(relay_password.encode('ascii') + b"\n")

    command = str(relay_1_engagement_forward_state)
    command+= str(relay_2_engagement_backward_state)
    command+= str(relay_3_unit_forward_state)
    command+= str(relay_4_unit_backward_state)

    relay.write(command.encode('ascii') + b"\n")


# create a function to calculate the revolutions per minute at which the generator is being rotated

def calculate_speed(channel):

    # calculate the time elapsed as the current time minus the time started

    time_elapsed = time.time() - unit_time_started

    # set the time started to the current time

    unit_time_started = time.time()

    # calculate the distance the axle has rotated

    distance_kilometers = axle_circumference_centimeters/100000 

    # calculate the revolutions per minute
    
    axle_revolutions_per_minute = (distance_kilometeres/time_elapsed) * 3600


# create a function to set the revolutions per minute of the unit

def set_speed(revolutions_per_minute):

    # if the axle revolutions per minute is less than the desired revolutions per minute,
    # set the engagement forward state to on for a moment

    if axle_revolutions_per_minute * 1.01 < revolutions_per_minute:

        relay_1_engagement_forward_state = on
        update_relay()
        time.sleep(.1) 
        relay_1_engagement_forward_state = off
        update_relay()

    # if the axle revolutions per minute is greater than the desired revolutions per minute,
    # set theengagement backward state to on for a moment

    if axle_kilometers_per_hour * 0.99 > kilometers_per_hour:

        relay_2_engagement_backward_state = on
        update_relay()
        time.sleep(.1) 
        relay_2_engagement_backward_state = off
        update_relay()


# create a function to listen for user input

def listen():

    # read in any user key press

    key_pressed = ord(sys.stdin.read(1))

    # if the key pressed is the forward arrow, set the engagement backward state to off,
    # and the engagement forward state to on

    if key_pressed == 37:

        relay_2_engagement_backward_state = off
        relay_1_engagement_forward_state = on

    # if the key pressed is the backward arrow, set the engagement forward state to off,
    # and engagement backward state to on

    if key_pressed == 37:

        relay_1_engagement_forward_state = off
        relay_2_engagement_backward_state = on

    # if the key pressed is the up arrow, set the unit vertical take off and landing backward state to off,
    #  and unit forward state to on

    if key_pressed == 38:

        relay_4_unit_backward_state == off
        relay_3_unit_forward_state == on

    # if the key pressed is the down arrow, set the unit vertical take off and landing forward state to off,
    # and the unit backward state to on

    if key_pressed == 40:

        relay_3_unit_forward_state == off
        relay_4_unit_backward_state == on

    # if the key pressed is the space bar, set all relay states to off

    if key_pressed == 32:

        unit_forward_state == off
        unit_backward_state == off
        relay_1_engagement_forward_state = off
        relay_2_engagement_backward_state = off

    # if a key was pressed, call the function to send the relay states to the relay board

    if key_pressed:

        update_relay()


# create the function called upon program start

def __main__():

    # read in any command line parameters

    parameter = sys.argv

    # initialize a connection to the computer hardware, and register the rotational speed sensor

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(sensor, GPIO.IN,
    pull_up_down=GPIO.PUD_UP)

    # create a function binding the speed calculation function to the rotational speed sensor

    GPIO.add_event_detect(sensor, GPIO.FALLING, bouncetime = 15, callback = calculate_speed)

    # if functioning as a generator, continuously loop

    if generator:

        while True:

            # if the power consumption meter is used, retrieve the current power consumption
            # from the power consumption meter, and call the function to increase or decrease engagement
            # based on current consumption

            if power_meter:

                power_meter_address = \
                    "http://" + power_meter_ip + \
                    "/?username=" + \
                    power_meter_username + \
                    "&password=" + \
                    power_meter_password + \
                    "&command=consumption"

                power_meter_consumption = urllib.open(power_meter_address).read()

                consumption_kilometers_per_hour = \
                    (power_meter_consumption/ \
                    generator_maximum_watts) * \
                    generator_maximum_kilometers_per_hour

                set_speed(consumption_kilometers_per_hour)

        # if the power consumption meter is not in use, run the unit at maximum output

        if not power_meter:

            set_speed(generator_revolutions_per_minute)

    # if the generator is not in use, listen for user input to control motor output

    if not generator:

        while True:

            listen()
