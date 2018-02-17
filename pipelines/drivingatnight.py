"""

This is for a personal project, but shows how to process an image

"""

# this is to remove night-like noise
pipe.add_vpl(Bilateral(s_color=15, s_space=21))

# cool vhs effect
pipe.add_vpl(CoolChannelOffset(w=lambda i: 46 * i))

# vhs cont
pipe.add_vpl(Scanlines(size=7.0, frequency=1.8, speed=0.8))


