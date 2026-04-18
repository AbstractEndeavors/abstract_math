from ..imports import *
def pi() -> float:
    return math.pi

def radius_from_circumference(circumference):
    return circumference/mul(2 , pi())

def radius_from_diameter(diameter):
    return div(diameter,2)    

def radius(radius=None,diameter=None,circumference=None):
    return radius or radius_from_diameter(diameter) or radius_from_circumference(circumference)
