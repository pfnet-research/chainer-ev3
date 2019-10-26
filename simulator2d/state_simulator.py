import math
import datetime as dt

import settings
from geometry.point import Point, polarvec


def linear_map(x, start1, stop1, start2, stop2):
    """
    Linearly map x from [start1, stop1] to [start2, stop2]
    Equivalent to Processing's map function. If x is outside [star1, stop1], it
    will be extrapolated linearly.
    """
    scale = float((stop2 - start2)) / (stop1 - start1)
    return (x - start1) * scale + start2


class EV3StateSimulator:
    def __init__(self):
        self.settings = settings.SettingsRegistry['global']
        self.logger = self.settings.logger
        self.pos = Point(self.settings.ini_car_x,
                         self.settings.ini_car_y)
        self.angle = self.settings.ini_car_angle
        self.color_offset = self.settings.color_sensor_offset
        self.color_radius = self.settings.color_sensor_radius
        self.color_pos = self._compute_color_pos()
        self.camera_offset = self.settings.camera_offset
        self.camera_pos = self._compute_camera_pos()

    def _compute_camera_pos(self):
        return polarvec(self.camera_offset, self.angle) + self.pos

    def _compute_color_pos(self):
        return polarvec(self.color_offset, self.angle) + self.pos

    def _compute_velocity(self, command, d=0.02, v=5.0):
        """
        Compute the resulting velocity[m/s] for a given command
        @d, @v: Some parameters for simulation.
        """
        drive_normalized = d * command['drive'] / 20.0
        steer_normalized = linear_map(abs(command['steer']), 0.0, 100.0, 1.0, 0.4)
        delta = v * drive_normalized * steer_normalized
        return polarvec(delta, self.angle)

    def _compute_angular_velocity(self, command, v=0.74, omega=1.0):
        """
        Compute the resulting angular velocity for a given command
        @v, @omega: Some parameters for simulation.
        """
        drive_diff = linear_map(
                abs(command['drive']), 0.0, 100.0, 1.0, 0.2) * command['drive']
        steer_diff = command['steer'] / 2000.0
        return v * omega * drive_diff * steer_diff

    def get_state(self):
        return {'x': self.pos.x,
                'y': self.pos.y,
                'angle': self.angle}

    def simulate_command(self, command, dt=0.1):
        velocity = self._compute_velocity(command, v=5.0)
        angular_velocity = self._compute_angular_velocity(command, omega=1)
        self.drive = command['drive']
        self.steer = command['steer']
        self.pos += velocity * dt
        self.angle += angular_velocity * dt
        self.color_pos = self._compute_color_pos()
        self.camera_pos = self._compute_camera_pos()
