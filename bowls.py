import time
import board
import adafruit_nunchuk
import neopixel
import random
from Objects_and_functions import *



# initialise nunchuk
nc = adafruit_nunchuk.Nunchuk(board.I2C())

# pin for neopixels
pixel_pin = board.D6

# no of neopixels
num_pixels = 144

# brightness of strip
brightness = 0.2

# initialise strip
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=brightness, auto_write=False)

# set new target
Target = newTarget(pixels)

# initialise to hold z button and last state of zbutton
lastZ = 0
Z = 0
C = 0

players = []  # initialise list that holds players

# handles which mode we in, 'm' is menu 'g' is gamepad
mode = 'm'

no_of_players = 1  # starts with one player only

# different colours for player, white; green; blue; violet, cyan, yello
playerColours = [(255, 255, 255), (0, 255, 0), (0, 0, 255), (255, 0, 255), (255, 255, 0), (0, 255, 255)]

# add one player for now
tilted = False

score = []  # empty list to contain scores

turn = 0  # keep track whose turn it is

#  handle the reset
wantToReset = False
resetTime = 2  # hold for three seconds


n = 5
while True:
    # switch off all lights
    pixels.fill((0, 0, 0))
    # read nunchuk inputs
    x, y = nc.joystick
    lastZ = Z
    lastC = C
    Z = nc.button_Z
    C = nc.button_C

    if mode == 'm':
        # map analog stick
        analogY = valmap(y, 40, 180, -1, 1)

        if abs(analogY) > 0 and not tilted:
            no_of_players += analogY  # change no of players
            tilted = True

        if abs(analogY) == 0:
            tilted = False

        if no_of_players < 1:
            no_of_players = 1  # cant be less than one

        if no_of_players > len(playerColours):
            no_of_players = len(playerColours)  # cant be more than 6

        for i in range(no_of_players):
            # light up to show number of players
            for k in range(n):
                pixels[n*i+k] = playerColours[i]

        pixels.show()

        if C:
            players=[] # resets players
            turn = 0 # reset turns
            score = [] # initialise score
            Target = newTarget(pixels)
            C = 0  # so it doesn't mess anything up
            if no_of_players > 1:
                mode = 'g'  # change to game mode
                for i in range(no_of_players):
                    #  go through and add correct number of players
                    players.append(Bowler(num_pixels, playerColours[i]))
            else:
                mode = 'p'
                players = [Bowler(num_pixels, playerColours[i])]

    if mode == 'p':  # practice mode

        # handles resetting
        if Z and C:
            if not wantToReset:
                # if just pressed start timer
                wantToReset = True
                resetTimer = time.monotonic()
            else:
                if time.monotonic() - resetTimer > resetTime:
                    mode = 'm'
                    wantToReset = False
                    rainbow_cycle(0.001, pixels, num_pixels)

        if not (Z and C):
            wantToReset = False

        if C and not lastC:
            Target = newTarget(pixels)

        pixels.fill((0, 0, 0))

        pixels[Target] = (255, 0, 0)
        ax, ay, az = nc.acceleration

        players[0].throw(az, Z, lastZ)
        players[0].animateThrow(pixels, Target)

        if players[0].thrown:
            if players[0].distance < num_pixels:
                pixels[players[0].distance] = players[0].playerColour

        pixels.show()

    if mode == 'g':

        # handles resetting
        if Z and C:
            if not wantToReset:
                # if just pressed start timer
                wantToReset = True
                resetTimer = time.monotonic()
            else:
                if time.monotonic() - resetTimer > resetTime:
                    mode = 'm'
                    wantToReset = False
                    rainbow_cycle(0.001, pixels, num_pixels)

        if not (Z and C):
            wantToReset = False

        pixels[Target] = (255, 0, 0)
        ax, ay, az = nc.acceleration
#         if C and not lastC:
#             players[turn].thrown = False
#             Target = newTarget(pixels)

        # handles throwing and animation
        players[turn].throw(az, Z, lastZ)
        players[turn].animateThrow(pixels, Target)
        # handles moving to next player
        if players[turn].thrown:  # if player has thrown
            # store score
            if players[turn].out:
                # if you through out get max score
                score.append(144)
            else:
                score.append(abs(Target - players[turn].distance))
            if turn < no_of_players - 1:
                # if not all players gone move onto next player
                turn += 1
            else:
                # all players done so show results
                rainbow_cycle(0.001, pixels, num_pixels)
                showResults(score, playerColours, num_pixels, pixels)
                mode = 'r'
                continue

        for i in range(no_of_players):
            # if bowl thrown then show it
            if players[i].thrown and not players[i].out :
                pixels[int(players[i].pos)] = playerColours[i]

        if not players[turn].thrown:
            # shows whose turn it is on first pixel
            pixels[2] = playerColours[turn]

        pixels.show()


    if mode == 'r':
        pixels.fill((0, 0, 0))

         # handles resetting
        if Z and C:
            if not wantToReset:
                # if just pressed start timer
                wantToReset = True
                resetTimer = time.monotonic()
            else:
                if time.monotonic() - resetTimer > resetTime:
                    mode = 'm'
                    wantToReset = False
                    rainbow_cycle(0.001, pixels, num_pixels)

        if not (Z and C):
            wantToReset = False

        # show  target and players

        pixels[Target] = (255, 0, 0)

        for i in range(no_of_players):
            if players[i].distance < num_pixels:
                pixels[players[i].distance] = playerColours[i]

        pixels.show()
