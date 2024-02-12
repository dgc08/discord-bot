import asyncio
import threading
import datetime
import time

import discord
from pydub import AudioSegment
import requests
from io import BytesIO

from Playlist import Playlist
from bot_provider import get_bot
from imagine import imagine, images_count
from chat import check_chat, send_response, add_channel, remove_channel
from chat.FakeConversation import conv

with open("discord_api.token") as f:
    for line in f.readlines():
        if line.startswith("#") or line.strip() == "":
            pass
        else:
            token = line.strip()
            break

playlist = Playlist()

channels = [1205461984489906196, 1205261654208811038, 1205261574130892830, 922766999388561460, 922839879249952809,
            1206352102280929291, 1205264701869785138]
channels_to_not_scan = [1205261654208811038, 922839879249952809, 1206352102280929291, 1205264701869785138]

start_time = time.time()
command_count = 0
response_count = 0

bot = get_bot()


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.invisible)
    print("Ready.")

@bot.event
async def on_message(message):
    global response_count, command_count

    if message.author == bot.user:  # Check if the message author is the bot itself
        return  # Ignore messages sent by the bot itself
    if check_chat(message) and ((not message.content.startswith("$")) or message.content.startswith("$imp")):  # Check if the message was sent in a channel where chat is allowed
        response_count += 1
        await send_response(message)
    if message.content.startswith("$"):
        command_count += 1
    await bot.process_commands(message)  # Ensure commands still work by processing them after handling the message

@bot.command(
    name="info"
)
async def info(ctx):
    uptime_seconds = time.time() - start_time
    uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))

    await ctx.send("Uptime: " + uptime_string + "\n\n" + "Commands executed (est.): " + str(command_count) + "\nImages Generated: " + str(images_count) + "\nMessages send by the chat module: " + str(response_count))

    image_info = []

    if ctx.message.channel.id in channels:
        image_info.append ("Image Generation is enabled in this channel")
    if ctx.message.channel.id in channels_to_not_scan:
         image_info.append ("Image Generation filters are disabled in this channel")

    await ctx.send("\n".join(image_info) + "\n\nModules:")

    external_modules = {
        "imagine (ComfyUI)": {"method": "GET", "url": "http://127.0.0.1:8188/system_stats"},
        "chat (oobabooga webui)": {"method": "GET", "url": "http://127.0.0.1:5000/v1/internal/model/info"}
    }

    for module_num, (module, config) in enumerate(external_modules.items(), start=1):
        method = config["method"]
        url = config["url"]

        # Perform the request
        try:
            # Perform the request
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url)
            else:
                raise ValueError("Unsupported HTTP method")

            # Check if the status code is 200
            ok = response.status_code == 200
            json_content = response.json() if ok else None
            status_code = response.status_code

        except requests.ConnectionError:
            # Handle the connection error gracefully
            print("The service is not available. Connection refused.")
            ok = False
            status_code, json_content = ("Connection Refused", "Connection Refused")


        if module_num==2:
            if ok:
                if json_content["model_name"] == "None":
                    content = f"**{module_num}: {module}: [--]** Service Running, but no Model is loaded ({json_content['model_name']})"
                else:
                    content = f"**{module_num}: {module}: [OK]** Loaded Model: {json_content['model_name']}"
            else:
                content = f"**{module_num}: {module}: [--]** Status Code {status_code}"
        else:
            content = f"**{module_num}: {module}: [{'OK' if ok else '--'}]** {json_content}"

        await ctx.send(content=content)

@bot.command(
    name="ping"
)
async def ping(ctx):
    await ctx.send(f"pong! (message received with {(datetime.datetime.now(datetime.timezone.utc) - ctx.message.created_at).total_seconds()}s delay)")


@bot.command(
    name='start_chat',
    description='starts a chat',
    pass_context=True, )
async def start_chat(ctx):
    await ctx.send("Chat started.")
    await asyncio.sleep(1)
    await add_channel(ctx.message.channel)


@bot.command(
    name='stop_chat',
    description='stops a chat',
    pass_context=True, )
async def start_chat(ctx):
    remove_channel(ctx.message.channel)
    await ctx.send ("Chat stopped.")

@bot.command(
    name='load',
    description='Downloads a mp3 file from deine röhre (übersetze auf englisch lol) lol',
    pass_context=True, )
async def load(ctx, link=None):
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
