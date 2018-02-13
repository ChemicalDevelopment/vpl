"""

fun filters

"""

from vpl import VPL

import cv2
import numpy as np

import math
import random

class CoolChannelOffset(VPL):

    def process(self, pipe, image, data):
        h, w, nch = image.shape
        ch = cv2.split(image)

        xoff_gen = self.get("xoff", lambda i: 8 * i)
        yoff_gen = self.get("yoff", lambda i: -2.5 * i)

        for i in range(nch):
            xoff = xoff_gen * i if type(xoff_gen) == int else int(xoff_gen(i)) 
            yoff = yoff_gen * i if type(yoff_gen) == int else int(yoff_gen(i)) 
            ch[i] = np.roll(np.roll(image[:,:,i], yoff, 0), xoff, 1)
            #image[:,:,i] = np.roll(image[:,:,i], 10, 1)

        image = cv2.merge(ch)

        return image, data


class Bleed(VPL):

    def process(self, pipe, image, data):
        N = self.get("N", 18)
        if not hasattr(self, "buffer"):
            self.buffer = []

        arith_dtype = np.float32

        self.buffer.insert(0, image.astype(arith_dtype))

        if len(self.buffer) >= N:
            self.buffer = self.buffer[:N]

        #a = [len(self.buffer) - i + N for i in range(0, len(self.buffer))]
        a = [(N - i) * 2.0 for i in range(0, len(self.buffer))]

        # normalize
        a = np.array([a[i] / sum(a) for i in range(len(a))], dtype=arith_dtype)

        b4dtype = image.dtype

        image = image.copy().astype(arith_dtype)

        image[:,:,:] = 0
        
        h, w, d = image.shape

        for i in range(len(a)):
            if image.shape != self.buffer[i].shape:
                self.buffer[i] = cv2.resize(self.buffer[i], (w, h))

            #image = image + a[i] * self.buffer[i]
            image = cv2.addWeighted(image, 1.0, self.buffer[i], a[i], 0)

        return image.astype(b4dtype), data

        """

        b4dtype = image.dtype
        image = image.astype(np.float32)

        for i in range(len(a)):
            image = image + self.buffer[i] * a[i]

        return image.astype(b4dtype), data


        """



class Pixelate(VPL):

    def process(self, pipe, image, data):
        N = self.get("N", 7.5)

        h, w, d = image.shape

        image = cv2.resize(image, (int(w // N), int(h // N)), interpolation=cv2.INTER_NEAREST)
        image = cv2.resize(image, (w, h), interpolation=cv2.INTER_NEAREST)

        return image, data

class Noise(VPL):

    def process(self, pipe, image, data):
        level = self.get("level", .125)

        m = (100,100,100) 
        s = (100,100,100)
        noise = np.zeros_like(image)

        image = cv2.addWeighted(image, 1 - level, cv2.randn(noise, m, s), level, 0)

        return image, data


class DetailEnhance(VPL):

    def process(self, pipe, image, data):
        image = cv2.detailEnhance(image, sigma_s=self.get("r", 10), sigma_r=self.get("s", .15))
        return image, data


class Cartoon(VPL):

    def process(self, pipe, image, data):
        down = self.get("down", 2)
        bilateral = self.get("bilateral", 7)

        for i in range(down):
            image = cv2.pyrDown(image)

        for i in range(bilateral):
            image = cv2.bilateralFilter(image, d=9,
                                    sigmaColor=9,
                                    sigmaSpace=7)

        for i in range(down):
            image = cv2.pyrUp(image)

        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image_blur = cv2.medianBlur(image_gray, 7)

        image_edge = cv2.adaptiveThreshold(image_blur, 255,
                                 cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY,
                                 blockSize=9,
                                 C=2)

        image_edge = cv2.cvtColor(image_edge, cv2.COLOR_GRAY2RGB)
        image_cartoon = cv2.bitwise_and(image, image_edge)

        return image_cartoon, data

class HSLBin(VPL):

    def process(self, pipe, image, data):
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

        def nearest(b, m):
            return m * (b // m)

        hls_image[:,:,0] = nearest(hls_image[:,:,0], self.get("H", 40))
        hls_image[:,:,1] = nearest(hls_image[:,:,1], self.get("L", 30))
        hls_image[:,:,2] = nearest(hls_image[:,:,2], self.get("S", 40))


        res_image = cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)

        return res_image, data

class RainbowCrazy(VPL):

    def process(self, pipe, image, data):
        hls_image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)

        if not hasattr(self, "ct"):
            self.ct = 0


        hls_image[:,:,0] = ((hls_image[:,:,0] + self.ct * 8) % 180).astype(hls_image.dtype)
        hls_image[:,:,2] += 20

        self.ct += 1

        res_image = cv2.cvtColor(hls_image, cv2.COLOR_HLS2BGR)

        return res_image, data

class Scanlines(VPL):

    def process(self, pipe, image, data):

        h, w, d = image.shape

        res = np.zeros(image.shape, dtype=image.dtype)

        if not hasattr(self, "ct"):
            self.ct = 0

        rnd_prd = random.random() * self.get("randomness", 0.0)

        for i in range(h):
            prd = rnd_prd + self.ct * self.get("speed", .8) / 60.0 + i * self.get("frequency", 1.6) / h
            off = self.get("size", 1.2) * math.tan(math.pi * prd)

            res[i] = np.roll(image[i], int(off), 0)

        self.ct += 1

        return res, data


class Roll(VPL):

    def register(self):
        self.available_args["h"] = "should be (lambda height, frame_count) to tell how much to roll"
        self.available_args["w"] = "should be (lambda width, frame_count) to tell how much to roll"

    def process(self, pipe, image, data):

        h, w, d = image.shape

        res = np.zeros(image.shape, dtype=image.dtype)

        if not hasattr(self, "ct"):
            self.ct = 0

        # check these out
        h_off = self.get("h", lambda height, frame_count: 0)
        w_off = self.get("w", lambda height, frame_count: 0)

        for i in range(h):
            off = h_off(i, self.ct)
            res[i] = np.roll(image[i], int(off), 0)

        image = res.copy()

        for i in range(w):
            off = w_off(i, self.ct)
            res[:,i,:] = np.roll(image[:,i,:], int(off), 0)

        self.ct += 1

        return res, data




class Grid(VPL):

    def register(self):
        self.available_args["h"] = "how many copies height wise"
        self.available_args["w"] = "how many copies width wise"
        self.available_args["keep_size"] = "whether or not to keep the input size (default True)"

    def process(self, pipe, image, data):

        h, w, d = image.shape

        orig_h, orig_w = int(h), int(w)


        # check these out
        h = self.get("h", 2)
        w = self.get("w", 2)

        if self.get("keep_size", True):
            image = cv2.resize(image.copy(), (orig_w // w, orig_h // h), cv2.INTER_NEAREST)

        res = image.copy()


        for i in range(h - 1):
            res = np.concatenate((res, image), axis=0)

        image = res.copy()

        for i in range(w - 1):
            res = np.concatenate((res, image), axis=1)

        if self.get("keep_size", True):
            res = cv2.resize(res, (orig_w, orig_h), cv2.INTER_NEAREST)

        return res, data






