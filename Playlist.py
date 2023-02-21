import discord
from asyncio import sleep as asyncsleep
import subprocess


def get_out(com):
    # Run the command and capture its output
    p = subprocess.Popen(com, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, errors = p.communicate()

    # Convert the byte string to a regular string
    output_str = output.decode('utf-8')

    # Print the output
    return output_str


class Playlist:
    lst = {}
    vcs = {}
    infos = {}

    async def play(self, song, voice_channel, ctx):
        await self.play_raw('..\\' + song.replace("/", "\\"), voice_channel, ctx)

    async def play_yt(self, song, voice_channel, ctx):
        link = None

        out = get_out("yt-dlp --list-formats {link}".format(link=song)).split("--\n")[1].split("\n")

        i = 0
        f = False

        while not f:
            if "video only" not in out[i] and "image" not in out[i] and "low" not in out[i]:
                f = out[i].split(" ")[0]
            i += 1

        link = get_out("yt-dlp -f {form} -g {link}".format(form=f, link=song))
        print(link)

        await self.play_raw(link, voice_channel, ctx)

    async def play_raw(self, song, voice_channel, ctx):
        if voice_channel not in self.vcs:
            self.vcs[voice_channel] = await voice_channel.connect()
            self.lst[voice_channel] = [song]
            self.infos[voice_channel] = ctx.message.channel

            await self.play_song(song, voice_channel)
        elif voice_channel in self.vcs and not self.vcs[voice_channel].is_connected():
            self.lst.pop(voice_channel)
            self.vcs.pop(voice_channel)
            try:
                self.infos.pop(voice_channel)
            except KeyError:
                pass
            await self.play(song, voice_channel,ctx)
        else:
            self.lst[voice_channel].append(song)
            self.infos[voice_channel] = ctx.message.channel

    async def wait_for_song_end(self, voice_channel):
        while self.vcs[voice_channel].is_playing():
            await asyncsleep(1)
        # disconnect after the player has finished
        await self.skip(voice_channel)

    async def play_song(self, song, voice_channel):
        self.vcs[voice_channel].play(discord.FFmpegPCMAudio(song, options="-vn"))
        self.vcs[voice_channel].pause()
        await asyncsleep(1)
        self.vcs[voice_channel].resume()
        self.lst[voice_channel].pop(0)
        await self.infos[voice_channel].send("Now playing: **{song}**".format(song=song.replace("..\\", "")))
        await self.wait_for_song_end(voice_channel)

    async def skip(self, voice_channel):
        self.vcs[voice_channel].stop()

        if not self.lst[voice_channel]:
            await self.stop(voice_channel)
        else:
            await self.play_song(self.lst[voice_channel][0], voice_channel)

    async def stop(self, voice_channel):
        self.vcs[voice_channel].stop()

        self.lst.pop(voice_channel)
        self.infos.pop(voice_channel)
        await self.vcs[voice_channel].disconnect()
        self.vcs.pop(voice_channel)
