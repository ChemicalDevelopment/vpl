"""

This is ran as straight code (i.e. in eval() code)

Some defined things are:

 `pipe` -> a vpl.Pipeline instance that you should call .add_vpl on

"""


class NlMeans(VPL):
    def process(self, pipe, image, data):
        #return cv2.fastNlMeansDenoisingColoredMulti(self.buffer, len(self.buffer) // 2, len(self.buffer), None, 4, 3, 5), data
        return cv2.fastNlMeansDenoisingColored(image,None, 14, 14, 19, 15), data

pipe.add_vpl(Bilateral(s_color=20, s_space=40))

