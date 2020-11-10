from os.path import abspath, dirname, join
from unittest import TestCase
from preggy import expect

from io import BytesIO


from thumbor.engines.wand import Engine
from thumbor.engines.pil import Engine as PileEngine
from thumbor.config import Config
from thumbor.context import Context

from wand.image import Image


STORAGE_PATH = abspath(join(dirname(__file__), "../fixtures/images/"))


class WandEngineTestCase(TestCase):

    def get_context(self):
        cfg = Config(
            SECURITY_KEY="ACME-SEC",
            ENGINE="thumbor.engines.wand",
            IMAGE_METADATA_READ_FORMATS="exif,xmp",
        )
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = STORAGE_PATH
        cfg.STORAGE = "thumbor.storages.no_storage"

        return Context(config=cfg)

    def setUp(self):
        self.context = self.get_context()

    def test_create_engine(self):
        engine = Engine(self.context)
        expect(engine).to_be_instance_of(Engine)

    def test_create_image(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        engine.load(buffer, None)
        expect(engine.image.format).to_equal("JPEG")

    def test_create_image_16bit_per_channel_lsb(self):
        engine = Engine(self.context)
        with open(
            join(STORAGE_PATH, "gradient_lsb_16bperchannel.tif"), "rb"
        ) as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        expect(engine.image.format).to_equal("TIFF")
        expect(engine.image.size).to_equal((100, 100))

    def test_load_tif_8bit_per_channel(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "gradient_8bit.tif"), "rb") as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)
        engine.load(buffer, None)

        expect(engine.image.format).to_equal("TIFF")
        expect(engine.image.size).to_equal((100, 100))

    def test_set_image_data_JPG(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "image.jpg"), "rb") as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)

        engine.load(buffer, None)

        engine.set_image_data(buffer)

        expect(engine.image.format).to_equal("JPEG")
        expect(engine.image.size).to_equal((300, 400))

    def test_set_image_data_PNG(self):
        engine = Engine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)

        engine.load(buffer, None)

        engine.set_image_data(buffer)

        expect(engine.image.format).to_equal("PNG")
        expect(engine.image.size).to_equal((691, 212))

    def test_compare_image_data_and_mode(self):
        engine = Engine(self.context)
        pil_engine = PileEngine(self.context)
        with open(join(STORAGE_PATH, "1bit.png"), "rb") as image_file:
            buffer = image_file.read()
        expect(buffer).not_to_equal(None)

        engine.load(buffer, '.png')
        pil_engine.load(buffer, '.png')

        pil_mode, pil_data = pil_engine.image_data_as_rgb()
        mode, data = engine.image_data_as_rgb()

        expect(mode).to_equal(pil_mode)
        expect(data).to_length(len(pil_data))
        expect(data[:100]).to_equal(pil_data[:100])
        expect(data[-100:]).to_equal(pil_data[-100:])
