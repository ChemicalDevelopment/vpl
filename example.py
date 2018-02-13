
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

pipe.add_vpl(VideoSource(source=0, properties=cam_props))


# processing here

#pipe.add_vpl(Bleed(N=10))
#pipe.add_vpl(Grayscale())
#pipe.add_vpl(RainbowCrazy())
#pipe.add_vpl(HSLBin())
#pipe.add_vpl(CoolChannelOffset(xoff=lambda i: 6 * i, yoff=0))
#pipe.add_vpl(Scanlines())
#pipe.add_vpl(Roll(h=lambda h, ct: 10 * math.sin(2 * math.pi * h / 120 + ct / 12.0)))
#pipe.add_vpl(Pixelate())
#pipe.add_vpl(Grid(w=2, h=2))


# just output

pipe.add_vpl(MJPGServer(port=5802))

pipe.add_vpl(Display(title="window"))


try:
    # we let our VideoSource do the processing, autolooping
    pipe.process(image=None, data=None, loop=True)
except (KeyboardInterrupt, SystemExit):
    print("keyboard interrupt, quitting")
    exit(0)

