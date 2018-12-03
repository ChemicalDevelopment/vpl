"""

basic operations

"""

from vpl import VPL

import numpy as np

import math

import cv2

import time

class Resize(VPL):
    """

    Usage: Resize(w=512, h=256)

      * "w" = width, in pixels
      * "h" = height, in pixels

    optional arguments:

      * "method" = opencv resize method, default is cv2.INTER_LINEAR

    """

    def register(self):
        self.available_args["w"] = "width in pixels"
        self.available_args["h"] = "height in pixels"

    def process(self, pipe, image, data):
        height, width, depth = image.shape

        if width != self["w"] or height != self["h"]:
            resize_method = self.get("method", cv2.INTER_LINEAR)
            #t = cv2.UMat(image)
            t = image
            r = cv2.resize(t, (self["w"], self["h"]), interpolation=resize_method)
            return r, data
        else:
            # if it is the correct size, don't spend time resizing it
            return image, data

class FFT(VPL):

    """

    Usage: FFT()

    Transforms the image into the FFT image

    """

    def register(self):
        pass

    def process(self, pipe, image, data):
        Bfft, Gfft, Rfft = np.fft.rfft2(image[:,:,0]), np.fft.rfft2(image[:,:,1]), np.fft.rfft2(image[:,:,2])

        filt_mask = np.zeros((Bfft.shape[0], Bfft.shape[1]), np.complex)
        max_dist = 1.0 + filt_mask.shape[1] / filt_mask.shape[0]
        for i in range(0, filt_mask.shape[0]):
            for j in range(0, filt_mask.shape[1]):
                prop = (i + j) / (max_dist * filt_mask.shape[0])
                #if prop < 0.04 or prop > 0.92:
                filt_mask[i, j] = 1.0 * np.exp(1j * 2 * math.pi * 0.1)
                #else:
                #    filt_mask[i, j] = 0.0


        Bfft *= filt_mask
        Gfft *= filt_mask
        Rfft *= filt_mask

        #result = np.zeros((image.shape[0], image.shape[1]//2+1, 3), dtype=np.float32)

        #result[:,:,0] = 4.0 * np.abs(np.fft.rfft2(B)) / (image.shape[0] * image.shape[1])

        image[:,:,0] = np.fft.irfft2(Bfft)
        image[:,:,1] = np.fft.irfft2(Gfft)
        image[:,:,2] = np.fft.irfft2(Rfft)
        #image[:,:321,0] = np.abs(Bfft) / 321
        #image[:,:321,1] = np.abs(Gfft) / 321
        #image[:,:321,2] = np.abs(Rfft) / 321
        return image, data


class Blur(VPL):
    """

    Usage: Blur(w=4, h=8)

      * "w" = width, in pixels (for guassian blur, w % 2 == 1) (for median blur, this must be an odd integer greater than 1 (3, 5, 7... are good))
      * "h" = height, in pixels (for guassian blur, w % 2 == 1) (for median blur, this is ignored)

    optional arguments:

      * "method" = opencv blur method, default is vpl.BlurType.BOX
      * "sx" = 'sigma x' for the Gaussian blur standard deviation, defaults to letting OpenCV choose based on image size
      * "sy" = 'sigma y' for the Gaussian blur standard deviation, defaults to letting OpenCV choose based on image size

    """

    def register(self):
        self.available_args["w"] = "width in pixels for blur kernel"
        self.available_args["h"] = "height in pixels for blur kernel"

        self.available_args["method"] = "method of blurring, 'box', 'median', 'guassian' are all good"

        self.available_args["sx"] = "sigma x (guassian only)"
        self.available_args["sy"] = "sigma y (guassian only)"



    def process(self, pipe, image, data):
        if self["w"] in (0, None) or self["h"] in (0, None):
            return image, data
        else:
            resize_method = self.get("method", "box")

            if resize_method == "guassian":
                sx, sy = self.get("sx", 0), self.get("sy", 0)
                return cv2.GaussianBlur(image, (self["w"], self["h"]), sigmaX=sx, sigmaY=sy), data
            elif resize_method == "median":
                return cv2.medianBlur(image, self["w"]), data
            else:
                # default is BlurType.BOX
                return cv2.blur(image, (self["w"], self["h"])), data


class Bilateral(VPL):
    def register(self):
        pass

    def process(self, pipe, image, data):
        s_color = self.get("s_color", 8)
        s_space = self.get("s_space", 16)
        res = cv2.bilateralFilter(image.copy(), s_color, s_space, s_space)
        return res, data



class ConvertColor(VPL):
    """
    Usage: ConvertColor(conversion=None)
      * conversion = type of conversion (see https://docs.opencv.org/3.1.0/d7/d1b/group__imgproc__misc.html#ga4e0972be5de079fed4e3a10e24ef5ef0) ex: cv2.COLOR_BGR2HSL
    """

    def process(self, pipe, image, data):
        if self["conversion"] is None:
            return image, data
        else:
            return cv2.cvtColor(image, self["conversion"]), data


class FPSCounter(VPL):
    """

    Usage: FPSCounter()


    Simply adds the FPS in the bottom left corner

    """

    def register(self):
        pass

    def process(self, pipe, image, data):
        if not hasattr(self, "fps_records"):
            self.fps_records = []

        if not hasattr(self, "last_print"):
            self.last_print = (0, None)

        ctime = time.time()
        self.fps_records += [(ctime, pipe.chain_fps[0])]
        
        # filter only the last second of readings
        self.fps_records = list(filter(lambda tp: abs(ctime - tp[0]) < 1.0, self.fps_records))

        avg_fps = sum([fps for t, fps in self.fps_records]) / len(self.fps_records)

        if self.last_print[1] is None or abs(ctime - self.last_print[0]) > 1.0 / 3.0:
            self.last_print = (ctime, avg_fps)


        font = cv2.FONT_HERSHEY_SIMPLEX
        height, width, _ = image.shape
        geom_mean = math.sqrt(height * width)
        offset = geom_mean * .01
        
        return cv2.putText(image.copy(), "%2.1f" % self.last_print[1], (int(offset), int(height - offset)), font, offset / 6.0, (255, 0, 0), int(offset / 6.0 + 2)), data




class Grayscale(VPL):
    """

    Usage: Resize(w=512, h=256)

      * "w" = width, in pixels
      * "h" = height, in pixels

    optional arguments:

      * "method" = opencv resize method, default is cv2.INTER_LINEAR

    """

    def register(self):
        pass

    def process(self, pipe, image, data):
        r, g, b = image[:,:,2], image[:,:,1], image[:,:,0]
        atype = np.float32
        bw = ((r.astype(atype) + g.astype(atype) + b.astype(atype)) / 3.0).astype(image.dtype)

        for i in range(0, 3):
            image[:,:,i] = bw
        return image, data




class PrintInfo(VPL):

    def register(self):
        self.available_args["fps"] = "fps cap to display results at"

    def process(self, pipe, image, data):
        if not hasattr(self, "num"):
            self.num = 0
        if not hasattr(self, "last_time") or time.time() - self.last_time > 1.0 / self.get("fps", 3):
            if self.get("extended", False):
                print ("(#%d) image[%s]: %s" % (self.num, image.dtype, image.shape))
                
                print ("total fps: %.1f" % (pipe.chain_fps[0]))
                for i in range(len(pipe.chain)):
                    if i < len(pipe.chain_fps[1]):
                        print ("  %s # %.1f fps" % (str(pipe.chain[i]), pipe.chain_fps[1][i]))
                    else:
                        print ("  %s" % (str(pipe.chain[i])))

                print ("data: ")
                
                for k in data:
                    print ("  %s: %s" %(k, data[k]))

                print("")

            else:
                print ("image[%s]: %s" % (image.dtype, image.shape))
                print ("fps: %s" % str(pipe.chain_fps))

            print("")

            self.last_time = time.time()

        self.num += 1

        return image, data


class Erode(VPL):
    """

    Usage: Erode(mask, None, iterations) 
    
    """
    def process(self, pipe, image, data):
        image = cv2.erode(image, None, iterations=self.get("iterations", 2))
        return image, data

class Dilate(VPL):
    """

    Usage: Dilate(mask, None, iterations)

    """
    def process(self, pipe, image, data):
        image = cv2.dilate(image, None, iterations=self.get("iterations", 2))
        return image, data


import pyopencl as cl

class OpenCL(VPL):

    def register(self):
        pass

    def process(self, pipe, image, data):

        if not hasattr(self, "is_init"):
            OPENCL_SRC="""
__kernel void convert(__global __read_only uchar * img_in, __global __write_only uchar * img_out, int w, int h) {
        int x = get_global_id(0), y = get_global_id(1);
        if (x >= w || y >= h) return;
        int idx = x + y * w;
        // img_in[3*idx+0] = R component at pixel x, y
        // img_in[3*idx+1] = G component at pixel x, y
        // img_in[3*idx+2] = B component at pixel x, y

        int ker = 20;

        // new components
        float nR = 0, nG = 0, nB = 0;

        int i, j;
        int tx, ty;
        float c_sum = 0.0f;
        for (i = -ker; i <= ker; ++i) {
            tx = x + i;
            if (tx < 0 || tx >= w) continue;
            for (j = -ker; j <= ker; ++j) {
                ty = y + i;
                if (ty < 0 || ty >= h) continue;
                int tidx = tx + ty * w;
                // window value
                //float w = 1.0f - (abs(i) + abs(j)) / (2.0f * ker);
                //float w = i == 0 && j == 0 ? 1.0f : 0.0f;

                float c = exp(-powf(abs(i) + abs(j), 2.0f) / (ker * ker));
                nR += c * img_in[3*tidx+0];
                nG += c * img_in[3*tidx+1];
                nB += c * img_in[3*tidx+2];
                c_sum += c;
            }
        }

        img_out[3 * idx + 2] = (uchar)(nR / c_sum);
        img_out[3 * idx + 1] = (uchar)(nG / c_sum);
        img_out[3 * idx + 0] = (uchar)(nB / c_sum);
    }
"""
            mf = cl.mem_flags

            platform = cl.get_platforms()[self.get("opencl_platform", 0)]
            devs = platform.get_devices()[self.get("opencl_device", -1)]
            self.ctx = cl.Context(devs if isinstance(devs, list) else [devs])
            self.queue = cl.CommandQueue(self.ctx)

            # now build the programs
            self.prg = cl.Program(self.ctx, OPENCL_SRC).build()

            self.src_buf = cl.Buffer(self.ctx, mf.READ_ONLY, image.nbytes)
            self.dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, image.nbytes)
            self.dest = np.empty_like(image)

            # we have initialized
            self.is_init = True

        h, w, _ = image.shape

        # write current image
        cl.enqueue_copy(self.queue, self.src_buf, image)

        self.prg.convert(self.queue, (w, h), None, self.src_buf, self.dest_buf, np.int32(w), np.int32(h))
        
        # read back image
        cl.enqueue_copy(self.queue, self.dest, self.dest_buf)

        return self.dest, data


class OpenCLConvolve(VPL):

    def register(self):
        pass

    def process(self, pipe, image, data):

        if not hasattr(self, "is_init"):
            # loop unrolling on mask
            mask = np.array(self.get("kernel", [[0, 0, 0], [0, 1, 0], [0, 0, 0]])) * self.get("factor", 1.0)
            
            if mask.shape[0] != mask.shape[1]:
                print ("WARNING: mask should be square for convolution!")

            if mask.shape[0] % 2 != 1:
                print ("WARNING: mask should be an odd length")

            single_val_codeblock = """
            tx = x + {i};
            ty = y + {j};
            if (tx >= 0 && tx < w && ty >= 0 && ty < h) {{
                tidx = tx + ty * w;
                c = (float)({MASK_VAL});
                nR += c * (float)img_in[3*tidx+0];
                nG += c * (float)img_in[3*tidx+1];
                nB += c * (float)img_in[3*tidx+2];
            }}
            """

            kernel_unfolded = ""

            for i in range(0, mask.shape[0]):
                for j in range(0, mask.shape[1]):
                    if mask[j, i] != 0:
                        print(i, j, mask[j, i])
                        cur_cb = single_val_codeblock.format(i=i - mask.shape[0] // 2, j=mask.shape[0] // 2 - j, MASK_VAL=mask[j, i])
                        kernel_unfolded += cur_cb

            print (kernel_unfolded)

            OPENCL_SRC="""
__kernel void convert(__global __read_only uchar * img_in, __global __write_only uchar * img_out, int w, int h) {{
        int x = get_global_id(0), y = get_global_id(1);
        if (x >= w || y >= h) return;
        int idx = x + y * w;
        // img_in[3*idx+0] = R component at pixel x, y
        // img_in[3*idx+1] = G component at pixel x, y
        // img_in[3*idx+2] = B component at pixel x, y

        // new components
        float nR = 0, nG = 0, nB = 0;

        int tx, ty, tidx;
        float c;

        // AUTOGEN START

        {gen_code}

        // AUTOGEN END

        

        img_out[3 * idx + 0] = (uchar)clamp(nR, 0.0f, 255.0f);
        img_out[3 * idx + 1] = (uchar)clamp(nG, 0.0f, 255.0f);
        img_out[3 * idx + 2] = (uchar)clamp(nB, 0.0f, 255.0f);
    }}
""".format(gen_code=kernel_unfolded)

            #print(OPENCL_SRC)

            mf = cl.mem_flags

            platform = cl.get_platforms()[self.get("opencl_platform", 0)]
            devs = platform.get_devices()[self.get("opencl_device", -1)]
            self.ctx = cl.Context(devs if isinstance(devs, list) else [devs])
            self.queue = cl.CommandQueue(self.ctx)

            # now build the programs
            self.prg = cl.Program(self.ctx, OPENCL_SRC).build()

            self.src_buf = cl.Buffer(self.ctx, mf.READ_ONLY, image.nbytes)
            self.dest_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, image.nbytes)
            self.dest = np.empty_like(image)

            # we have initialized
            self.is_init = True

        h, w, _ = image.shape

        # write current image
        cl.enqueue_copy(self.queue, self.src_buf, image)

        self.prg.convert(self.queue, (w, h), None, self.src_buf, self.dest_buf, np.int32(w), np.int32(h))
        
        # read back image
        cl.enqueue_copy(self.queue, self.dest, self.dest_buf)

        return self.dest, data


