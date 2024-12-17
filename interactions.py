import math

def distance(obj1, obj2):
    x = obj1.position[0] - obj2.position[0]
    y = obj1.position[1] - obj2.position[1]

    return math.sqrt(x**2 + y**2)

