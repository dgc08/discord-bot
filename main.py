import threading

import discord
from pydub import AudioSegment
import requests
from io import BytesIO
from discord.ext import commands

from Playlist import Playlist
from imagine import imagine

with open("discord_api.token") as f:
    for line in f.readlines():
        if line.startswith("#") or line.strip() == "":
            pass
        else:
            token = line.strip()
            print(token)
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
async def play_file(context, song=None, *args):
    if args == [] or args is not None:
        song = song + " " + " ".join(args)
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
    name='imagine',
    description='Generative Image AI powered by Stable Diffusion. If its not working, that might be because my Comfy UI is not running.',
    pass_context=True,
)
async def imagine_call(context, prompt=None, *args):
    channels = [1205261574130892830, 1205261654208811038, 1094293780330463282, 1205264701869785138, 922766999388561460, 1205461984489906196]
    channels_to_not_scan = [1205264701869785138, 1205261654208811038,]
    if context.channel.id not in channels:
        await context.send("You cannot use this function here.")
        return
    if args == [] or args is not None:
        prompt = prompt + " " + " ".join(args)

    batch_count = 1
    negative_prompt = ""
    style = "base_workflow"
    if "/" in prompt:
        splitted = prompt.split("/")
        prompt = splitted[0]


        for i in splitted[1:]:
            i = i.strip()
            try:
                batch_count = int(i)
                continue
            except ValueError:
                pass

            if i.lower().startswith ("negative:") or i.lower().startswith ("n:"):
                negative_prompt = i.split(":")[1].strip()
            else:
                style = i

    prompt = prompt + " "

    if context.channel.id not in channels_to_not_scan:
        await imagine(context, prompt, negative_prompt, style, batch_count, True)
    else:
        await imagine(context, prompt, negative_prompt, style, batch_count)

@bot.command(
    name='play',
    description='Plays a yt lol',
    pass_context=True,
)
async def play(context, song=None, *args):
    print("play called")
    if args == [] or args is not None:
        song = song + " " + " ".join(args)
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
        try:
            user_input = input(">>> ")
        except KeyboardInterrupt:
            exit()
        if user_input == "exit":
            break
        else:
            try:
                exec(user_input)
            except Exception as e:
                print(e)
