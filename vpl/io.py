"""

input/output

"""

from vpl import VPL

from vpl.defines import cap_prop_lookup

import cv2
import numpy as np

import vpl

import os
import time
import pathlib

class VideoSource(VPL):
    """

    Usage: VideoSource(source=0)

    optional arguments:

      * "source" = camera index (default of 0), or a string containing a video file (like "VIDEO.mp4") or a string containing images ("data/*.png")
      * "properties" = CameraProperties() object with CAP_PROP values (see that class for info)
      * "repeat" = whether to repeat the image sequence (default False)
    
    this sets the image to a camera.

    THIS CLEARS THE IMAGE THAT WAS BEING PROCESSED, USE THIS AS THE FIRST PLUGIN

    """

    def register(self):
        self.available_args["source"] = "source for VideoSource (int for camera index, filename for video file, or pattern 'data/{num}.png' for image sequence)"
        
        self.available_args["properties"] = "this should be a vpl.CameraProperties objects"
        self.available_args["repeat"] = "bool whether or not to repeat an image sequence (default is False)"


    def camera_update_image(self):
        self.camera_flag, self.camera_image = self.camera.read()

    def video_reader_update_image(self):
        _, self.camera_image = self.video_reader.read()

    def image_sequence_update_image(self):
        my_idx = self.images_idx
        if self.get("repeat", False):
            my_idx = my_idx % len(self.images)
        self.images_idx += 1

        if my_idx >= len(self.images):
            return False, None

        if self.images[my_idx] is None:
            self.images[my_idx] = cv2.imread(self.image_sequence_sources[my_idx])
        return True, self.images[my_idx]

    def update_image(self):
        stime = time.time()

        if self._type == "video":
            self.video_reader_update_image()
        elif self._type == "sequence":
            self.image_sequence_update_image()
        elif self._type == "camera":
            self.camera_update_image()

        etime = time.time()
        elapsed_time = etime - stime
        self.update_fps = 1.0 / elapsed_time if elapsed_time != 0 else -1.0


    def update_loop(self):
        cap_fps = 0

        if self.get("cap_fps", None) is not None:
            cap_fps = self.get("cap_fps", None)
        elif self._type == "video":
            cap_fps = self.video_reader.get(vpl.defines.cap_prop_lookup["FPS"])

        self.cap_fps = cap_fps

        while True:
            try:
                st = time.time()
                self.update_image()
                et = time.time()
                dt = et - st
                if cap_fps is not None and cap_fps > 0:
                    if dt > 0 and dt < 1.0 / cap_fps:
                        time.sleep(1.0 / cap_fps - dt)
            except:
                pass

    def set_camera_props(self):
        props = self["properties"]
        if props != None:
            for p in props.props:
                #print ("setting: " + str(cap_prop_lookup[p]) + " to: " + str(type(props[p])))
                self.camera.set(cap_prop_lookup[p], props[p])

    def get_image(self):
        if not self.is_async:
            self.update_image()
        return self.camera_image

    def process(self, pipe, image, data):
        if not hasattr(self, "has_init"):
            # first time running, default camera
            self.has_init = True

            # default async is false
            self.is_async = self.get("async", False)

            source = self.get("source", 0)

            self._source = source

            # default images
            self.camera_flag, self.camera_image = True, np.zeros((320, 240, 3), np.uint8)

            if isinstance(source, int) or source.isdigit():
                if not isinstance(source, int):
                    source = int(source)
                # create camera
                self.camera = cv2.VideoCapture(source)
                self.set_camera_props()

                self._type = "camera"

            elif isinstance(source, str):
                _, extension = os.path.splitext(source)
                extension = extension.replace(".", "").lower()
                if extension in vpl.defines.valid_image_formats:
                    # have an image sequence
                    self.image_sequence_sources = glob.glob(source)
                    self.images = [None] * len(self.image_sequence_sources)
                    self.images_idx = 0

                    self._type = "sequence"
                
                elif extension in vpl.defines.valid_video_formats:
                    # read from a video file
                    self.video_reader = cv2.VideoCapture(source)
                    self._type = "video"
                else:
                    raise Exception("unknown source type:" + str(source))

            else:
                # use an already instasiated camera
                self.camera = source
                self.set_camera_props()
                self._type = "camera"

            for i in range(self.get("burn", 1)):
                self.update_image()

            if self.is_async:
                self.do_async(self.update_loop)


        image = self.get_image()

        #data["camera_flag"] = flag
        if hasattr(self, "camera_fps"):
            data["camera_" + str(self._source) + "_fps"] = self.camera_fps

        if hasattr(self, "cap_fps") and self.cap_fps is not None and self.cap_fps > 0:
            data["cap_fps"] = self.cap_fps

        if image is None:
            pipe.quit()

        return image, data




class VideoSaver(VPL):
    """

    Usage: VideoSaver(path="data/{num}.png")

      * "path" = image format, or video file (.mp4 or .avi)


    optional arguments:
    
      * "every" = save every N frames (default 1 for every frame)

    Saves images as they are received to their destination

    """

    def register(self):
        self.available_args["path"] = "string path like (data/{num}.png) or video file like (data/mine.mp4)"
        self.available_args["every"] = "integer number of saving one every N frames (default is 1, every frame)"
        self.available_args["fps"] = "frames per second to write to video file(default 24)"

    def end(self):
        if hasattr(self, "video_out"):
            self.video_out.release()


    def save_image(self, image, num):
        if self._type == "video":
            if not hasattr(self, "last_time") or time.time() - self.last_time >= 1.0 / self.fps:
                self.video_out.write(image)
                self.last_time = time.time()

        elif self._type == "sequence":
            
            loc = pathlib.Path(self["path"].format(num="%08d" % num))

            cv2.imwrite(str(loc), image)


    def process(self, pipe, image, data):
        if not hasattr(self, "num"):
            self.num = 0

            self.is_async = self.get("async", True)

            _, ext = os.path.splitext(self["path"])
            if ext.replace(".", "") in vpl.defines.valid_video_formats:
                self._type = "video"

                h, w, d = image.shape
                cc_text = self.get("fourcc", "X264")
                self.fourcc = cv2.VideoWriter_fourcc(*cc_text)
                if "cap_fps" in data.keys():
                    self.fps = data["cap_fps"]
                else:
                    self.fps = self.get("fps", 24.0)
                self.video_out = cv2.VideoWriter(self["path"], self.fourcc, self.fps, (w, h))

                loc = pathlib.Path(self["path"])
                if not loc.parent.exists():
                    loc.parent.mkdir(parents=True)

            else:
                self._type = "sequence"
                
                _loc = pathlib.Path(self["path"])

                if not _loc.parent.exists():
                    _loc.parent.mkdir(parents=True)

        
        if self.num % self.get("every", 1) == 0:

            # async save it
            if self.is_async:
                self.do_async(self.save_image, (image.copy(), self.num))
            else:
                self.save_image(image, self.num)

        self.num += 1

        return image, data


class Display(VPL):
    """

    Usage: Display(title="mytitle")

        * "title" = the window title

    """

    def register(self):
        self.available_args["title"] = "opencv window title"

    def process(self, pipe, image, data):

        cv2.imshow(self["title"], image)
        cv2.waitKey(1)

        return image, data
