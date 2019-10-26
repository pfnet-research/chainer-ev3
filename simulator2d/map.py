import math
import numpy as np
import cv2

import settings
from geometry.point import polarvec, Point


class EV3Map:
    def __init__(self):
        self.settings = settings.SettingsRegistry['global']
        self.image = cv2.imread(self.settings.load_map)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY)
        offset = self.settings.camera_shadow_offset
        self.gray[self.gray < offset] = 0
        self.gray[self.gray >= offset] -= offset
        self.image_w = self.image.shape[1]
        self.image_h = self.image.shape[0]
        self.world_w = self.settings.world_w
        self.world_h = self.settings.world_h
        self.calib_w2i = Point(self.image_w / self.world_w,
                               self.image_h / self.world_h)
        self.calib_i2w = Point(self.world_w / self.image_w,
                               self.world_h / self.image_h)

    def _world2image(self, p):
        return (int(p.x * self.calib_w2i.x),
                int(p.y * self.calib_w2i.y))

    def image2world(self, image_x, image_y):
        return Point(image_x * self.calib_i2w.x,
                     image_y * self.calib_i2w.y)

    def get_circle(self, world_center, world_radius, angle):
        center = self._world2image(world_center)
        radius = int(world_radius * self.calib_w2i.x)
        patch_size = (radius * 2, radius * 2)
        patch = cv2.getRectSubPix(self.gray, patch_size, center)
        return patch

    def get_rectangle(self, world_center, camera_w, camera_h, angle):
        center = self._world2image(world_center)
        patch_w = int(camera_w * self.calib_w2i.x)
        patch_h = int(camera_h * self.calib_w2i.y)
        angle_degree = math.degrees(angle)
        patch_size = (patch_w, patch_h)
        m = cv2.getRotationMatrix2D(center, angle_degree + 90., 1.)
        dst = cv2.warpAffine(self.gray, m, (self.image_w, self.image_h), flags=cv2.INTER_LINEAR)
        patch = cv2.getRectSubPix(dst, patch_size, center)
        return patch
