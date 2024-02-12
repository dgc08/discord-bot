import asyncio

from . import add_channel, remove_channel
from .parse import get_bot_response

class Message:
    def __init__(self, content, channel):
        self.channel = channel
        self.content = content

class Channel:
    async def send(self, text):
        print(text)

def conv():
    asyncio.run(conversation())

async def conversation():
    channel = Channel()
    username = input("username>")

    await add_channel(channel)

    usr = ""
    while usr != "$exit":
        usr = input("@" + username + ">")
        if usr. startswith("@@"):
            msg_user = usr.split(" ")[0].replace("@@", "@")
            usr = usr.split(" ")[1]
        else:
            msg_user = username

        print(await get_bot_response(Message(usr, channel), msg_user))


    remove_channel("console")
