
import time
import board
import adafruit_nunchuk
import neopixel
import random

class Bowler:
    def __init__(self, num_pixels, colour):
        """ needs number of leds on strip and player colour to initialise"""
        if colour is not tuple and len(colour) != 3:
            raise Exception("need a tuple of RGB values for colour")
        self.speed = 0
        self.max = 0
        self.thrown = False
        self.distance = 0
        self.slowestSpeed = 0.01  # slowest speed before stopping
        self.pos = 0
        self.startSpeed = 0
        self.num_pixels = num_pixels # number of leds in strip
        self.playerColour = colour # needs to be a tuple with RGB from 0 - 255
        self.out = False  # true if overthrown
        self.flash = False

    def Flash(self, no_of_flashes, aStrip):
        """ flashes for as many times as specified """
        if self.flash:
            on = 0
            for i in range(no_of_flashes * 2):
                time.sleep(0.5)
                if on:
                    aStrip[int(self.pos)] = self.playerColour
                else:
                    aStrip[int(self.pos) ] = (0, 0, 0)

                aStrip.show()
                on = (on + 1) % 2


        self.flash = False

    def maxAccZ(self, accelZ):
        """records highest z acceleration and stores in max"""
        if accelZ > self.max:
            if accelZ < 600:
                self.max = 600
            else:
                self.max = accelZ

    def throw(self, accelZ, zButton, lastZ):
        """ handles the throw, stores max accel z and how far the ball should go"""
        if not lastZ and zButton:
            # if z is pressed restart counter
            self.max = 0
            self.thrown = False
            self.out = False
            self.pos = 0

        if zButton:
            self.maxAccZ(accelZ)

        if lastZ and not zButton:
            # when z is let go say its thrown
            self.thrown = True  # mark that its thrown
            # calc how far the ball goes
            self.distance = valmap(self.max, 600, 1023, 0, self.num_pixels + 5)
            if self.distance > self.num_pixels - 1:
                self.out = True
            # give initial speed based on the throw
            self.speed = valmap(self.distance, 0, self.num_pixels - 1, 0.2, 3, False)

    def animateThrow(self, aStrip, aTarget):
        """ Animates throw of the ball, aStrip is the neopixel strip to animate"""
        if self.thrown:
            delay = 0.1
            iterations = 2*(self.distance - 5)/(self.speed + self.slowestSpeed) - 1
            increment = (self.speed - self.slowestSpeed)/iterations
            on = 0
            while self.pos <= self.distance :
                if self.pos < self.num_pixels:
                    if self.pos < self.distance - 5:
                        self.pos += self.speed  # moves ball
                        if self.speed - increment < self.slowestSpeed:
                            self.speed = self.slowestSpeed
                        else:
                            self.speed -= increment  # make wait longer
                    else:
                        # last five steps are handled separately to go slower
                        time.sleep(delay) # wait
                        self.pos += 1 # move
                        delay += 0.1 # increment delay
                        if not self.out:
                            self.flash = True
                    if self.pos < self.num_pixels:  # make sure within range
                        # shows strips
                        aStrip.fill((0, 0, 0))  # switch all lights off
                        aStrip[aTarget] = ((255, 0, 0))  # switches on target light red
                        aStrip[int(self.pos)] = (self.playerColour)  # shows bowl position
                        aStrip.show()
                else:
                    #  you over shot flash red
                    for i in range(6):
                        if on == 1:
                            aStrip.fill((255, 0, 0))
                        else:
                            aStrip.fill((0, 0, 0))

                        time.sleep(0.2)
                        on = (on + 1) % 2
                        aStrip.show()
                    self.pos = self.distance + 1
                #print("position: {} \t speed: {} \t increment: {} \t distance: {}".format(self.pos, self.speed, increment, self.distance))
            self.Flash(3, aStrip)


def valmap(x, in_min, in_max, out_min, out_max, integer=True):
    """ does the same as the map function in arduino
    if integer is true then maps to ints else returns float"""
    if integer:
        return int((x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min)
    else:
        return (x-in_min) * (out_max-out_min) / (in_max-in_min) + out_min

def averageAccZ(aZ, count, average):
    if aZ > 600:
        count += 1
        average = (average * (count - 1) + aZ)/count
    return count, average

def maxAccZ(aZ, Max):
    if aZ > Max:
        Max = aZ
    return Max


def animateThrow(index):
    speed = valmap(index, self.num_pixels - 1, 0, 0, 0.5, False)
    return speed

def newTarget(aStrip):
    """ sets new random target and lights it on strip"""
    Target = random.randrange(30, aStrip.n - 1)  # randomly choose target
    aStrip[Target] = ((255, 0, 0))
    aStrip.show()
    print('Target is {}'.format(Target))
    return Target

def showResults(score, playerColours, num_pixels, aStrip):
    # sorts scores
    rank = sorted(range(len(score)), key=lambda k: score[k])
    score = sorted(score)
    # stores winner
    winner =[rank[0]]
    # check if winner is shared
    for i in range(len(score)):
        if i == i + 1:
            # if same score then store as winner
            winner.append(rank[i+1])
        else:
            break

    l = int(num_pixels/len(winner))  # split strip to number of winners
    aStrip.fill((0, 0, 0))  # clear strip
    #  show winners on strip
    for i in range(len(winner)):
        for j in range(i*l,(i+1) * l):
            time.sleep(0.01)
            aStrip[j] = playerColours[winner[i]]
            aStrip.show()
    time.sleep(1)
    for i in range(len(score)):
        print("Player {} \t Score: {}".format(rank[i]+1, score[i]))

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

def rainbow_cycle(wait, aStrip, num_pixels):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            aStrip[i] = wheel(pixel_index & 255)
        aStrip.show()
        time.sleep(wait)


