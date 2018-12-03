# vpl

Vide Pipe Line


# installation

Run `pip3 install vpl` (it's on pypi)

Or `pip3 install -e git://github.com/chemicaldevelopment/vpl` (for development, i.e. unstable builds)

# usage

You can use `import vpl` in your code

## Commandline

It comes with a simple viewer, run:

`python3 -mvpl video 0`

You can change `0` to higher numbers if you have multiple cameras connected. Or, you can change it to a file name to use the video as input:

`python3 -mvpl video ~/path/video.mp4`

To record, use `-o`:

`python3 -mvpl video 0 -o tmp/{num}.jpg`

The recording to video is glitchy, so it is recomended to render to individual frames

# exposure settings

Exposure settings are extremely finicky to get working. Here's a few commands to try:

First, set the auto control cutoff to 1:

`v4l2-ctl -d /dev/video0 -c exposure_auto=1`

Then, try setting the exposure value to various values between -100 and +100:

`v4l2-ctl -d /dev/video0 -c exposure_absolute=-30`

`v4l2-ctl -d /dev/video0 -c exposure_absolute=0`

`v4l2-ctl -d /dev/video0 -c exposure_absolute=0.5`

`v4l2-ctl -d /dev/video0 -c exposure_absolute=20`

The optimal low/medium light setting for the Micro$oft Lifecam is:

`v4l2-ctl -d /dev/video0 -c exposure_absolute=20.9`


Use this command:

`v4l2-ctl --all`

*to print settings (and their defaults). This is the most important v4l command*

Run through setting all these to defaults


Here are the defaults for Micro$oft Lifecam:

```

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

```

 
Use the script `utils/reset_lifecam.sh`

