import unittest
import math

from libc cimport math

cdef class Point:
    cdef:
        public double x, y

    def __init__(self, double x, double y):
        self.x = x
        self.y = y

    cpdef astuple(self):
        return (self.x, self.y)

    def __repr__(self):
        return "Point(%s,%s)" % (self.x, self.y)

    def __add__(Point lhs, Point rhs):
        return Point(lhs.x + rhs.x,
                     lhs.y + rhs.y)

    def __sub__(Point lhs, Point rhs):
        return Point(lhs.x - rhs.x,
                     lhs.y - rhs.y)

    def __mul__(lhs, rhs):
        if not isinstance(lhs, Point):
            lhs, rhs = rhs, lhs
        return Point(lhs.x * rhs,
                     lhs.y * rhs)

    def __div__(Point lhs, double rhs):
        # x/y can be integers, but what we expect is not integer division
        return Point(lhs.x / rhs,
                     lhs.y / rhs)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __abs__(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def __richcmp__(Point lhs, Point rhs, int op):
        if op == 2:
            return lhs.x == rhs.x and lhs.y == rhs.y
        elif op == 3:
            return not (lhs.x == rhs.x and lhs.y == rhs.y)
        return NotImplemented

    def __reduce__(self):
        # This method is needed for Point to be deepcopied
        return (lambda x, y: Point(x, y), (self.x, self.y))

cpdef double abs_opt(Point self) except *:
    return math.sqrt(self.x * self.x + self.y * self.y)

cpdef double dot(Point p1, Point p2) except *:
    return p1.x * p2.x + p1.y * p2.y

cpdef double cross(Point p1, Point p2) except *:
    return p1.x * p2.y - p1.y * p2.x

cdef double cross_opt(double p1x, double p1y, double p2x, double p2y):
    return p1x * p2y - p1y * p2x

cpdef double ccw(Point p1, Point p2, Point p3) except *:
    return cross(p2 - p1, p3 - p1)

cdef double ccw_opt(double p1x, double p1y, double p2x, double p2y, double p3x, double p3y):
    cdef double tmp1x, tmp1y, tmp2x, tmp2y
    tmp1x = p2x - p1x
    tmp1y = p2y - p1y
    tmp2x = p3x - p1x
    tmp2y = p3y - p1y
    return tmp1x * tmp2y - tmp1y * tmp2x

def intersection_point(s, t):
    cdef Point s0, s1, t0, t1, sv, tv
    s0, s1 = s
    t0, t1 = t
    sv = s1 - s0
    tv = t1 - t0
    return s0 + sv * (cross(tv, t0 - s0) / cross(tv, sv))

cpdef intersection_point_opt(s, t):
    cdef Point s0, s1, t0, t1
    cdef double scale, tmp1x, tmp1y, tmp2x, tmp2y
    s0, s1 = s
    t0, t1 = t
    tmp1x = s1.x - s0.x
    tmp1y = s1.y - s0.y
    tmp2x = t1.x - t0.x
    tmp2y = t1.y - t0.y
    scale = cross_opt(tmp2x, tmp2y, t0.x - s0.x, t0.y - s0.y) / cross_opt(tmp2x, tmp2y, tmp1x, tmp1y)
    return Point(s0.x + tmp1x * scale,
                 s0.y + tmp1y * scale)

cpdef check_segment_intersection(s, t):
    cdef Point s0, s1, t0, t1
    s0, s1 = s
    t0, t1 = t
    return ((ccw(s0, s1, t0) > 0) != (ccw(s0, s1, t1) > 0)
        and (ccw(t0, t1, s0) > 0) != (ccw(t0, t1, s1) > 0))

cpdef check_segment_intersection_opt(s, t):
    cdef Point s0, s1, t0, t1
    s0, s1 = s
    t0, t1 = t
    return ((ccw_opt(s0.x, s0.y, s1.x, s1.y, t0.x, t0.y) > 0) !=
            (ccw_opt(s0.x, s0.y, s1.x, s1.y, t1.x, t1.y) > 0)
        and (ccw_opt(t0.x, t0.y, t1.x, t1.y, s0.x, s0.y) > 0) !=
            (ccw_opt(t0.x, t0.y, t1.x, t1.y, s1.x, s1.y) > 0))

cpdef polarvec(double len, double angle):
    return Point(len * math.cos(angle),
                 len * math.sin(angle))

cpdef arg(l):
    '''Return a signed angle between x-axis (positive direction
    and vector (l[0], l[1]). The value is between (-pi, +pi).'''
    p = l[1] - l[0]
    return math.atan2(p.y, p.x)

def undirected_arg(l1, l2):
    ret = abs(arg(l1) - arg(l2))
    if ret >= math.pi:
        ret = 2 * math.pi - ret
    if ret >= math.pi / 2:
        ret = math.pi - ret
    return ret

cpdef double arg_opt(l):
    '''Return a signed angle between x-axis (positive direction
    and vector (l[0], l[1]). The value is between (-pi, +pi).'''
    cdef double x, y
    cdef Point l0, l1
    l0, l1 = l
    x = l1.x - l0.x
    y = l1.y - l0.y
    return math.atan2(y, x)

cpdef undirected_arg_opt(l1, l2):
    cdef double ret
    ret = abs(arg_opt(l1) - arg_opt(l2))
    if ret >= math.M_PI:
        ret = 2 * math.M_PI - ret
    if ret >= math.M_PI / 2:
        ret = math.M_PI - ret
    return ret

def normalize(angle):
    mod = 2 * math.pi
    return math.fmod(math.fmod(angle, mod) + mod, mod)

def compute_angle(segment):
    """Compute the angle of a segment

    Returns:
      angle (double) in [-pi, pi]
    """
    pt_from, pt_to = segment
    v = pt_to - pt_from
    return math.atan2(v.y, v.x)

def compute_angle_distance(x, y):
    """Compute the distance between two angles in (-pi, pi]
    """
    return abs(pipi(x - y))

cpdef pipi(double angle):
    """Fit a given angle in (-pi, pi]
    """
    while angle <= -math.pi:
        angle += 2 * math.pi
    while angle > math.pi:
        angle -= 2 * math.pi
    return angle

def perpendicular_foot(p, segment):
    """Compute a perpendicular foot

    If the perpendicular foot is outside the segment, this function returns
    the nerest end point of the segment.
    """
    cdef Point segment_vec
    cdef double segment_len
    segment_vec = segment[1] - segment[0]
    segment_len = abs(segment_vec)
    segment_unit_vec = Point(segment_vec.x / segment_len,
    		             segment_vec.y / segment_len)
    l = dot(p - segment[0], segment_unit_vec)
    if l < 0:
        return segment[0]
    elif l > segment_len:
        return segment[1]
    else:
        return segment[0] + l * segment_unit_vec

def point_segment_distance(p, segment):
    foot = perpendicular_foot(p, segment)
    return abs(foot - p)


class TestPoint(unittest.TestCase):

    def _almost_equal_points(self, p, q):
        self.assertAlmostEqual(p.x, q.x)
        self.assertAlmostEqual(p.y, q.y)


    def test_intersection_point(self):
        s = [Point(0, 0), Point(1, 1)]
        t = [Point(1, 0), Point(0, 1)]
        p = intersection_point(s, t)

    def test_functions(self):
        o = Point(0, 0)
        ps = [[o, Point(1, 0)],
              [o, Point(0, 1)],
              [o, Point(-1, 1)],
              [o, Point(1, -1)]]
        self.assertAlmostEqual(arg(ps[0]), 0)
        self.assertAlmostEqual(arg(ps[1]), math.pi / 2)
        self.assertAlmostEqual(arg(ps[2]), 3 * math.pi / 4)
        self.assertAlmostEqual(arg(ps[3]), -math.pi / 4)

        self.assertAlmostEqual(undirected_arg(ps[0], ps[1]), math.pi / 2)
        self.assertAlmostEqual(undirected_arg(ps[1], ps[2]), math.pi / 4)
        self.assertAlmostEqual(undirected_arg(ps[2], ps[3]), 0)
        self.assertAlmostEqual(undirected_arg(ps[3], ps[2]), 0)

        self.assertAlmostEqual(normalize( 100 * math.pi + 0.1234), 0.1234)
        self.assertAlmostEqual(normalize(-100 * math.pi + 0.1234), 0.1234)

    def test_perpendicular_foot(self):
        # left-top to right-bottom
        segment = [Point(-1.0, 1.0), Point(1.0, -1.0)]

        def check_left_bottom_pt():
            pt = Point(-0.5, -0.5)
            self._almost_equal_points(perpendicular_foot(pt, segment),
                                      Point(0.0, 0.0))

        def check_right_top_pt():
            pt = Point(0.6, 0.6)
            self._almost_equal_points(perpendicular_foot(pt, segment),
                                      Point(0.0, 0.0))
        def check_on_segment():
            pt = Point(-0.1, 0.1)
            self._almost_equal_points(perpendicular_foot(pt, segment),
                                      pt)
        def check_before_start_point():
            pt = Point(-3, 0)
            self._almost_equal_points(perpendicular_foot(pt, segment),
                                      segment[0])
        def check_after_end_point():
            pt = Point(3, 0)
            self._almost_equal_points(perpendicular_foot(pt, segment),
                                      segment[1])

        check_left_bottom_pt()
        check_right_top_pt()
        check_on_segment()
        check_before_start_point()
        check_after_end_point()

if __name__ == '__main__':
    unittest.main()
