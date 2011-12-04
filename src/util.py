import math

halfPi = math.pi / 2.0
pi = math.pi
twoPi = math.pi * 2

def vecAdd(vec1, vec2):
    """
    returns the elementwise sum of vec1 and vec2
    vec1 and vec2 must be the same length
    return type matches vec1
    vec1 must have a constructor that accepts a generator
    both vec1 and vec2 must support indexing
    """
    if not len(vec1) == len(vec2): raise Exception("Vectors not of the smame length")
    return type(vec1)(vec1[i] + vec2[i] for i in xrange(len(vec1)))

def shortestTurn(current, desired):
    '''
    return: the least number of radians (+ or -) needed
    to get from current angle to desired angle (ie is it faster
    to turn left or turn right?)
    '''
    delta = desired - current
    if delta > pi:
        delta = -twoPi + delta
    elif delta < -pi:
        delta = twoPi + delta
    return delta

def normalizeAngle(angle):
    '''
    return: angle between 2pi and -2pi
    '''
    return angle - (int(angle / (twoPi)) * twoPi)

def normalizePositiveAngle(angle):
    '''
    return: angle between 0 and 2pi
    '''
    n = normalizeAngle(angle)
    if n < 0: n = twoPi - abs(n)
    return n

def curveValue(current, target, smooth):
    '''
    Proportionally interpolate current towards
    '''
    return current + (target - current) / smooth

def distance(pt1, pt2):
    '''
    return: the distance between pt1 and pt2
    '''
    return math.sqrt((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

def distance2(pt1, pt2):
    '''
    return: the distance**2 between pt1 and pt2
    faster than distance above, use for comparisons
    '''
    return ((pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2)

def slope(pt1, pt2):
    '''
    return: the slope between pt1 and pt2 or inf for vertical lines
    '''
    if pt1[0] - pt2[0] == 0: return float('inf')
    return (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])

def getAngle(pt1, pt2):
    '''
    return: the angle between the line segment from pt1 --> pt2 and the x axis, from -pi to pi
    '''
    xcomp = pt2[0] - pt1[0]
    ycomp = pt1[1] - pt2[1]
    return math.atan2(ycomp, xcomp)

def movePt(pt, vec):
    '''
    moves a point by a vector
    '''
    x, y = pt
    mx, my = vec
    x += mx
    y += my
    return x, y

def midPt(pt1, pt2):
    '''
    return: the midpoint of the line segment from pt1 --> pt2 
    '''
    return ((pt1[0] + pt2[0]) / 2.0, (pt1[1] + pt2[1]) / 2.0)

def constructTriangleFromLine(pt1, pt2):
    '''
    return: a list of ordered pairs that describe an equilteral triangle around the segment from pt1 --> pt2
    '''

    halfHeightVector = (0.57735 * (pt2[1] - pt1[1]), 0.57735 * (pt2[0] - pt1[0]))
    pt3 = (pt1[0] + halfHeightVector[0], pt1[1] - halfHeightVector[1])
    pt4 = (pt1[0] - halfHeightVector[0], pt1[1] + halfHeightVector[1])
    return [pt2, pt3, pt4]

def polyArea(vertices):
    '''
    return: the area of the polygon described by vertices
    '''
    n = len(vertices)
    A = 0
    p = n - 1
    q = 0
    while q < n:
        A += vertices[p][0] * vertices[q][1] - vertices[q][0] * vertices[p][1]
        p = q
        q += 1
    return A / 2.0

def ceilVec(vec, ceil):
    '''
    return: vec if the magnitude of vec is < ceil,
    otherwise vec scaled to have magnitude ceil
    '''
    x, y = vec
    mag = math.sqrt(x ** 2 + y ** 2)
    if mag > ceil:
        x *= (ceil / mag)
        y *= (ceil / mag)
    return (x, y)

def scaleVec(vec, mag):
    '''
    return: vec scaled to have magnitude mag
    '''
    x, y = vec
    if x == 0 and y == 0: return vec
    cmag = math.sqrt(x ** 2 + y ** 2)
    r = mag / cmag
    x *= r
    y *= r
    return (x, y)
