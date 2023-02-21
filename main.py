import os
from asyncio import sleep as asyncsleep
from Playlist import Playlist

import threading
from discord.ext import commands
import discord
from os.path import exists as file_exists
from os import system
from os import remove

with open("discord_api.token") as f:
    token = f.read()

playlist = Playlist()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)


@bot.command(
    name='load',
    description='Downloads a mp3 file from deine röhre (übersetze auf englisch lol) lol',
    pass_context=True, )
async def load(ctx, link=None, name=None):
    if link is None or name is None:
        await ctx.send("Ju häve tu spesifei se link änd se neime of se feil.")
        return
    filename = "load\\" + name
    if file_exists("..\\" + filename):
        await ctx.send("Sät feil alredi exists.")
        return
    await ctx.send("Downloading...")

    out = system("yt-dlp.exe " + link + " -o ..\\" + filename)
    print(out)

    if out != 0:
        await ctx.send("Errör daunloding video.")
        return
    system("ffmpeg -i " + "..\\" + filename + ".webm -vn -ab 128k -ar 48000 -y ..\\" + filename + ".mp3")
    remove("..\\" + filename + ".webm")

    await ctx.send("Download complete... Song name: {}.mp3".format(filename.replace("\\", "/")))


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
        await playlist.play(song, voice_channel, ctx)

    else:
        await ctx.send('Ai kant plei miusik in ä text tschännel')

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
        await playlist.play_yt(song + '  --default-search "ytsearch"', voice_channel, ctx)

    else:
        await ctx.send('Ai kant plei miusik in ä text tschännel')


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
        await playlist.play_raw(song, voice_channel, ctx)

    else:
        await ctx.send('Ai kant plei miusik in ä text tschännel')


def run_bot():
    bot.run(token)


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
