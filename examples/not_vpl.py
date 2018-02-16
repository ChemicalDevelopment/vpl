"""

Non VPL simple camera viewer

"""

import cv2
import argparse
import time

parser = argparse.ArgumentParser(description='webcam viewer')

parser.add_argument("source", nargs='?', default=0, type=int, help='camera source (can be video file)')

parser.add_argument("-s", "--size", default=None, type=int, nargs=2, help='size')
parser.add_argument("-np", "--no-prop", action='store_true', help='use this flag to not use CameraProperties')

args = parser.parse_args()


src = cv2.VideoCapture(args.source)


# set preferred width and height
if args.size is not None and not args.no_prop:
    src.set(cv2.CAP_PROP_FRAME_WIDTH, args.size[0]) 
    src.set(cv2.CAP_PROP_FRAME_HEIGHT, args.size[1])

#time.sleep(2)
src.set(cv2.CAP_PROP_AUTO_EXPOSURE, .25)
src.set(cv2.CAP_PROP_EXPOSURE, 0.1)

while True:
    _, img = src.read()
    print(img.shape)

    cv2.imshow("window", img)

    k = cv2.waitKey(1)

    if k != -1:
        break

