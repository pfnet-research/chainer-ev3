import argparse
import numpy as np
import time
from datetime import datetime as dt
from threading import Thread
from PIL import Image

import settings
from renderer import Renderer
from map import EV3Map
from state_simulator import EV3StateSimulator


class EV3Env:
    def __init__(self):
        self.settings = settings.SettingsRegistry['global']
        self.ev3_map = EV3Map()
        self.ev3_state = EV3StateSimulator()
        self.simulation_speed = self.settings.simulation_speed_factor
        self.motor_command = {'drive': 0, 'steer': 0}
        self.camera_range = {'w': self.settings.camera_w,
                             'h': self.settings.camera_h}
        self.touch_sensor = {'is_pressed': False,
                             'pressed_time': -1.}
        self.enter_button = {'is_pressed': False,
                             'pressed_time': -1.}
        self.up_button = {'is_pressed': False,
                          'pressed_time': -1.}
        self.down_button = {'is_pressed': False,
                            'pressed_time': -1.}
        self.left_button = {'is_pressed': False,
                            'pressed_time': -1.}
        self.right_button = {'is_pressed': False,
                             'pressed_time': -1.}
        self.lcd_messages = {0: '',
                             1: '',
                             2: '',
                             3: '',
                             4: '',
                             5: '',
                             6: '',
                             7: ''}
        self.camera_view = None
        self.camera_settings = {'resolution': (64, 48),
                                'colormode': 'binary',
                                'bin_threshold': 50}
        self.last_updated_time = dt.now().timestamp()

    def step(self):
        current_time = dt.now().timestamp()
        step_time = (current_time - self.last_updated_time) * self.simulation_speed
        self.ev3_state.simulate_command(self.motor_command, step_time)
        self.camera_view = self.ev3_map.get_rectangle(self.ev3_state.camera_pos,
                                                      self.camera_range['w'],
                                                      self.camera_range['h'],
                                                      self.ev3_state.angle)
        if current_time - self.touch_sensor['pressed_time'] > 0.5:
            self.touch_sensor['is_pressed'] = False
        if current_time - self.up_button['pressed_time'] > 0.25:
            self.up_button['is_pressed'] = False
        if current_time - self.down_button['pressed_time'] > 0.25:
            self.down_button['is_pressed'] = False
        if current_time - self.left_button['pressed_time'] > 0.25:
            self.left_button['is_pressed'] = False
        if current_time - self.right_button['pressed_time'] > 0.25:
            self.right_button['is_pressed'] = False
        if current_time - self.enter_button['pressed_time'] > 0.25:
            self.enter_button['is_pressed'] = False

        self.last_updated_time = current_time
        time.sleep(0.01)

    def motor_config(self, motor_port, motor_type):
        ''' Dummy function '''
        return

    def motor_steer(self, l_motor_port, r_motor_port, drive, steer):
        self.motor_command['drive'] = min(100, max(-100, drive))
        self.motor_command['steer'] = min(100, max(-100, steer))

    def sensor_config(self, sensor_port, sensor_config):
        ''' Dummy function '''
        return

    def color_sensor_get_reflect(self, sensor_port):
        patch = self.ev3_map.get_circle(self.ev3_state.color_pos,
                                        self.ev3_state.color_radius,
                                        self.ev3_state.angle)
        patch = patch.flatten()
        return np.int(np.sum(patch / 255.) / patch.shape[0] * 100)

    def touch_sensor_is_pressed(self, sensor_port):
        return 1 if self.touch_sensor['is_pressed'] else 0

    def button_is_pressed(self, button_id):
        if button_id == 0:
            return 1 if self.right_button['is_pressed'] else 0
        elif button_id == 1:
            return 1 if self.left_button['is_pressed'] else 0
        elif button_id == 2:
            return 1 if self.up_button['is_pressed'] else 0
        elif button_id == 3:
            return 1 if self.down_button['is_pressed'] else 0
        elif button_id == 4:
            return 1 if self.enter_button['is_pressed'] else 0
        else:
            raise NotImplementedError()

    def lcd_draw_string(self, string, row):
        assert(row < len(self.lcd_messages))
        self.lcd_messages[row] = string

    def set_camera_resolution(self, width, height):
        self.camera_settings['resolution'] = (width, height)

    def set_camera_colormode(self, colormode):
        self.camera_settings['colormode'] = colormode

    def set_binary_threshold(self, bin_threshold):
        self.camera_settings['bin_threshold'] = bin_threshold

    def read_camera(self):
        if self.camera_view is None:
            return None
        pil_im = Image.fromarray(self.camera_view)
        if self.camera_settings['colormode'] == 'gray':
            ret = pil_im.convert('L').resize(self.camera_settings['resolution'])
            ret = np.asarray(ret)
        elif self.camera_settings['colormode'] == 'binary':
            pil_im = pil_im.convert('L').resize(self.camera_settings['resolution'])
            im = np.asarray(pil_im)
            im_bin = np.array(im)
            im_bin[im < self.camera_settings['bin_threshold']] = 0
            im_bin[im >= self.camera_settings['bin_threshold']] = 255
            ret = im_bin
        else:
            raise NotImplementedError()
        return ret

    def force_ev3_pos(self, new_pos):
        self.ev3_state.pos = new_pos

    def increment_ev3_angle(self, angle_delta):
        self.ev3_state.angle = angle_delta + self.ev3_state.angle

    def set_touch_sensor_state(self, is_pressed):
        self.touch_sensor['is_pressed'] = is_pressed
        self.touch_sensor['pressed_time'] = dt.now().timestamp()

    def set_left_button_state(self, is_pressed):
        self.left_button['is_pressed'] = is_pressed
        self.left_button['pressed_time'] = dt.now().timestamp()

    def set_right_button_state(self, is_pressed):
        self.right_button['is_pressed'] = is_pressed
        self.right_button['pressed_time'] = dt.now().timestamp()

    def set_up_button_state(self, is_pressed):
        self.up_button['is_pressed'] = is_pressed
        self.up_button['pressed_time'] = dt.now().timestamp()

    def set_down_button_state(self, is_pressed):
        self.down_button['is_pressed'] = is_pressed
        self.down_button['pressed_time'] = dt.now().timestamp()

    def set_enter_button_state(self, is_pressed):
        self.enter_button['is_pressed'] = is_pressed
        self.enter_button['pressed_time'] = dt.now().timestamp()

    def reset(self):
        self.__init__()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting_file', type=str, default='setting.yaml')
    args = parser.parse_args()
    settings.SharedSettings('global', args)

    env = EV3Env(args)
    renderer = Renderer()

    midpoint = 50.
    while True:
        color = env.color_sensor_get_reflect()
        error = color - midpoint
        steer = 1.2 * error
        env.motor_steer(10, int(steer))
        env.step()
        renderer.show(env)


if __name__ == '__main__':
    main()
