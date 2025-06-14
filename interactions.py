import math

import pygame
import pymunk

def distance_squared(obj1, obj2):
    dx = obj1.position[0] - obj2.position[0]
    dy = obj1.position[1] - obj2.position[1]
    return dx * dx + dy * dy

