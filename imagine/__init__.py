import asyncio
import hashlib
import json
import os.path
import time
from asyncio import sleep
from random import randint

import discord

from .imagine import test, queue_prompt, check_image

id_to_prompt = {}


def file_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


async def imagine(ctx, prompt_user, negative_prompt, style, batch_count=1, scan_image=False):
    prompt = json.load(open(f'imagine/{style}.json'))

    # Insert Prompts
    for i, prompt_obj in prompt.items():
        if prompt_obj["_meta"]["title"] == "Prompt": # Positive Prompt
            prompt[i]["inputs"]["raw_text"] = prompt_user
        if prompt_obj["class_type"] == "RawText" and prompt_obj["inputs"]["raw_text"] == "": # Negative Prompt
            print("Negative Node:", i)
            prompt[i]["inputs"]["raw_text"] = negative_prompt
        if i == "25":
            print(prompt_obj)


    coroutines = [imagine_core(ctx, prompt, str(randint(1, 2147483647)), style, scan_image) for _ in range(batch_count)]
    await asyncio.gather(*coroutines)


async def imagine_core(ctx, prompt, queue_id, style, scan_image=False, sleeptime=0.1):
    # set the seed for our KSampler node
    try:
        prompt["3"]["inputs"]["seed"] = randint(1, 2147483647)
    except KeyError:
        pass
    for i, prompt_obj in prompt.items():
        if prompt_obj["class_type"] == "SaveImage":
            filename_prefix = prompt[i]["inputs"]["filename_prefix"]
            # Remove everything after the last "/", then append the queue_id
            prompt[i]["inputs"]["filename_prefix"] = filename_prefix[:filename_prefix.rfind("/")] + "/" + queue_id
            print(prompt[i]["inputs"]["filename_prefix"])

    for i, prompt_obj in prompt.items():
        if prompt_obj["_meta"]["title"] == "Prompt":
            textprompt = prompt[i]["inputs"]["raw_text"]
            print(prompt[i]["inputs"]["raw_text"])

    filename = f"imagine/outputs/{queue_id}_00001_.png"
    print(filename)

    if scan_image == True:
        try:
            if not check_image(filename, textprompt):
                await ctx.send(
                    "I won't imagine this. Skibbidy image (or rather skibbidy prompt) detected. Hans get se flammenwerfer!")
                os.remove(filename)
                return
        except UnboundLocalError:
            pass

    start_time = time.time()

    queue_prompt(prompt)

    while True:
        if os.path.isfile(filename):
            break
        else:
            await sleep(0.05)

    time.sleep(sleeptime)

    elapsed_time = time.time() - start_time

    print("Elapsed time:", elapsed_time, "seconds", filename)

    # ctx, prompt_user, style, scan_image = False
    id_to_prompt[queue_id] = {"ctx": ctx, "prompt": prompt, "scan_image": scan_image, "style": style}

    with open(filename, "rb") as f:
        try:
            await ctx.send(f'Generation Time: {elapsed_time} \nSeed: {prompt["3"]["inputs"]["seed"]}', file=discord.File(f, f"{queue_id}.png", spoiler=True),
                        reference=ctx.message, view=GeneratedOptions())
        except KeyError:
            await ctx.send(f'Generation Time: {elapsed_time}',
                           file=discord.File(f, f"{queue_id}.png", spoiler=True),
                           reference=ctx.message, view=GeneratedOptions())

    await sleep(60)

    del id_to_prompt[queue_id]
    os.remove(filename)


class GeneratedOptions(discord.ui.View):  # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Another image",
                       style=discord.ButtonStyle.primary)  # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, interaction, button):
        generate_id = interaction.message.attachments[0].filename.replace('SPOILER_', '').replace('.png', '')
        try:
            id_to_prompt[generate_id]["ctx"]
        except KeyError:
            await interaction.reply("Too much time has elapsed, the buttons don't work anymore...")

        await interaction.response.send_message(content="Generating...", ephemeral=True)

        queue_id = str(randint(1, 2147483647))
        prompt = id_to_prompt[generate_id]["prompt"]
        prompt["3"]["inputs"]["denoise"] = 1

        await interaction.response.defer()
        await imagine_core(id_to_prompt[generate_id]["ctx"], prompt, queue_id, id_to_prompt[generate_id]["style"],
                           id_to_prompt[generate_id]["scan_image"])

    @discord.ui.button(label="Other Variant of this image",
                       style=discord.ButtonStyle.primary)  # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback2(self, interaction, button):
        generate_id = interaction.message.attachments[0].filename.replace('SPOILER_', '').replace('.png', '')
        try:
            await id_to_prompt[generate_id]["ctx"]
        except KeyError:
            await interaction.reply("Too much time has elapsed, the buttons don't work anymore...")

        await interaction.response.send_message(content="Generating...", ephemeral=True)

        queue_id = str(randint(1, 2147483647))
        prompt = id_to_prompt[generate_id]["prompt"]
        prompt["3"]["inputs"]["denoise"] = 0.85
        for i, prompt_obj in prompt.items():
            if prompt_obj["class_type"] == "LoadImage":
                prompt_obj["inputs"]["image"] = "../output/imagine/" + generate_id + "_00001_.png"

        await interaction.response.defer()
        await imagine_core(id_to_prompt[generate_id]["ctx"], prompt, queue_id, id_to_prompt[generate_id]["style"],
                           id_to_prompt[generate_id]["scan_image"])

    @discord.ui.button(label="Upscale this image",
                       style=discord.ButtonStyle.primary)  # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback3(self, interaction, button):
        generate_id = interaction.message.attachments[0].filename.replace('SPOILER_', '').replace('.png', '')
        try:
            await id_to_prompt[generate_id]["ctx"]
        except KeyError:
            await interaction.reply("Too much time has elapsed, the buttons don't work anymore...")

        await interaction.response.send_message(content="Upscaling...", ephemeral=True)

        queue_id = str(randint(1, 2147483647))
        prompt = json.load(open(f'imagine/upscale.json'))
        for i, prompt_obj in prompt.items():
            if prompt_obj["class_type"] == "LoadImage":
                prompt_obj["inputs"]["image"] = "../output/imagine/" + generate_id + "_00001_.png"

        await interaction.response.defer()
        await imagine_core(id_to_prompt[generate_id]["ctx"], prompt, queue_id, id_to_prompt[generate_id]["style"],
                           id_to_prompt[generate_id]["scan_image"], 1.2)

