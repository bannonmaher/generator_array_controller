# Copyright and Patents Pending Jonathan Bannon Maher Corporation
# Inventor and author Jonathan Bannon Maher
# This software provides utility scale demand based control of an array of Bannon Maher self-powered generators,
# by connecting through TCP/IP to an on off relay and a power consumption meter on each unit


# import a library for accessing the relays

import telnetlib

# import a library for system resource access

import sys

# initialize and set variables holding relay on and off values

off = 0
on = 1

# create an array of IP addresses of unit on off relay boards

unit_ips = ["192.168.1.2", "192.168.1.3"]

# initialize an array of unit relay board connections 

relays = []
for unit_ip in unit_ips:
    relays.append(None)

# create an array of unit output watts

unit_watts = [10000, 10000]

# create an array of unit on off states

unit_states = [on, off]

# create variables holding the default unit relay board username and password

unit_username = "admin"
unit_password = "admin"

# create variables to hold the total watts available across all units, the current watts being consumed,
# and whether or not time based watts are to be used

watts_total = 0
watts_current = 1000000
time_watts = False

# create an array of pairs of times and time desired watts

times_watts = [["7:00", 1000000],["20:00",500000]]

# create a variable indicating whether or not unit power consumption meters are to be used

power_meter = True

# create and array of power consumption meter IP addresses

power_meter_ips = ["192.168.1.4","192.168.1.5"]

# create variables holding the power consumption meters username and password

power_meter_username = "admin"
power_meter_password = "admin"

# create variables holding the minimum and maximum power consumption to be allowed before switching units on or off

consumption_minimum = 0.5
consumption_maximum = 0.9

# create a function to send a command to a unit at a specified index in the unit IP address array

def send_command(unit_index, command):

    # create a connection to the unit on off relay board,
    # at the IP address at the provided index in the unit IP address array,
    # if the connection has not been initialized, or had been dropped

    if not relays[unit_index]:
        relays[unit_index] = telnetlib.Telnet(unit_ips[unit_index], 23)
        relays[unit_index].read_until(b"User Name: ") 
        relays[unit_index].write(unit_username.encode('ascii') + b"\n")
        relays[unit_index].read_until(b"Password: ")
        relays[unit_index].write(unit_password.encode('ascii') + b"\n")

    # create a variable holding the command string to be sent to the unit based on whether the unit is to be turned on or off

    command_string = "00"
    if command == on:
        command_string = "01"
    if command == off:
        command_string = "10"

    # send the command the the unit relay

    relays[unit_index].write(command_string.encode('ascii') + b"\n")

    # wait for the command to go through, then turn off all relays

    time.sleep(1)
    command_string = "00"
    relays[unit_index].write(command_string.encode('ascii') + b"\n")


# define a function to run on script execution

if __name__ == "__main__":

    # iterate through each unit IP address and call the function to switch the unit on

    index = 0
    for unit_ip in unit_ips:
        send_command(index, on)
        index += 1

    # run a continuous loop

    while True:

        # create variables to hold a unit index iterator, an output display message, and the current action

        index = 0
        message = ""
        action = None

        # proceed if power consumption meters are being used

        if power_meter:

            # create variables to hold average and total consumption of unit power, and add up total possible power output

            consumption_average = 0
            consumption_total = 0
            consumption_capacity = 0

            # loop through the each power consumption meter IP address
            while index < len(power_meter_ips):

                # retrieve the current power consumption number

                power_meter_address = "http://" + power_meter_ips[index] + \
                    "/?username=" + power_meter_username + \
                    "&password=" + power_meter_password + \
                    "&command=consumption"
                power_meter_consumption = urllib.open(power_meter_address).read()

                # calculate the average consumption

                consumption_average += power_meter_consumption/unit_watts

                # add the current consumption to the total

                consumption_total += power_meter_consumption

                # add the unit maximum capacity to the total consumption capacity

                consumption_capacity += unit_watts[index]

                # increment the index

                index = index + 1

            # calculate the consumption percentage as the consumption total divided by the total unit capacities

            consumption_percentage = consumption_total/consumption_capacity

            # create a message to display the states the currently consumed watts and the current watt capacity

            message = str(consumption_total) + " of " + str(consumption_capacity) + " watts consumed"

            # if the average consumption is greater than the maximum consumption level before more unit should be turned on,
            # then set the unit action equal to on

            if consumption_percentage > consumption_maximum:
                action = on

            # if the average consumption is less than the minimum consumption level before more unit should be turned off,
            # then set the unit action equal to off

            if consumption_average < consumption_minimum:
                action = off

            # iterate through unit states until one is found that is either off, if looking to turn a unit on,
            # or on if looking to turn a unit off, then send the command to switch the unit state

            index = 0
            unit_found = False
            if action:
                for unit_state in unit_states:
                    if not unit_found:
                        if (action == on and unit_state == off) or (action == off and unit_state == on):
                            send_command(index, action)
                            unit_found = True
                            unit_state[index] == "on"
                            state = "on"
                            if action == off: state = "off"
                            message += ", unit turned " + state
                        index += 1

        # proceed if power consumption meters are not used, and instead the total watts to be provided by the units
        # are determined by the current time

        if not power_meter:

            # iterate through each time watts pair, and if the current time is equal to the specified time,
            # send commands to turn units on or off, until the desired level of output is produced,
            # and display each action on the command line

            for time_watt in time_watts:
                if time == time_watt[0]:
                    desired_watts = time_watt[1]
                    transition_complete = False
                    index = 0
                    for unit_state in unit_states:
                        while not transition_complete:
                            if watts_current > time_watt[1]:
                                action = off
                                watts_current -= unit_watts
                                message = "unit turned off"
                            if watts_current < time_watt[1]:
                                action = on
                                watts_current += unit_watts
                                message = "unit turned on"
                            if (action == on and unit_state == off) or (action == off and unit_state == on):
                                send_command(index, action)
                                unit_state[index] == "on"
                                state = "on"
                                if action == off: state = "off"
                                message += ", unit turned " + state
                                index += 1
                            action = None
                            print message
                            message = ""

        # sleep for a moment before looping again

        time.sleep(1)
