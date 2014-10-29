from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, send_file, jsonify
from flask.ext.socketio import SocketIO, emit


import numpy as np
from StringIO import StringIO
from PIL import Image

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'blah'
socketio = SocketIO(app)


class Align(object):
    def __init__(self):
        pass

    def byte_scale(self, data, floor=None, ceiling=None):

        if floor is not None:
            data[data < floor] = floor
        min_val = np.min(data)

        if ceiling is not None:
            data[data > ceiling] = ceiling
        max_val = np.max(data)

        return np.round(255.0 * (data - min_val) / (max_val - min_val - 1.0)).astype(np.uint8)

    def image_gap_scale(self, image, x_offset=None, Y_offset=None):
        height = 1043
        width = 981

        vert_gap = 7
        horiz_gap = 17

        num_v_gaps = 1
        num_h_gaps = 4

        if x_offset is None:
            x_offset = vert_gap
        if y_offset is None:
            y_offset = horiz_gap




        scale_mask = np.ones((width, height))

        for i in range(4):
            scale_mask[i]


        image[]


    def image_data(self, image_path, x_offset=0, y_offset=0):
        data = np.reshape(np.array(Image.open(image_path).getdata()), (1043, 981))
        data = np.roll(data, x_offset, 0)
        data = np.roll(data, y_offset, 1)
        return data

    def serve_pil_image(self):
        ur_data = self.image_data("/home/mudies/garveygaps/1_2_1_ambient_CUR__0364.tif", 17, 7)
        cr_data = self.image_data("/home/mudies/garveygaps/1_2_1_ambient_CCR__0364.tif")
        ll_data = self.image_data("/home/mudies/garveygaps/1_2_1_ambient_CLL__0364.tif", -17, 7)

        data_summed = (ur_data + cr_data + ll_data)
        data_summed[np.where(data_summed < 0)] = 0
        data_summed **= .2

        data = np.reshape(align.byte_scale(data_summed, 3, 15), (981*1043,))

        pil_img = Image.new("I", (981, 1043))
        pil_img.putdata(list(data))
        pil_img = pil_img.convert("L")
        img_io = StringIO()
        pil_img.save(img_io, format="PNG")
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

    def serve_pil_histogram(self, pil_img):
        img_data = np.array(pil_img.getdata())
        sort = np.sort(img_data)
        print sort[-1000]
        hist = np.histogram(sort[:-1000], bins=np.max(sort[:-1000]))
        data = {'hist': list(hist[0][1:])}
        print len(data['hist'])
        return jsonify(data)


@app.route('/')
def hello_world():
    return render_template('align_image.html')


@app.route('/image')
def image():
    return align.serve_pil_image()


if __name__ == '__main__':
    align = Align()
    socketio.run(app)
