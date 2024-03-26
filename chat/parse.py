from random import randint
import re

import aiohttp
import requests
from .FakeContext import Context

from bot_provider import get_bot
from chat.History_Service import append_to_history, get_history
from imagine import imagine

url = "http://127.0.0.1:5000/v1/completions"
"""
with open("openai.token") as f:
    for line in f.readlines():
        if line.startswith("#") or line.strip() == "":
            pass
        else:
            token = line.strip()
            break

headers = {
    "Content-Type": "application/json"
}
"""

async def post_data(url, headers, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data, ssl=False) as response:
            # Parse the response body as JSON
            return await response.json()


async def send_response(message):
    msg = await message.channel.send("[GENERATING...]")
    bot_response = await get_bot_response(message, message.author.name)

    pattern = r'\{(\w+):\s*(.*?)\}'

    # Find all matches of the pattern in the string
    matches = re.findall(pattern, bot_response)

    # Iterate over each match and replace it with the desired format
    output_string = bot_response
    for match in matches:
        variable_name = match[0]
        prompt = match[1]
        replacement = f"[Generating {variable_name}. Prompt: {prompt}]"
        output_string = output_string.replace(f"{{{variable_name}: {prompt}}}", replacement)

    await msg.delete()
    await message.channel.send(output_string)

    for match in matches:
        prompt = match[1]
        await imagine(Context(message), prompt)


def parse(text):
    # return content
    # """
    # Regular expression pattern to match Discord user IDs
    pattern = re.compile(r'<@(\d+)>')

    # Fetch the Discord usernames for each user ID
    def replace(match):
        user_id = int(match.group(1))
        user = get_bot().get_user(user_id)
        return f'@{user.name}' if user else f'<@{user_id}>'

    # Replace user IDs with usernames using the regex pattern
    replaced_text = pattern.sub(replace, text)
    return replaced_text
    # """


async def get_bot_response(message, username):
    with open("chat/base_prompt.txt") as f:
        base_prompt = f.read()
    username = f"@{username}"
    parsed_content = parse(message.content)
    data = {
        "prompt": base_prompt + "\n".join(get_history(message.channel)) + "\n",
        "max_tokens": 200,
        "temperature": 0.75,
        "top_p": 0.9,
        "seed": 5,
        "stop": "<",
    }

    if len(get_history(message.channel)):
        data["prompt"] = data["prompt"][:-1]

    user_input = f"\n<{username}> " + parsed_content + "\n<The Royal Lucy von Chronos>"
    if not parsed_content.startswith("$imp"):
        append_to_history(message.channel, f"<{username}> " + parsed_content)

    data["prompt"] += user_input

    assistant_message = ""
    if parsed_content.startswith("$imp"):
        assistant_message = parsed_content.replace("$imp ", "")

    while assistant_message.strip() == "":
        data["seed"] = randint(1, 2147483647)
        # response = requests.post(url, headers=headers, json=data, verify=False)
        response = await post_data(url, headers, data)
        print(response)

        assistant_message = response['choices'][0]['text']

    append_to_history(message.channel, "<The Royal Lucy von Chronos>" + assistant_message)
    return assistant_message


async def get_bot_response_openai(message, username):
    username = f"@{username}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}"}

    append_to_history(message.channel, {"role": "user:", "content": username + ": " + message.content})
    data = {
        'model': "gpt-3.5-turbo",
        "messages": get_history(message.channel)
    }

    response = requests.post(url, headers=headers, json=data, verify=False)
    assistant_message = response.json()['choices'][0]['message']['content']
    append_to_history(message.channel, {"role": "The Royal Lucy von Chronos", "content": assistant_message})
    return assistant_message
    # return f"Hello {username}."
