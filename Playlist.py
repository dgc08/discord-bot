import discord
from asyncio import sleep as asyncsleep

class Playlist:
    lst = {}
    vcs = {}
    infos = {}

    async def play(self, song, voice_channel, ctx):
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
        self.vcs[voice_channel].play(discord.FFmpegPCMAudio('..\\' + song.replace("/", "\\")))
        self.vcs[voice_channel].pause()
        await asyncsleep(1)
        self.vcs[voice_channel].resume()
        self.lst[voice_channel].pop(0)
        await self.infos[voice_channel].send("Now playing: **{song}**".format(song=song))
        await self.wait_for_song_end(voice_channel)

    async def skip(self, voice_channel):
        self.vcs[voice_channel].stop()

        if not self.lst[voice_channel]:
            await self.stop(voice_channel)
        else:
            await self.play_song(self.lst[voice_channel][0], voice_channel)

    async def stop(self, voice_channel):
        self.vcs[voice_channel].stop()
        await self.vcs[voice_channel].disconnect()
