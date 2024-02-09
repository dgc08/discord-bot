import hashlib
import json
import os.path
import time
from random import randint

import discord

from .imagine import test, queue_prompt, check_image


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

    queue_id = str(randint(1, 2147483647))
    for i, prompt_obj in prompt.items():
        if prompt_obj["class_type"] == "SaveImage":
            prompt[i]["inputs"]["filename_prefix"] = prompt[i]["inputs"]["filename_prefix"] + queue_id

    print(prompt["20"]["inputs"]["raw_text"])

    # set the seed for our KSampler node
    prompt["3"]["inputs"]["seed"] = randint(1, 2147483647)

    start_time = time.time()

    queue_prompt(prompt)


    filename = f"imagine/outputs/{queue_id}_00001_.png"

    while True:
        if os.path.isfile(filename):
            break
        else:
            time.sleep(0.05)

    time.sleep(0.1)
    print(os.path.getsize(filename))

    elapsed_time = time.time() - start_time

    print("Elapsed time:", elapsed_time, "seconds", filename)

    if scan_image == True:
        if not check_image(filename, prompt_user):
            await ctx.send("No.")
            os.remove(filename)
            return

    with open(filename, "rb") as f:
        await ctx.message.reply(f"Generation Time: {elapsed_time}", file=discord.File(f, "imagine.png", spoiler=True))

    os.remove(filename)
