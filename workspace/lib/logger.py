import os
import time
from datetime import datetime as dt
import numpy as np
from PIL import Image

class Logger:
    def __init__(self, top_dir='data', base_dir=None, frame_id=0):
        if not os.path.exists(top_dir):
            os.mkdir(top_dir)
        if base_dir is None:
            self.base_dir = os.path.join(top_dir, dt.now().strftime('%Y%m%d-%H%M%S'))
        else:
            self.base_dir = os.path.join(top_dir, base_dir)
        self.image_dir = os.path.join(self.base_dir, 'images')
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)
        if not os.path.exists(self.image_dir):
            os.mkdir(self.image_dir)
        self.f = None
        self.frame_id = frame_id
        self.f = open(os.path.join(self.base_dir, 'list.txt'), 'w')

    def write(self, image, label=None):
        print(self.image_dir + '/{:07d}.png'.format(self.frame_id))
        image_path = self.image_dir + '/{:07d}.png'.format(self.frame_id)
        image.save(image_path)
        if label is not None:
            self.f.write('{0:07d}.png {1}\n'.format(self.frame_id, label))
        else:
            self.f.write('{0:07d}.png\n'.format(self.frame_id))
        self.f.flush()
        self.frame_id = self.frame_id + 1

    def close(self):
        self.f.close()
