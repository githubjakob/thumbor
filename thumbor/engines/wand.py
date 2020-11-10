#!/usr/bin/env python
# -*- coding: utf-8 -*-

# thumbor imaging service - graphicsmagick engine
# https://github.com/thumbor/graphicsmagick-engine

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2014 globo.com timehome@corp.globo.com

from wand.image import (
    Image, Blob, FilterTypes,
    Color, InterlaceType, CompositeOperator as co
)
from wand.api import Draw
from wand._pgmagick import get_blob_data

from thumbor.engines import BaseEngine
from thumbor.utils import deprecated

FORMATS = {
    '.jpg': 'JPEG',
    '.jpeg': 'JPEG',
    '.gif': 'GIF',
    '.png': 'PNG'
}


class Engine(BaseEngine):

    def gen_image(self, size, color_value):
        color = Color(str(color_value))
        if not color.isValid():
            raise ValueError('Color %s is not valid.' % color_value)
        return Image(*size, color)

    def create_image(self, buffer):
        return Image(blob=buffer)

    @property
    def size(self):
        size = self.image.size()

        return (size.width(), size.height())

    def resize(self, width, height):
        self.image.zoom('%dx%d!' % (width, height))

    def crop(self, left, top, right, bottom):
        self.image.crop(
            left=int(left), top=int(top), right=int(right), bottom=int(bottom)
        )

    def flip_vertically(self):
        self.image.flip()

    def flip_horizontally(self):
        self.image.flop()

    def read(self, extension=None, quality=None):
        if quality is None:
            quality = self.context.config.QUALITY

        #returns image buffer in byte format.
        img_buffer = Blob()

        ext = extension or self.extension
        try:
            self.image.magick(FORMATS[ext])
        except KeyError:
            self.image.magick(FORMATS['.jpg'])

        if ext == '.jpg':
            self.image.interlaceType(InterlaceType.LineInterlace)
            self.image.quality(quality)
            f = FilterTypes.CatromFilter
            self.image.filterType(f)

        self.image.write(img_buffer)

        return img_buffer.data

    @deprecated("Use image_data_as_rgb instead.")
    def get_image_data(self):
        self.image.magick(self.get_image_mode())
        blob = Blob()
        self.image.write(blob)
        data = get_blob_data(blob)
        return data

    def set_image_data(self, data):
        self.image.magick(self.get_image_mode())
        blob = Blob(data)
        self.image.size(self.image.size())
        self.image.read(blob)

    @deprecated("Use image_data_as_rgb instead.")
    def get_image_mode(self):
        if self.alpha_channel:
            return "RGBA"
        return "RGB"

    def image_data_as_rgb(self, update_image=True):
        # TODO: Handle other image formats
        return self.get_image_mode(), self.get_image_data()

    def draw_rectangle(self, x, y, width, height):
        draw = Draw()
        draw.fill_opacity(0.0)
        draw.stroke_color('white')
        draw.stroke_width(1)

        draw.rectangle(x, y, x + width, y + height)
        self.image.draw(draw.drawer)

    def paste(self, other_engine, pos, merge=True):
        self.enable_alpha()
        other_engine.enable_alpha()

        operator = co.OverCompositeOp if merge else co.CopyCompositeOp
        self.image.composite(other_engine.image, pos[0], pos[1], operator)

    def enable_alpha(self):
        self.image.type("truecoloralpha")

    def strip_icc(self):
        self.image.iccColorProfile(Blob())

    def convert_to_grayscale(self):
        self.image.type("grayscalealpha")
        self.image.quantizeColorSpace("gray")
        self.image.quantize()
