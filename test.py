import asyncio

import Playlist
async def main():
    await Playlist.Playlist.play_yt(None, "https://www.youtube.com/watch?v=dy90tA3TT1c", None, None)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())