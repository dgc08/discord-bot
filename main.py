import subprocess
import threading
from os import remove
from os import system
from os.path import exists as file_exists

import discord
from pydub import AudioSegment
import requests
from io import BytesIO
from discord.ext import commands

from Playlist import Playlist

with open("discord_api.token") as f:
    for line in f.readlines():
        if line.startswith("#") or line.strip() == "":
            pass
        else:
            token = line
            break

playlist = Playlist()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)

async def webm_to_mp3(url):
    # Get the webm file from the URL
    response = requests.get(url)
    webm_data = response.content

    # Convert webm data to AudioSegment
    webm_audio = AudioSegment.from_file(BytesIO(webm_data), format="webm")

    # Export AudioSegment as mp3
    mp3_data = BytesIO()
    webm_audio.export(mp3_data, format="mp3")

    return mp3_data.getvalue()

@bot.command(
    name='load',
    description='Downloads a mp3 file from deine röhre (übersetze auf englisch lol) lol',
    pass_context=True, )
async def load(ctx, link=None):
    if link is None:
        await ctx.send("Ju häve tu spesifei se link.")
        return
    await ctx.send("Downloading...")

    resource = Playlist.get_audio_yt_link(link)

    print(resource["url"])
    print(resource["title"])

    mp3_data = await webm_to_mp3(resource["url"])
    print("got data")

    # Upload the mp3 file to Discord
    await ctx.send(file=discord.File(BytesIO(mp3_data), filename=resource["title"]))



@bot.command(
    name='stop',
    description='stops the player',
    pass_context=True, )
async def stop(ctx):
    voice_channel = ctx.message.author.voice
    # only play music if user is in a voice channel
    if voice_channel != None:
        voice_channel = voice_channel.channel
        await playlist.stop(voice_channel)
    else:
        await ctx.send('Ai kant stop miusik in ä text tschännel')


@bot.command(
    name='skip',
    description='stops the player',
    pass_context=True, )
async def skip(ctx):
    voice_channel = ctx.message.author.voice
    # only play music if user is in a voice channel
    if voice_channel != None:
        voice_channel = voice_channel.channel
        await playlist.skip(voice_channel)
    else:
        await ctx.send('Ai kant skip miusik in ä text tschännel')


@bot.command(
    name='play_file',
    description='Plays a mp3 file lol',
    pass_context=True,
)
async def play_file(context, song=None):
    file = "..\\" + song
    await play_raw(context, file)

@bot.command(
    name='yt',
    description='Plays a yt lol',
    pass_context=True,
)
async def yt(context, song=None):
    ctx = context
    global playlist

    if song is None:
        await ctx.send("plis tel mi a song näme")
        return
    # grab the user who sent the command
    voice_channel = context.message.author.voice
    # only play music if user is in a voice channel
    if voice_channel != None:
        voice_channel = voice_channel.channel
        await playlist.play_yt(song, voice_channel, ctx)

    else:
        await ctx.send('Ai kant plei miusik in ä text tschännel')


@bot.command(
    name='play',
    description='Plays a yt lol',
    pass_context=True,
)
async def play(context, song=None):
    if "http" in song:
        if "youtube.com/" in song or "youtu.be/" in song:
            await yt(context, song)
        else:
            await play_raw(context, song)


@bot.command(
    name='play_raw',
    description='Plays a mp3 file lol',
    pass_context=True,
)
async def play_raw(context, song=None):
    ctx = context
    global playlist

    if song is None:
        await ctx.send("plis tel mi a song näme")
        return
    # grab the user who sent the command
    voice_channel = context.message.author.voice
    # only play music if user is in a voice channel
    if voice_channel != None:
        voice_channel = voice_channel.channel
        await playlist.play_raw(song, voice_channel, ctx, {"title": song.replace("..\\", "")})

    else:
        await ctx.send('Ai kant plei miusik in ä text tschännel')


def run_bot():
    bot.run(token)

if __name__ == "__main__":
    # run_bot()
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    while True:
        user_input = input(">>> ")
        if user_input == "exit":
            break
        else:
            try:
                exec(user_input)
            except Exception as e:
                print(e)
