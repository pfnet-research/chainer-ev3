import os
import sys
import socket
import queue
import argparse
import time
import cv2
import math
from threading import Thread

import settings
from point import Point
from env import EV3Env
from renderer import Renderer


class Receiver:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((host, port))

    def receive(self, bufsize=1024):
        rcvmsg, _ = self.server.recvfrom(bufsize)
        return rcvmsg

    def close(self):
        self.server.close()

class Sender:
    def __init__(self, host, port):
        self.address = (host, port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.client.sendto(data, self.address)

    def close(self):
        self.client.close()


class EV3Communicator:
    def __init__(self):
        self.settings = settings.SettingsRegistry['global']
        self.que = queue.Queue()
        self.recver = Receiver(self.settings.sim_host, self.settings.sim_port)
        self.sender = Sender(self.settings.rpi_host, self.settings.rpi_port)

    def _send(self, data):
        self.sender.send(bytes(data))

    def _receive(self, bufsize=1024):
        rsvmsg = self.recver.receive(bufsize)
        return list(map(int, rsvmsg))

    def send_byte(self, b):
        assert(0 <= b and b <= 255)
        self._send([b])

    def read_byte(self):
        if self.que.empty():
            try:
                data = self._receive()
            except:
                return
            for x in data:
                self.que.put(x)
        return self.que.get()

    def close(self):
        self.recver.close()
        self.sender.close()


class VSCommunicator:
    def __init__(self):
        self.settings = settings.SettingsRegistry['global']
        self.que = queue.Queue()
        self.recver = Receiver(self.settings.sim_host, self.settings.sim_vs_port)
        self.sender = Sender(self.settings.rpi_host, self.settings.rpi_vs_port)

    def _receive(self, bufsize=1024):
        rsvmsg = self.recver.receive(bufsize)
        return list(map(int, rsvmsg))

    def read_byte(self):
        if self.que.empty():
            try:
                data = self._receive()
            except:
                return
            for x in data:
                self.que.put(x)
        return self.que.get()

    def send_image(self, image):
        self.sender.send(image.tostring())

    def close(self):
        self.recver.close()
        self.sender.close()


class Simulator:
    def __init__(self):
        self.settings = settings.SettingsRegistry['global']
        self.ev3_com = EV3Communicator()
        self.vs_com = VSCommunicator()
        self.env = EV3Env()
        self.stopped = False

    def start(self):
        self.simulation_thread = Thread(target=self.simulation_loop, args=()).start()
        self.command_thread = Thread(target=self.command_loop, args=()).start()
        self.vs_thread = Thread(target=self.vs_loop, args=()).start()
        return self

    def stop(self):
        self.stopped = True
        self.ev3_com.close()
        self.vs_com.close()

    def simulation_loop(self):
        while True:
            if self.stopped:
                return
            self.env.step()

    def command_loop(self):
        while True:
            if self.stopped:
                return

            header = self.ev3_com.read_byte()
            if header != 255:
                continue

            cmd_id = self.ev3_com.read_byte()
            if cmd_id == 0:
                motor_port = self.ev3_com.read_byte()
                motor_type = self.ev3_com.read_byte()
                self.env.motor_config(motor_port, motor_type)
                continue

            if cmd_id == 10:
                left_motor_port = self.ev3_com.read_byte()
                right_motor_port = self.ev3_com.read_byte()
                drive = self.ev3_com.read_byte() - 100
                steer = self.ev3_com.read_byte() - 100
                drive = min(max(drive, -100), 100)
                steer = min(max(steer, -100), 100)
                self.env.motor_steer(left_motor_port, right_motor_port, drive, steer)
                continue

            if cmd_id == 100:
                sensor_port = self.ev3_com.read_byte()
                sensor_type = self.ev3_com.read_byte()
                self.env.sensor_config(sensor_port, sensor_type)
                continue

            if cmd_id == 110:
                touch_sensor_port = self.ev3_com.read_byte()
                touch = self.env.touch_sensor_is_pressed(touch_sensor_port)
                self.ev3_com.send_byte(touch)
                continue

            if cmd_id == 120:
                color_sensor_port = self.ev3_com.read_byte()
                color = self.env.color_sensor_get_reflect(color_sensor_port)
                self.ev3_com.send_byte(color)
                continue

            if cmd_id == 200:
                line = self.ev3_com.read_byte()
                buf = ''
                for i in range(100):
                    r = self.ev3_com.read_byte()
                    if r == 0:
                        break
                    buf += chr(r)
                self.env.lcd_draw_string(buf, line)
                continue
            time.sleep(0.01)

    def vs_loop(self):
        while True:
            if self.stopped:
                return

            header = self.vs_com.read_byte()
            if header != 255:
                continue

            cmd_id = self.vs_com.read_byte()

            if cmd_id == 0:
                """ Set resolution """
                width = self.vs_com.read_byte()
                height = self.vs_com.read_byte()
                self.env.set_camera_resolution(width, height)
                continue

            if cmd_id == 10:
                """ Set color mode """
                mode_id = self.vs_com.read_byte()
                if mode_id == 0:
                    mode = 'gray'
                elif mode_id == 1:
                    mode = 'binary'
                else:
                    raise NotImplementedError()
                self.env.set_camera_colormode(mode)
                continue

            if cmd_id == 20:
                """ Set a threshold to binalize an image """
                threshold = self.vs_com.read_byte()
                self.env.set_binary_threshold(threshold)
                continue

            if cmd_id == 100:
                """ Send a latest image """
                img = self.env.read_camera()
                self.vs_com.send_image(img)
                continue
            time.sleep(0.01)

from PIL import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting_file', type=str, default='setting.yaml')
    args = parser.parse_args()
    params = settings.SharedSettings('global', args)
    simulator = Simulator().start()
    renderer = Renderer()
    window_name = 'EV3 Simulator'
    cv2.namedWindow(window_name)

    def canvas2world(canvas_x, canvas_y):
        scale_w = params.world_w / params.canvas_w
        scale_h = params.world_h / params.canvas_h
        return Point(canvas_x * scale_w,
                     canvas_y * scale_h)

    def on_mouse(event, x, y, flag, params):
        env = params[0]
        if event == cv2.EVENT_LBUTTONDOWN:
            if flag & cv2.EVENT_FLAG_SHIFTKEY:
                delta = math.radians(10)
                env.increment_ev3_angle(delta)
            elif flag & cv2.EVENT_FLAG_ALTKEY:
                delta = math.radians(10)
                env.increment_ev3_angle(-delta)
            else:
                new_pos = canvas2world(x, y)
                env.force_ev3_pos(new_pos)

    cv2.setMouseCallback(window_name, on_mouse, [simulator.env])

    try:
        while True:
            canvas = renderer.render_env(simulator.env)
            cv2.imshow(window_name, canvas)
            key = cv2.waitKey(5)
            if key == ord('q'):
                # Quit simulator
                break
            if key == ord('r'):
                # Reset simulator
                simulator.env.reset()
            if key == ord('t'):
                # Push touch sensor
                simulator.env.set_touch_sensor_state(is_pressed=True)
            time.sleep(0.01)
    except:
        simulator.stop()
        import traceback
        traceback.print_exc()
    simulator.stop()

if __name__ == '__main__':
    main()
