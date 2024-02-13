import discord

from bot_provider import get_bot


class Context:
    def __init__(self, message):
        self.message = message
        self.send = message.channel.send

    @classmethod
    async def get_ctx_message(cls, msg_id, channel_id):
        client = get_bot()
        try:
            # Fetching the channel by ID
            channel = client.get_channel(channel_id)
            if channel:
                # Fetching the message by its ID in the specified channel
                message = await channel.fetch_message(msg_id)
                return Context(message)
            else:
                print("Channel not found.")
        except discord.NotFound:
            print("Message not found.")
        except Exception as e:
            print("An error occurred:", e)
