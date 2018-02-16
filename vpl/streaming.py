"""

for streaming things as a video

"""

from vpl import VPL

import time

from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn

import cv2
import numpy as np


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    def update_image(self, image):
        self.RequestHandlerClass.image = image

    def update_pipe(self, pipe):
        self.RequestHandlerClass.pipe = pipe

class MJPGStreamHandle(BaseHTTPRequestHandler):
    """

    handles web requests for MJPG

    """

    def do_GET_MJPG(self):
        if not hasattr(self, "image"):
            return

        print (self.path)

        self.send_response(200)
        self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
        self.end_headers()
        while True:
            # MAKE sure this refreshes the image every time
            im = self.image.copy()

            # encode image
            cv2s = cv2.imencode('.jpg', im)[1].tostring()

            # write a jpg
            self.wfile.write("--jpgboundary".encode())
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Content-length', str(len(cv2s)).encode())
            self.end_headers()
            self.wfile.write(cv2s)
            #self.wfile.write("<body>hello</body>".encode('utf-8'))
            while np.array_equal(self.image, im):
                time.sleep(0.01)

    def do_GET_HTML(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write("""
        <html>
            <head></head>
            <body>
            <img src="
            />
            </body>
        </html>
        """.encode())

    def do_GET(self):
        #self.send_response(200)
        #self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        #self.end_headers()

        if self.path.endswith('.html'):
            self.do_GET_HTML()
        else:
            self.do_GET_MJPG()
            

class MJPGServer(VPL):
    """

    Usage: MJPGServer(port=5802, fps_cap=None)

      * "port" = the port to host it on

    This is code to host a web server

    This only works on google chrome, connect to "localhost:PORT" to see the image. Or, if you are hosting it on another device (such as a raspi), connect like (raspberrypi.local:PORT) in your browser

    """

    def process(self, pipe, image, data):
        if not hasattr(self, "http_server"):
            self.http_server = ThreadedHTTPServer(('0.0.0.0', self["port"]), MJPGStreamHandle)
            self.http_server.daemon_threads = True
            self.do_async(self.http_server.serve_forever)

        self.http_server.update_pipe(pipe)
        self.http_server.update_image(image.copy())

        return image, data

