import os
from dotenv import load_dotenv
import discord

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LEO_ID = os.getenv("LEO_ID")

client = discord.Client(intents=discord.Intents.all())

custom_leo = discord.utils.get(client.emojis, name='leo1')
custom_scott = discord.utils.get(client.emojis, name='scottie')
custom_tsa = discord.utils.get(client.emojis, name='tsa')

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')    

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "leo" in message.content.lower() or message.author.id == LEO_ID:
        if custom_leo:
            await message.add_reaction(custom_leo)
        await message.channel.send(custom_leo)

    elif "scott" in message.content.lower():
        if custom_scott:
            await message.add_reaction(custom_scott)
        await message.channel.send(custom_scott)

    elif "tsa" in message.content.lower():
        if custom_tsa:
            await message.add_reaction(custom_tsa)
        await message.channel.send(custom_tsa)

    elif "shiv" in message.content.lower():
        await message.channel.send("@shiv")

    elif "game" in message.content.lower():
        await message.channel.send("You just lost the game")

    elif "consty" in message.content.lower() or "constable" in message.content.lower():
        await message.channel.send(file=discord.File('absolute_honors.png'))

client.run(DISCORD_TOKEN)