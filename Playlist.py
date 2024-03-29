import discord
from asyncio import sleep as asyncsleep
from yt_dlp import YoutubeDL

class Playlist:
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -b:a 64k -bufsize 2048k'}
    lst = {}
    info_dicts = {}
    vcs = {}
    infos = {}

    @staticmethod
    def get_audio_yt_link(link_yt):

        ydl_opts = {'extract_flat': 'discard_in_playlist',
         'default_search': "ytsearch",
         'noplaylist': True,
         'format': 'bestaudio[ext=m4a],bestaudio[ext=webm]',
         'fragment_retries': 10,
         'ignoreerrors': 'only_download',
         'postprocessors': [{'key': 'FFmpegExtractAudio',
                             'nopostoverwrites': False,
                             'preferredcodec': 'best',
                             'preferredquality': '5'},
                            {'key': 'FFmpegConcat',
                             'only_multi_video': True,
                             'when': 'playlist'}],
         'retries': 10}
        with YoutubeDL(ydl_opts) as ydl:
            print (link_yt)
            link = ydl.extract_info(link_yt, download=False)
        return link

    async def play_yt(self, song, voice_channel, ctx):
        infos = Playlist.get_audio_yt_link(song)
        await self.play_raw(infos["url"], voice_channel, ctx, infos)

    async def play_raw(self, song, voice_channel, ctx, infos):
        try:
            if voice_channel not in self.vcs:
                print("we connect")
                self.vcs[voice_channel] = await voice_channel.connect()
                print("we connected")
                self.lst[voice_channel] = [song]
                self.info_dicts[voice_channel] = [infos]
                self.infos[voice_channel] = ctx.message.channel
                await self.play_song(song, voice_channel)
            elif voice_channel in self.vcs and not self.vcs[voice_channel].is_connected():
                self.lst.pop(voice_channel)
                self.info_dicts.pop(voice_channel)
                self.vcs.pop(voice_channel)
                try:
                    self.infos.pop(voice_channel)
                except KeyError:
                    pass
                await self.play_raw(song, voice_channel, ctx)
            else:
                self.lst[voice_channel].append(song)
                self.info_dicts[voice_channel].append(infos)
                self.infos[voice_channel] = ctx.message.channel
        except Exception as e:
            print(f"An error occurred: {e}")

    async def wait_for_song_end(self, voice_channel):
        while self.vcs[voice_channel].is_playing():
            await asyncsleep(1)
        await self.skip(voice_channel)

    async def play_song(self, song, voice_channel):
        print("play_soing called", song, self.info_dicts[voice_channel][0])
        if "http" in song:
            self.vcs[voice_channel].play(discord.FFmpegPCMAudio(song, **Playlist.FFMPEG_OPTIONS))
        else:
            self.vcs[voice_channel].play(discord.FFmpegPCMAudio(song, options='-vn -b:a 64k -bufsize 2048k'))
        self.vcs[voice_channel].pause()
        await asyncsleep(1)
        self.vcs[voice_channel].resume()
        self.lst[voice_channel].pop(0)
        info_entry = self.info_dicts[voice_channel][0]
        self.info_dicts[voice_channel].pop(0)
        await self.infos[voice_channel].send("Now playing: **{song}**".format(song=info_entry["title"]))
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
        self.info_dicts.pop(voice_channel)
        self.infos.pop(voice_channel)
        await self.vcs[voice_channel].disconnect()
        self.vcs.pop(voice_channel)
