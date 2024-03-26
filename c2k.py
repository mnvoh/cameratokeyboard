# pylint: disable=missing-function-docstring
import asyncio
import sys


from cameratokeyboard.config import Config
from cameratokeyboard.args import parse_args
from cameratokeyboard.app import App
from cameratokeyboard.model.model_downloader import ModelDownloader

args = parse_args(sys.argv[1:])


async def async_main():
    config = Config.from_args(args)
    ModelDownloader(config).run()
    await App(config).run()


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    if args.get("command") is not None:
        args.get("command")().run()
    else:
        main()
