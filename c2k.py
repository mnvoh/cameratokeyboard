import asyncio
import sys


from cameratokeyboard.config import Config
from cameratokeyboard.args import parse_args
from cameratokeyboard.app import App

args = parse_args(sys.argv[1:])


async def main():
    app = App(Config.from_args(args))
    await app.run()


if __name__ == "__main__":
    if args.get("command") is not None:
        args.get("command")().run()
    else:
        asyncio.run(main())
