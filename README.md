# vpl

Vide Pipe Line


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

