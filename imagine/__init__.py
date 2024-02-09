import hashlib
import json
import os.path
import time
from asyncio import sleep
from random import randint

import discord

from .imagine import test, queue_prompt, check_image

id_to_prompt= {}

def file_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
async def imagine(ctx, prompt_user, style, scan_image = False):
    prompt = json.load(open(f'imagine/{style}.json'))

    for i, prompt_obj in prompt.items():
        if prompt_obj["_meta"]["title"] == "Prompt":
            prompt[i]["inputs"]["raw_text"] = prompt_user
            break

    queue_id = str(randint(1, 2147483647))

    await imagine_core(ctx, prompt,queue_id, style,scan_image)

async def imagine_core(ctx, prompt,queue_id,style, scan_image = False):
    # set the seed for our KSampler node
    prompt["3"]["inputs"]["seed"] = randint(1, 2147483647)
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

    start_time = time.time()

    queue_prompt(prompt)

    filename = f"imagine/outputs/{queue_id}_00001_.png"
    print(filename)

    while True:
        if os.path.isfile(filename):
            break
        else:
            await sleep(0.05)

    time.sleep(0.1)

    elapsed_time = time.time() - start_time

    print("Elapsed time:", elapsed_time, "seconds", filename)

    if scan_image == True:
        if not check_image(filename, textprompt):
            await ctx.send("I won't imagine this. Skibbidy image (or rather skibbidy prompt) detected. Hans get se flammenwerfer!")
            os.remove(filename)
            return

    #ctx, prompt_user, style, scan_image = False
    id_to_prompt[queue_id] = {"ctx": ctx, "prompt":prompt, "scan_image":scan_image, "style":style}

    with open(filename, "rb") as f:
        await ctx.send(f"Generation Time: {elapsed_time}", file=discord.File(f, f"{queue_id}.png", spoiler=True), reference=ctx.message, view=GeneratedOptions())

    await sleep(60)

    del id_to_prompt[queue_id]
    os.remove(filename)

class GeneratedOptions(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Another image", style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback(self, interaction, button):
        try:
            generate_id = interaction.message.attachments[0].filename.replace('SPOILER_', '').replace('.png', '')
        except:
            interaction.reply("Too much time has elapsed, the buttons don't work anymore...")
            return

        queue_id = str(randint(1, 2147483647))
        prompt = id_to_prompt[generate_id]["prompt"]
        prompt["3"]["inputs"]["denoise"] = 1

        print("call")
        print(id_to_prompt[generate_id].keys())
        await imagine_core(id_to_prompt[generate_id]["ctx"], prompt, queue_id, id_to_prompt[generate_id]["style"], id_to_prompt[generate_id]["scan_image"])\

    @discord.ui.button(label="Other Variant of this image", style=discord.ButtonStyle.primary) # Create a button with the label "😎 Click me!" with color Blurple
    async def button_callback2(self, interaction, button):
        try:
            generate_id = interaction.message.attachments[0].filename.replace('SPOILER_', '').replace('.png', '')
        except:
            interaction.reply("Too much time has elapsed, the buttons don't work anymore...")
            return
        queue_id = str(randint(1, 2147483647))
        prompt = id_to_prompt[generate_id]["prompt"]
        prompt["3"]["inputs"]["denoise"] = 0.85
        for i, prompt_obj in prompt.items():
            if prompt_obj["class_type"] == "LoadImage":
                prompt_obj["inputs"]["image"] = "../output/imagine/" + generate_id + "_00001_.png"

        await imagine_core(id_to_prompt[generate_id]["ctx"], prompt, queue_id, id_to_prompt[generate_id]["style"], id_to_prompt[generate_id]["scan_image"])

