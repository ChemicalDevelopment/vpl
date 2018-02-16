#!/bin/bash

: '

Here are the defaults

Streaming Parameters Video Capture:
	Capabilities     : timeperframe
	Frames per second: 30.000 (30/1)
	Read buffers     : 0
                     brightness (int)    : min=30 max=255 step=1 default=133 value=133
                       contrast (int)    : min=0 max=10 step=1 default=5 value=5
                     saturation (int)    : min=0 max=200 step=1 default=83 value=83
 white_balance_temperature_auto (bool)   : default=1 value=1
           power_line_frequency (menu)   : min=0 max=2 default=2 value=2
      white_balance_temperature (int)    : min=2800 max=10000 step=1 default=4500 value=4500 flags=inactive
                      sharpness (int)    : min=0 max=50 step=1 default=25 value=25
         backlight_compensation (int)    : min=0 max=10 step=1 default=0 value=5
                  exposure_auto (menu)   : min=0 max=3 default=1 value=1
              exposure_absolute (int)    : min=5 max=20000 step=1 default=156 value=40
                   pan_absolute (int)    : min=-201600 max=201600 step=3600 default=0 value=0
                  tilt_absolute (int)    : min=-201600 max=201600 step=3600 default=0 value=0
                  zoom_absolute (int)    : min=0 max=10 step=1 default=0 value=0


'

DEVICE="/dev/video0"

v4l2-ctl -d $DEVICE -c brightness=133
v4l2-ctl -d $DEVICE -c contrast=5
v4l2-ctl -d $DEVICE -c saturation=83
v4l2-ctl -d $DEVICE -c white_balance_temperature_auto=1
v4l2-ctl -d $DEVICE -c power_line_frequency=2
v4l2-ctl -d $DEVICE -c white_balance_temperature=4500
v4l2-ctl -d $DEVICE -c sharpness=25

v4l2-ctl -d $DEVICE -c backlight_compensation=0
v4l2-ctl -d $DEVICE -c exposure_auto=1
v4l2-ctl -d $DEVICE -c exposure_absolute=156
v4l2-ctl -d $DEVICE -c pan_absolute=0
v4l2-ctl -d $DEVICE -c tilt_absolute=0
v4l2-ctl -d $DEVICE -c zoom_absolute=0

