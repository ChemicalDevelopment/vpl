
import vpl

# this line makes it easier
from vpl.all import *

import math


pipe = Pipeline("mypipe")

size = 640, 480

cam_props = CameraProperties()

# set preferred width and height
cam_props["FRAME_WIDTH"] = size[0]
cam_props["FRAME_HEIGHT"] = size[1]

# input

pipe.add_vpl(VideoSource(source=0))#, properties=cam_props))
#pipe.add_vpl(VideoSource(source="recording.avi"))#, properties=cam_props))

pipe.add_vpl(Resize(w=size[0], h=size[1]))

#pipe.add_vpl(VideoSaver(path="recording.avi"))


# processing here


#pipe.add_vpl(Bleed(N=24))
#pipe.add_vpl(Grayscale())
#pipe.add_vpl(RainbowCrazy())
#pipe.add_vpl(HSLBin())
#pipe.add_vpl(CoolChannelOffset(xoff=lambda i: 6 * i, yoff=0))
#pipe.add_vpl(Grid(w=2, h=2))
#pipe.add_vpl(Roll(w=lambda w, ct: w / 2.0 + ct * 12, h=lambda h, ct: 10 * math.sin(2 * math.pi * h / 120 + ct * 6) + ct * 4))
#pipe.add_vpl(Pixelate())
#pipe.add_vpl(Scanlines())

# just output

#pipe.add_vpl(PrintInfo(fps=2, extended=True))

#pipe.add_vpl(MJPGServer(port=5802))

pipe.add_vpl(Display(title="window"))


try:
    # we let our VideoSource do the processing, autolooping
    pipe.process(image=None, data=None, loop=True)
except (KeyboardInterrupt, SystemExit):
    print("keyboard interrupt, quitting")
    exit(0)

