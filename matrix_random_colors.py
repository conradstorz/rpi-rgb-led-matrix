#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" expose methods of setting random colors on the RaspberryPi connected NeoPixel matrix
"""

# ___ REMOVE ___ from itertools import product
from random import choice, shuffle
from time import sleep
import json

USE_RPI_OUTPUT = True # set if using RPi to drive NeoPixels directly
if USE_RPI_OUTPUT == True:
    import board
    import neopixel
    # Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18 NeoPixels must be connected to 
    # D10, D12, D18 or D21 to work.
    pixel_pin = board.D18
    # The number of NeoPixels
    num_pixels = 256
    # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed! For RGBW NeoPixels, simply 
    # change the ORDER to RGBW or GRBW.
    ORDER = neopixel.RGB
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.02, auto_write=False, 
                            pixel_order=ORDER)

# detect various add-on Rpi hats
try:
    SenseHatLoaded = True
    from sense_hat import SenseHat
    senseObj = SenseHat()
except ImportError as e:
    SenseHatLoaded = False

# Load color codes
with open("rgb_color_codes.json", "r") as read_file:
    color_dict = json.load(read_file)

COLOR_KEYS = list(color_dict.keys())

x_index = list(range(32)) # establish a default index for 32x8 pixel display
y_index = list(range(8)) # establish a default index for 32x8 pixel display


def Set_Random_Pixels(senseObj=None, x=x_index, y=y_index, pace=1, rounds=99):
    """ Fill display with random pixel colors.
    Params: senseObj = senseHat Object pointer (required)
    Optional: ,x,y list of valid index values (zero based) (size of area to display)
    Optional: ,pace >0<=1 (speed of change, 1=fastest)
    Optional: ,rounds >=1 (number of times each pixel will change on average)
    """
    # TODO range check x,y, rounds and pace
    # TODO type check senseObj
    field = [int(rounds) for i in range(len(x) * len(y))]
    pxls = list(range(len(x) * len(y)))
    shuffle(pxls)  # scramble list    
    while len(pxls) > 0:
        color = choice(COLOR_KEYS)
        pxl = pxls.pop()
        xp = int(pxl / 8)
        yp = int(pxl % 8)        
        iters = field[xp * 8 + yp]
        field[xp * 8 + yp] = iters - 1
        if SenseHatLoaded == True:
            senseObj.set_pixel(xp, yp, color_dict[color]["rgb"])
        if USE_RPI_OUTPUT == True:
            pixels[xp * 8 + yp] = color_dict[color]["rgb"]
            pixels.show() 
        """
        delay = (pace / 10000000) * (sum(field) / rounds)
        if delay > 0:
            sleep(delay)
        else:
            sleep(pace / 10000000)
        """
    return color


def random_to_solid(senseObj=None, colorName="black", x=x_index, y=y_index, fast=False, flicker=True):
    """flicker controls if display should animate during color unifomity process 
    """
    if colorName not in color_dict.keys():
        raise ValueError
    # TODO range check x,y and fast
    if fast == True:
        field = list(range(len(x) * len(y)))
        shuffle(field)  # scramble list
        while len(field) > 0:
            pxl = field.pop()
            x = int(pxl / 8)
            y = int(pxl % 8)
            if USE_RPI_OUTPUT == True:
                pixels[x * 8 + y] = color_dict[colorName]["rgb"]
                pixels.show()         
            if SenseHatLoaded == True:                
                senseObj.set_pixel(x, y, color_dict[colorName]["rgb"])
            if flicker == True:
                for ndx in field:
                    x = int(ndx / 8)
                    y = int(ndx % 8)
                    if USE_RPI_OUTPUT == True:
                        pixels[x * 8 + y] = color_dict[choice(COLOR_KEYS)]["rgb"]
                        pixels.show()                    
                    if SenseHatLoaded == True:                
                        senseObj.set_pixel(x, y, color_dict[choice(COLOR_KEYS)]["rgb"])                                
            # sleep(len(field)/2*.01)
    else:
        field = [1 for i in range(len(x) * len(y))]
        while sum(field) > 0:
            pixel_x = choice(x)
            pixel_y = choice(y)
            pxl = pixel_x * 8 + pixel_y
            if field[pxl] != 0:
                field[pxl] = 0
                if USE_RPI_OUTPUT == True:
                    pixels[pixel_x * 8 + pixel_y] = color_dict[colorName]["rgb"]
                    pixels.show()      
                if SenseHatLoaded == True:                              
                    senseObj.set_pixel(pixel_x, pixel_y, color_dict[colorName]["rgb"])
            #sleep(0.1)
    return True


#@logger.catch
def DisplayMessage(message, senseObj=None, pause=1):
    """ Place a text string on the display of the SenseHat.
    Params: senseObj: required SenseHat Object, message: text string (required) 
    """
    # TODO range check inputs (example: pause must be >= 0)
    if SenseHatLoaded:
        # TODO trap exceptions
        senseObj.show_message(str(message))
        sleep(pause)
    return


def Main():
    print(f'Start random display')
    last = Set_Random_Pixels(rounds=1)
    print(f'Start solid display')
    random_to_solid(colorName=last, fast=True, flicker=False)
    print(f'Start second round of random display')
    last = Set_Random_Pixels(pace=.1, rounds=1)
    print(f'Start second round of solid display')   
    random_to_solid(fast=True, flicker=False)
    #sense.low_light = True
    #sense.clear(255, 255, 255)
    return


if __name__ == "__main__":
    Main()
