import time
import configparser
import socket
from threading import Thread
import numpy as np
from PIL import Image


class RealCameraBase:
    def __init__(self, resolution=(64,48), framerate=32):
        from picamera import PiCamera
        from picamera.array import PiRGBArray
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.raw_capture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.raw_capture,
                                                     format="bgr",
                                                     use_video_port=True)
        self.stopped = False
        self.frame = None
        self.stopped = False
        self.camera.sharpness = 0
        self.camera.contrast = 0
        self.camera.brightness = 50
        self.camera.saturation = 0
        self.camera.ISO = 0
        self.camera.video_stabilization = False
        self.camera.exposure_compensation = 0
        self.camera.awb_mode = 'flash'
        self.camera.meter_mode = 'average'
        self.camera.image_effect = 'none'
        self.camera.color_effects = None
        self.camera.rotation = 180
        self.camera.hflip = True
        self.camera.vflip = True
        self.camera.crop = (0.0, 0.0, 1.0, 1.0)
        self.convert_image=True

    def start(self):
        self.stopped = False
        self.update_thread = Thread(target=self.update, args=())
        self.update_thread.start()
        time.sleep(2.0)
        return self

    def update(self):
        for f in self.stream:
            self.frame = f.array
            self.raw_capture.truncate(0)
            if self.stopped:
                return

    def read(self):
        return self.frame

    def stop(self):
        if self.update_thread is not None:
            self.stopped = True
            self.update_thread.join()
        self.stream.close()
        self.raw_capture.close()
        self.camera.close()


class RealCamera(RealCameraBase):
    def __init__(self, resolution=(64,48), framerate=10, colormode='binary', bin_threshold=50):
        # Set original resolution to (64,48) for resolutions smaller than (64,48)
        # because PiCamera doesn't work when giving a small resolution.
        if resolution[0] < 64 or resolution[1] < 48:
            original_resol = (64, 48)
        else:
            original_resol = resolution
        super().__init__(resolution=original_resol, framerate=framerate)
        self.resolution = resolution
        self.colormode = colormode
        self.bin_threshold = bin_threshold

    def _convert(self, pil_im):
        if self.colormode == 'gray':
            ret = pil_im.convert('L').resize(self.resolution)
        elif self.colormode == 'binary':
            pil_im = pil_im.convert('L').resize(self.resolution)
            im = np.asarray(pil_im)
            im_bin = np.array(im)
            im_bin[im < self.bin_threshold] = 0
            im_bin[im >= self.bin_threshold] = 255
            ret = Image.fromarray(im_bin)
        elif self.colormode == 'rgb':
            ret = pil_im.resize(self.resolution)
        else:
            ret = pil_im.resize(self.resolution)
        return ret

    def read(self):
        # Convert BGR in PiCamera format into RGB in Pillow format.
        pil_im = Image.fromarray(super().read()[:, :, ::-1])
        return self._convert(pil_im)


class SimCamera:
    class Receiver:
        def __init__(self, host, port):
            self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server.bind((host, port))

        def receive(self, bufsize=1024):
            rcvmsg, _ = self.server.recvfrom(bufsize)
            return np.fromstring(rcvmsg, dtype=np.uint8)

        def close(self):
            self.server.close()

    class Sender:
        def __init__(self, host, port):
            self.address = (host, port)
            self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        def send(self, data):
            data = bytes(data)
            self.client.sendto(data, self.address)

        def close(self):
            self.client.close()

    def __init__(self, resolution, framerate, colormode, bin_threshold,
                 rpi_address, rpi_port, sim_address, sim_port):
        # Note SimCamera supports the gray or binary colormodes.
        # Do NOT use the rgb colormode.
        self.recver = self.Receiver(rpi_address, rpi_port)
        self.sender = self.Sender(sim_address, sim_port)
        self.resolution = resolution
        self.colormode = colormode
        self.bin_threshold = bin_threshold
        self.image_bytes = resolution[0] * resolution[1]

    def _set_resolution(self):
        resolution = self.resolution
        send_data = [255, 0, resolution[0], resolution[1]]
        self.sender.send(send_data)

    def _set_color_colormode(self):
        send_data = [255, 10]
        colormode = self.colormode
        if colormode == 'gray':
            send_data.append(0)
        elif colormode == 'binary':
            send_data.append(1)
        else:
            raise ValueError(colormode)
        self.sender.send(send_data)

    def _set_bin_threshold(self):
        send_data = [255, 20, self.bin_threshold]
        self.sender.send(send_data)

    def start(self):
        self._set_resolution()
        self._set_color_colormode()
        self._set_bin_threshold()
        return self

    def read(self):
        send_data = [255, 100]
        self.sender.send(send_data)
        data = self.recver.receive(self.image_bytes)
        data = np.reshape(data, (self.resolution[1], self.resolution[0]))
        return Image.fromarray(data)

    def stop(self):
        self.sender.close()
        self.recver.close()


class VideoStream:
    def __init__(self, resolution=(64,48), framerate=10, colormode='rgb', bin_threshold=50):
        inifile = configparser.SafeConfigParser()
        inifile.read('./config.ini')
        env = inifile.get('environment', 'env')
        if env == 'real_ev3':
            self.camera = RealCamera(resolution,
                                     framerate,
                                     colormode,
                                     bin_threshold)
        elif env == 'simulated_ev3':
            rpi_address = inifile.get('simulated_ev3', 'rpi_address')
            rpi_port = inifile.getint('simulated_ev3', 'rpi_vs_port')
            sim_address = inifile.get('simulated_ev3', 'sim_address')
            sim_port = inifile.getint('simulated_ev3', 'sim_vs_port')
            self.camera = SimCamera(resolution,
                                    framerate,
                                    colormode,
                                    bin_threshold,
                                    rpi_address, rpi_port,
                                    sim_address, sim_port)
        else:
            raise NotImplementedError()

    def start(self):
        return self.camera.start()

    def read(self):
        return self.camera.read()

    def stop(self):
        self.camera.stop()


def main():
    vs = VideoStream((20, 15), 10, colormode='gray').start()
    for i in range(500):
        print("i = {0}".format(i))
        im = vs.read()
        im.save('test/{0}.png'.format(i))
        time.sleep(0.1)
    vs.stop()


if __name__ == '__main__':
    main()
