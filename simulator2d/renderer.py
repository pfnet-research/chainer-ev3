from point import polarvec, Point
import math
import numpy as np
import cv2

import settings


def cv_arrow(img, pt1, pt2, color=(64,64,255), thickness=2, lineType=8, shift=0):
    """Draw arrow from pt1 to pt2"""
    cv2.line(img,pt1,pt2,color,thickness,lineType,shift)
    vx = pt2[0] - pt1[0]
    vy = pt2[1] - pt1[1]
    v  = math.sqrt(vx ** 2 + vy ** 2)
    ux = vx / v
    uy = vy / v
    w = 5
    h = 10
    ptl = (int(pt2[0] - uy*w - ux*h), int(pt2[1] + ux*w - uy*h))
    ptr = (int(pt2[0] + uy*w - ux*h), int(pt2[1] - ux*w - uy*h))
    cv2.line(img, pt2, ptl, color, thickness, lineType, shift)
    cv2.line(img, pt2, ptr, color, thickness, lineType, shift)


def corner_points(w, l, pos, angle):
    vecs = [polarvec(l / 2.0, angle),
            polarvec(w / 2.0, angle + math.pi * 0.5),
            polarvec(l / 2.0, angle + math.pi * 1.0),
            polarvec(w / 2.0, angle + math.pi * 1.5)]
    ret = []
    for i in range(4):
        ret.append(vecs[i] + vecs[(i + 1) % 4] + pos)
    return ret


class Renderer:
    def __init__(self, write_movie=False):
        self.settings = settings.SettingsRegistry['global']
        self.canvas_w = self.settings.canvas_w
        self.canvas_h = self.settings.canvas_h
        self.canvas_camera_w = self.settings.canvas_camera_w
        self.canvas_camera_h = self.settings.canvas_camera_h
        self.scale_w = self.canvas_w / self.settings.world_w
        self.scale_h = self.canvas_h / self.settings.world_h
        self.car_w = self.settings.car_w
        self.car_h = self.settings.car_h
        self.color_offset = self.settings.color_sensor_offset
        self.color_radius = self.settings.color_sensor_radius
        self.ev3_img = cv2.imread('./ev3.png')
        self.ev3_img = cv2.resize(self.ev3_img, (65, 85))
#         fourcc = cv2.VideoWriter_fourcc(*'X264')
#         self.vw = cv2.VideoWriter(
#             '{}_vl_out.avi'.format('test'),
#             fourcc,
#             10, (self.canvas_w, self.canvas_h))

    def cvt(self, wx, wy):
        cx = int(wx * self.scale_w)
        cy = int(wy * self.scale_h)
        return (cx, cy)

    def cvtp(self, wp):
        return self.cvt(wp.x, wp.y)

    def draw_ev3(self, canvas, state, color=(255,0,0), thickness=4):
        pos = state.pos
        angle = state.angle
        angle_degree = -(angle * 180. / math.pi + 90.)
        apexes = corner_points(self.car_w, self.car_h, pos, angle)
        center = (int(self.ev3_img.shape[1] / 2.), int(self.ev3_img.shape[0] / 2.))
        mat = cv2.getRotationMatrix2D(center, angle_degree, 1.0)
        mat[0,2] = self.cvtp(apexes[3])[0] - 40 * math.cos(angle)
        mat[1,2] = self.cvtp(apexes[3])[1] - 40 * math.sin(angle)
        h, w, c = canvas.shape
        cv2.warpAffine(self.ev3_img, mat, (w, h), borderMode=cv2.BORDER_TRANSPARENT, dst=canvas)
#         for i in range(len(apexes)):
#             cv2.line(canvas, self.cvt(apexes[i].x, apexes[i].y),
#                      self.cvt(apexes[(i+1)%len(apexes)].x, apexes[(i+1)%len(apexes)].y),
#                      color=color, thickness=thickness)

    def draw_color_sensor(self, canvas, state, color=(0,255,0), thickness=2):
        color_pos = state.color_pos
        cv2.circle(canvas, self.cvt(color_pos.x, color_pos.y),
                   int(self.color_radius * self.scale_w), color, thickness)

    def draw_camera_frame(self, canvas, raw_camera_frame):
        if raw_camera_frame is None:
            return
        camera_frame = cv2.resize(raw_camera_frame, 
                                  (self.canvas_camera_w, self.canvas_camera_h))
        bgr_frame = cv2.cvtColor(camera_frame, cv2.COLOR_GRAY2RGB)
        canvas[0:bgr_frame.shape[0], 0:bgr_frame.shape[1], :] = bgr_frame
        cv2.rectangle(canvas, (0, 0), (int(bgr_frame.shape[1]), int(bgr_frame.shape[0])),
                      (0, 0, 255), 1)

    def draw_camera_range(self, canvas, pos, width, height, angle,
                          color=(0,0,255), thickness=1):
        apexes = corner_points(width, height, pos, angle)
        n = len(apexes)
        for i in range(n):
            cv2.line(canvas, self.cvt(apexes[i].x, apexes[i].y),
                     self.cvt(apexes[(i+1) % n].x, apexes[(i+1) % n].y),
                     color=color, thickness=thickness)

    def draw_lcd(self, canvas, lcd_messages, lcd_width, lcd_height, font_size,
                 bg_color=(170,170,170), thickness=1):
        lt = (canvas.shape[1] - lcd_width, canvas.shape[0] - lcd_height)
        rb = (canvas.shape[1], canvas.shape[0])
        cv2.rectangle(canvas, lt, rb, bg_color, -1)
        cv2.rectangle(canvas, lt, rb, (0, 0, 0), 1)
        for i in range(len(lcd_messages)):
            cv2.putText(canvas, lcd_messages[i], (lt[0] + 5, lt[1] + 15 * (i+1)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), thickness=1)

    def render_env(self, env):
        canvas = cv2.resize(env.ev3_map.image, (self.canvas_w, self.canvas_h))
        self.draw_ev3(canvas, env.ev3_state)
        self.draw_color_sensor(canvas, env.ev3_state)
        self.draw_camera_frame(canvas, env.read_camera())
        self.draw_camera_range(canvas,
                               env.ev3_state.camera_pos,
                               env.camera_range['w'],
                               env.camera_range['h'],
                               env.ev3_state.angle)
        self.draw_lcd(canvas, env.lcd_messages, 150, 80, 3)
        return canvas
