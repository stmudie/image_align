from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError

import numpy as np
from StringIO import StringIO
from PIL import Image
import cPickle as Pickle
from json import dumps

class AppSession(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):

        ## SUBSCRIBE to a topic and receive events
        def on_power(msg):
            self.serve_pil_image(power=msg)

        sub = yield self.subscribe(on_power, 'as.saxs.align.power')


    def byte_scale(self, data, floor=None, ceiling=None):

        if floor is not None:
            data[data < floor] = floor
        min_val = np.min(data)

        if ceiling is not None:
            data[data > ceiling] = ceiling
        max_val = np.max(data)

        return np.round(255.0 * (data - min_val) / (max_val - min_val - 1.0)).astype(np.uint8)

    def module_mask(self, vert_gap=7, horiz_gap=17):
        height = 1043
        width = 981

        num_v_gaps = 1
        num_h_gaps = 4

        module_width = (width-vert_gap*num_v_gaps)/(num_v_gaps+1)
        module_height = (height-horiz_gap*num_h_gaps)/(num_h_gaps+1)

        mask = np.ones((height, width))

        for i in range(1, num_v_gaps + 1):
            mask[:, i*module_width+(i-1)*vert_gap:i*(module_width+vert_gap)] = 0

        for i in range(1, num_h_gaps + 1):
            mask[i*module_height+(i-1)*horiz_gap:i*(module_height+horiz_gap), :] = 0

        return mask

    def image_gap_scale(self, image, x_offset=None, y_offset=None, vert_gap=7, horiz_gap=17):

        scale_mask = self.module_mask(vert_gap=vert_gap, horiz_gap=horiz_gap)

        if x_offset is None:
            x_offset = vert_gap
        if y_offset is None:
            y_offset = horiz_gap

        scale_mask_sum = np.copy(scale_mask)
        scale_mask_sum += self.image_offset(scale_mask, x_offset, -y_offset)
        scale_mask_sum += self.image_offset(scale_mask, -x_offset, y_offset)

        scale_mask_sum[np.where(scale_mask_sum == 0)] = 1

        return image*(3/scale_mask_sum)

    def image_offset(self, image, x_offset=0, y_offset=0):
        image = np.roll(image, y_offset, 0)
        image = np.roll(image, x_offset, 1)
        return image

    def image_data(self, image_path, x_offset=0, y_offset=0):
        data = np.reshape(np.array(Image.open(image_path).getdata()), (1043, 981))
        return self.image_offset(data, x_offset, y_offset)

    def serve_pil_image(self, power=1):
        ur_data = self.image_data("/home/mudies/garveygaps/1_2_1_ambient_CUR__0364.tif", 7, -17)
        cr_data = self.image_data("/home/mudies/garveygaps/1_2_1_ambient_CCR__0364.tif")
        ll_data = self.image_data("/home/mudies/garveygaps/1_2_1_ambient_CLL__0364.tif", -7, 17)

        ur_data *= self.image_offset(self.module_mask(11, 25), 7, -17)
        cr_data *= self.module_mask(11, 25)
        ll_data *= self.image_offset(self.module_mask(11, 25), -7, 17)

        data_summed = (ur_data + cr_data + ll_data)
        data_summed[np.where(data_summed < 0)] = 0
        data_scaled = self.image_gap_scale(data_summed, x_offset=7, y_offset=17, vert_gap=11, horiz_gap=25)

        pil_img_save = Image.new("I", (981, 1043))
        pil_img_save.putdata(list(np.reshape(data_scaled,(981*1043,))))
        pil_img_save.save("/home/mudies/garveygaps/1_2_1_ambient_C_0364.tif", "TIFF")



        data_scaled **= power

        data = np.reshape(self.byte_scale(data_scaled, 0, 150), (981*1043,))

        pil_img = Image.new("I", (981, 1043))
        pil_img.putdata(list(data))
        pil_img = pil_img.convert("L")
        img_io = StringIO()
        pil_img.save(img_io, format="PNG")
        img_io.seek(0)
        self.publish('com.example.image', img_io.getvalue().encode("base64"))

    def serve_pil_histogram(self, pil_img):
        img_data = np.array(pil_img.getdata())
        sort = np.sort(img_data)
        print sort[-1000]
        hist = np.histogram(sort[:-1000], bins=np.max(sort[:-1000]))
        data = {'hist': list(hist[0][1:])}
        print len(data['hist'])
        self.publish('com.example.histdata', data)