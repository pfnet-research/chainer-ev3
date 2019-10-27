import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%s,%s)" % (self.x, self.y)

    def __add__(lhs, rhs):
        return Point(lhs.x + rhs.x,
                     lhs.y + rhs.y)

    def __sub__(lhs, rhs):
        return Point(lhs.x - rhs.x,
                     lhs.y - rhs.y)

    def __mul__(lhs, rhs):
        if not isinstance(lhs, Point):
            lhs, rhs = rhs, lhs
        return Point(lhs.x * rhs,
                     lhs.y * rhs)

    def __div__(lhs, rhs):
         return Point(lhs.x / rhs,
                     lhs.y / rhs)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __abs__(self):
        return math.sqrt(self.x * self.x + self.y * self.y)


def polarvec(len, angle):
    return Point(len * math.cos(angle),
                 len * math.sin(angle))


