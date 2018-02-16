
import sys
import os

import math

import argparse

parser = argparse.ArgumentParser(description='webcam viewer')

parser.add_argument("source", nargs='?', default=0, help='camera source (can be video file)')
parser.add_argument("-s", "--size", default=None, type=int, nargs=2, help='size')
parser.add_argument("-e", "--exposure", default=None, type=float, help='exposure settings')
parser.add_argument("-so", "--source-output", default=None, help='output raw webcam feed')
parser.add_argument("-ns", "--no-show", action='store_true', help='use this flag to not show')
parser.add_argument("-np", "--no-prop", action='store_true', help='use this flag to not use CameraProperties')
parser.add_argument("--dev", action='store_true', help='developer (non-install) flag')
parser.add_argument("-o", "--output", default=None, help='output file')

args = parser.parse_args()

if args.dev:
    sys.path.append(os.getcwd())

import vpl

# this line makes it easier
from vpl.all import *

pipe = Pipeline("pipe")


# input
vsrc = VideoSource(source=args.source)

pipe.add_vpl(vsrc)

pipe.add_vpl(PrintInfo(fps=2, extended=True))

cam_props = CameraProperties()

cam_props["FPS"] = 60.0

if args.exposure is not None and not args.no_prop:
    #cam_props["AUTO_EXPOSURE"] = args.exposure
    cam_props["EXPOSURE"] = args.exposure

# set preferred width and height
if args.size is not None and not args.no_prop:
    cam_props["FRAME_WIDTH"] = args.size[0]
    cam_props["FRAME_HEIGHT"] = args.size[1]

vsrc["properties"] = cam_props


#if args.size is not None:
#    pipe.add_vpl(Resize(w=args.size[0], h=args.size[1]))

if args.source_output:
    pipe.add_vpl(VideoSaver(path=args.source_output))

# processing here

#pipe.add_vpl(Bleed(N=24))
#pipe.add_vpl(Grayscale())
#pipe.add_vpl(RainbowCrazy())
#pipe.add_vpl(HSLBin())
#pipe.add_vpl(CoolChannelOffset(xoff=lambda i: 6 * i, yoff=0))
#pipe.add_vpl(Grid(w=2, h=2))
#pipe.add_vpl(Roll(w=lambda w, ct: 20 * ct / 24.0, h=lambda h, ct: 2.5 * ct / 24.0))
#pipe.add_vpl(Pixelate())
#pipe.add_vpl(Scanlines())
#pipe.add_vpl(Diff())

# just output


#pipe.add_vpl(MJPGServer(port=5802))

if not args.no_show:
    pipe.add_vpl(Display(title="window"))

if args.output:
    pipe.add_vpl(VideoSaver(path=args.output))

try:
    # we let our VideoSource do the processing, autolooping
    pipe.process(image=None, data=None, loop=True)
except (KeyboardInterrupt, SystemExit):
    print("keyboard interrupt, quitting")
    exit(0)

