from os.path import join

from tornado.testing import gen_test

from . import EngineCase
from .urls_helpers import UrlsTester, single_dataset


class WandTest(EngineCase):
    engine = "thumbor.engines.wand"

    @gen_test
    async def test_single_params(self):
        if not self._app:
            return True
        group = list(single_dataset(False))  # FIXME: remove False
        count = len(group)
        tester = UrlsTester(self.http_client)

        print("Requests count: %d" % count)
        for options in group:
            joined_parts = join(*options)
            url = "unsafe/%s" % joined_parts
            await tester.try_url(self.get_url(f"/{url}"))

        tester.report()
